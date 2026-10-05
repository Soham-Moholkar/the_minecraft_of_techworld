"""Offline SDK boundary contracts; these do not certify a live Kafka broker."""

from types import SimpleNamespace

import pytest

from atlas_api.kafka_broker import KafkaBroker
from atlas_api.streaming import StreamUnavailable, UsageEvent


class Consumer:
    def __init__(self, config: dict[str, object]) -> None:
        self.config = config
        self.earliest = 0
        self.end = 1
        self.offset = -1001
        self.assignment: object = None
        self.closed = False
        self.polls = 0

    def list_topics(self, topic: str, timeout: float) -> object:
        return SimpleNamespace(topics={topic: SimpleNamespace(error=None, partitions={0: None})})

    def get_watermark_offsets(self, part: object, timeout: float, cached: bool) -> tuple[int, int]:
        return self.earliest, self.end

    def committed(self, parts: list[object], timeout: float) -> list[object]:
        return [SimpleNamespace(offset=self.offset, error=None)]

    def assign(self, parts: object) -> None:
        self.assignment = parts

    def poll(self, timeout: float) -> object:
        self.polls += 1
        return SimpleNamespace(
            error=lambda: None, offset=lambda: 0, value=lambda: b'{"event_id":"one","units":4}'
        )

    def commit(self, offsets: list[object], asynchronous: bool) -> list[object]:
        assert asynchronous is False
        self.offset = offsets[0].offset
        return [SimpleNamespace(error=None)]

    def close(self) -> None:
        self.closed = True


class Producer:
    def __init__(self, config: dict[str, object]) -> None:
        self.config = config
        self.events: list[object] = []

    def produce(self, topic: str, **kwargs: object) -> None:
        self.events.append((topic, kwargs))

    def flush(self, timeout: float) -> int:
        return 0


@pytest.fixture
def broker(monkeypatch: pytest.MonkeyPatch) -> KafkaBroker:
    confluent_kafka = pytest.importorskip("confluent_kafka")

    monkeypatch.setattr(confluent_kafka, "Consumer", Consumer)
    monkeypatch.setattr(confluent_kafka, "Producer", Producer)
    return KafkaBroker("127.0.0.1:59092", "northstar")


def test_manual_commit_tenant_topic_and_disabled_autocommit(broker: KafkaBroker) -> None:
    assert broker.consumer.config["enable.auto.commit"] is False
    assert broker.consumer.config["enable.auto.offset.store"] is False
    broker.publish([UsageEvent(event_id="one", units=4)])
    assert broker.producer.events[0][0] == "atlas.usage.northstar"
    records = broker.fetch(1)
    assert len(records) == 1
    assert broker.position().checkpoint == 0  # Fetch alone never acknowledges.
    broker.commit(records[-1].offset + 1)
    assert broker.position().checkpoint == 1
    broker.close()
    assert broker.consumer.closed


def test_retention_gap_fails_closed_without_poll(broker: KafkaBroker) -> None:
    broker.consumer.earliest = 1
    assert broker.position().retention_gap
    with pytest.raises(StreamUnavailable):
        broker.fetch(10)
    assert broker.consumer.polls == 0


def test_partial_produce_timeout_reports_uncertain_delivery(broker: KafkaBroker) -> None:
    broker.producer.flush = lambda timeout: 1
    with pytest.raises(StreamUnavailable):
        broker.publish([UsageEvent(event_id="one", units=4)])
