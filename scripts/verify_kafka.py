"""Live isolated Kafka acceptance; creates/deletes ONLY a unique test-owned topic.

No existing topic, group, database or platform volume is reset. Requires the
optional Kafka runtime and operator-configured broker. A failure is never a skip.
"""

import json
from pathlib import Path
from uuid import uuid4

from atlas_api.config import get_settings
from atlas_api.kafka_broker import KafkaBroker
from atlas_api.streaming import UsageEvent, UsageStream


def verify() -> None:
    from confluent_kafka.admin import AdminClient, NewTopic

    tenant = f"verify-{uuid4().hex}"
    topic = f"atlas.usage.{tenant}"
    bootstrap = get_settings().kafka_bootstrap
    admin = AdminClient(
        {"bootstrap.servers": bootstrap, "socket.timeout.ms": 3000, "log_level": 0}
    )
    path = Path("output") / f"kafka-{uuid4().hex}.db"
    created = False
    sink: UsageStream | None = None
    broker: KafkaBroker | None = None
    try:
        future = admin.create_topics(
            [
                NewTopic(
                    topic,
                    num_partitions=1,
                    replication_factor=1,
                    config={"retention.ms": "3600000"},
                )
            ],
            request_timeout=10,
        )[topic]
        future.result(timeout=15)
        created = True  # Never delete a topic whose creation did not succeed.
        sink = UsageStream(path, tenant, "kafka")
        broker = KafkaBroker(bootstrap, tenant)
        broker.publish(
            [UsageEvent(event_id="one", units=4), UsageEvent(event_id="bad", units=-1)]
        )
        broker.publish([UsageEvent(event_id="one", units=4)])
        records = broker.fetch(10)
        if len(records) != 3:
            raise RuntimeError("live broker did not return the expected bounded batch")
        sink.apply(
            records
        )  # Simulated crash after sink commit, before broker acknowledgement.
        broker.close()
        broker = KafkaBroker(bootstrap, tenant)
        result = sink.consume(broker, 10)
        if (
            result.units,
            result.accepted,
            result.quarantined,
            result.partitions[0].lag,
        ) != (4, 1, 1, 0):
            raise RuntimeError("live replay/checkpoint acceptance failed")
        print(
            json.dumps(
                {
                    "event": "kafka_live_verified",
                    "replayed": len(records),
                    "units": result.units,
                    "quarantined": result.quarantined,
                    "lag": result.partitions[0].lag,
                }
            )
        )
    finally:
        if broker:
            broker.close()
        if sink:
            sink.close()
        path.unlink(missing_ok=True)
        if created:
            try:
                admin.delete_consumer_groups(
                    [f"atlas.usage.{tenant}.rollup"], request_timeout=10
                )[f"atlas.usage.{tenant}.rollup"].result(timeout=15)
            finally:
                # A missing group after early failure must not strand the
                # uniquely owned topic; cleanup failures still fail the gate.
                admin.delete_topics([topic], request_timeout=10)[topic].result(timeout=15)


if __name__ == "__main__":
    verify()
