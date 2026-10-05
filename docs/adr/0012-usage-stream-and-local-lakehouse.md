# ADR 0012: bounded usage streaming and local Iceberg projection

Status: accepted for trusted local development, 2026-10-03.

The Phase 10 lab proves local recovery but does not provide product ingestion or
broker interchangeability. `/streaming` now operates an authenticated usage API
through a server-only BFF. Request inputs contain bounded event IDs/counters or
batch size; paths, tenant, topic, consumer and connection settings are operator-owned.

`Broker` separates publish/fetch/ack/position/close. SQLite is the default durable
source. Optional Kafka is an actual SDK adapter using tenant-specific topics and
group offsets, one manually assigned partition, disabled automatic commits and
disabled automatic topic creation. Group balancing and multi-partition processing
remain future work. A retention gap fails closed; it never resets automatically.

SQLite persists event-ID effects and content-free quarantine before acknowledgement.
An acknowledgement failure causes replay; deduplication prevents counting twice.
Producer delivery may be partial on failure: retry the same IDs. There is no shared
transaction between sink and broker, and no distributed exactly-once claim.
Local source/effects/quarantine storage is capped at 10,000 records per tenant/provider.
SQLite serializes writers; this is not the production multi-worker sink.

Accepted rows export through Arrow to Parquet with schema and embedded lineage.
Export is a consistent sink read, not a transactional broker cutoff. No arbitrary
files, uploads, SQL or storage URLs are exposed. An independent opt-in publishes
that accepted read into a local Iceberg SQL catalog. Full overwrites preserve
snapshot history and skip identical content. Reserve two snapshot slots for
overwrite's delete/append behavior, with a maximum of 32. JavaScript receives
snapshot identities as strings. Catalog conflicts fail rather than retrying stale
source images. Failed writes can leave orphan files; cleanup/expiration, remote
catalogs, schema evolution and concurrent distributed processing remain pending.

API/UI tests exercise real SQLite, Arrow and Iceberg. Kafka SDK boundary tests
are offline tests, not certification of a live broker. The Kafka Compose profile
uses a pinned Apache image, bounded resources and loopback host publishing.
PLAINTEXT is for this isolated local exercise only. Shared deployment requires
production identities, TLS/SASL, topic/group ACLs, quotas, durable storage, tracing
and operational retention/recovery. Existing local dev identity fails closed when
`ATLAS_ENVIRONMENT` differs from `development`.

No existing product database migration or reset is performed. The new standalone
stream store creates its own tables idempotently. Core installs remain lightweight;
streaming and lakehouse extras are optional and pinned.

Dependency review: Apache Kafka 4.3.1, confluent-kafka 2.15.1, PyArrow 25.0.1,
PyIceberg 0.12.0. Official releases, API documentation, licenses and security
policies reviewed; no external source copied. SDK native wheels and dependencies
retain their upstream licenses. Review is not a claim of a vulnerability-free SBOM.

`local_iceberg_io.py` owns a narrow FileIO compatibility adapter: decode canonical
local URIs, preserve Windows drives/spaces and use extended native paths for long
manifest filenames. Remote schemes/authorities are rejected. The smoke verifier
executes actual local runtimes and validates generated-path containment before
cleanup. `verify_kafka.py` is a separate live gate using only unique owned topics.

Sources:
- https://kafka.apache.org/community/downloads/
- https://kafka.apache.org/community/cve-list/
- https://docs.confluent.io/kafka-clients/python/current/overview.html
- https://github.com/confluentinc/confluent-kafka-python/releases
- https://github.com/confluentinc/confluent-kafka-python/blob/master/LICENSE
- https://arrow.apache.org/install/
- https://arrow.apache.org/docs/python/parquet.html
- https://arrow.apache.org/security/
- https://github.com/apache/arrow/blob/main/LICENSE.txt
- https://py.iceberg.apache.org/
- https://py.iceberg.apache.org/api/
- https://github.com/apache/iceberg-python/releases
- https://github.com/apache/iceberg-python/blob/main/LICENSE
- https://iceberg.apache.org/security/
