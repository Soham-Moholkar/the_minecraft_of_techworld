"""Optional real Kafka transport for the trusted local streaming profile.

No topic creation or arbitrary broker input is exposed over HTTP. An operator
provisions one partition per tenant. Manual assignment keeps the first slice
small; this does NOT implement distributed consumer-group coordination.
"""

from __future__ import annotations

import time
from typing import Any

from atlas_api.streaming import PartitionRead, Record, StreamUnavailable, UsageEvent


class KafkaBroker:
    def __init__(self, bootstrap: str, tenant: str) -> None:
        # Lazy import means offline/core installations never need the native SDK.
        import confluent_kafka as kafka  # type: ignore[import-not-found,import-untyped]

        self.sdk: Any = kafka
        self.topic = f"atlas.usage.{tenant}"
        self.consumer = kafka.Consumer(
            {
                "bootstrap.servers": bootstrap,
                "group.id": f"atlas.usage.{tenant}.rollup",
                "enable.auto.commit": False,
                "enable.auto.offset.store": False,
                "allow.auto.create.topics": False,
                "auto.offset.reset": "error",
                "socket.timeout.ms": 3000,
                "session.timeout.ms": 6000,
                "fetch.message.max.bytes": 65536,
                "queued.max.messages.kbytes": 64,
                "log_level": 0,
            }
        )
        try:
            self.producer = kafka.Producer(
                {
                    "bootstrap.servers": bootstrap,
                    "enable.idempotence": True,
                    "message.timeout.ms": 3000,
                    "socket.timeout.ms": 3000,
                    "queue.buffering.max.messages": 100,
                    "message.max.bytes": 65536,
                    "log_level": 0,
                }
            )
        except Exception:
            self.consumer.close()
            raise

    def position(self) -> PartitionRead:
        part = self.sdk.TopicPartition(self.topic, 0)
        metadata = self.consumer.list_topics(self.topic, timeout=3)
        topic = metadata.topics.get(self.topic)
        if topic is None or topic.error or len(topic.partitions) != 1:
            raise StreamUnavailable()
        earliest, end = self.consumer.get_watermark_offsets(part, timeout=3, cached=False)
        committed = self.consumer.committed([part], timeout=3)[0]
        if committed.error:
            raise StreamUnavailable()
        # A new group may start at zero only if retention has not removed history.
        checkpoint = max(0, committed.offset)
        return PartitionRead(
            partition=0,
            earliest=earliest,
            end=end,
            checkpoint=checkpoint,
            lag=max(0, end - checkpoint),
            retention_gap=checkpoint < earliest or checkpoint > end,
        )

    def publish(self, events: list[UsageEvent]) -> None:
        self.position()  # Fail closed for missing/multi-partition topics.
        failures: list[object] = []

        def delivered(error: object, message: object) -> None:
            if error:
                failures.append(error)

        for event in events:
            self.producer.produce(
                self.topic,
                partition=0,
                key=event.event_id.encode(),
                value=event.model_dump_json().encode(),
                on_delivery=delivered,
            )
        remaining = self.producer.flush(4)
        if failures or remaining:
            # Some records may have arrived: retry the SAME IDs after a timeout.
            raise StreamUnavailable()

    def fetch(self, limit: int) -> list[Record]:
        position = self.position()
        if position.retention_gap:
            raise StreamUnavailable()
        self.consumer.assign([self.sdk.TopicPartition(self.topic, 0, position.checkpoint)])
        records: list[Record] = []
        deadline = time.monotonic() + 3
        while len(records) < limit and time.monotonic() < deadline:
            message = self.consumer.poll(min(0.2, max(0, deadline - time.monotonic())))
            if message is None:
                continue
            if message.error():
                raise StreamUnavailable()
            offset = message.offset()
            if offset is None or offset < 0:
                raise StreamUnavailable()
            records.append(Record(offset, message.value() or b""))
            if offset + 1 >= position.end:
                break
        return records

    def commit(self, next_offset: int) -> None:
        result = self.consumer.commit(
            offsets=[self.sdk.TopicPartition(self.topic, 0, next_offset)],
            asynchronous=False,
        )
        if result is None or any(part.error for part in result):
            raise StreamUnavailable()

    def close(self) -> None:
        self.consumer.close()
