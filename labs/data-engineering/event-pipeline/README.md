# Durable usage-event pipeline

Run from the repository root with the repository Python environment:

```powershell
.\.venv\Scripts\python labs/data-engineering/event-pipeline/run.py start
.\.venv\Scripts\python labs/data-engineering/event-pipeline/run.py test
.\.venv\Scripts\python labs/data-engineering/event-pipeline/run.py reset
```

`verify` runs all three, cleaning up even after a failed test. Start recreates a
disposable database and numeric evidence under this lab's `.lab-state` directory.
No application database is touched. The website catalog at
`/labs/durable-event-pipeline` exposes commands and source location; its lifecycle
buttons record operator state and do not execute commands or certify tests.

The pipeline aggregates synthetic tenant usage. A bounded source admits negative
counters for a quality rejection scenario. Processing commits aggregate effects,
quarantine reasons and consumer checkpoints together. A pre-commit fault rolls
back all three. A fresh process resumes committed offsets. Duplicate source IDs
are idempotent only when their counters agree; conflicting retries fail closed.

Evidence contains per-batch accepted/rejected counts, source offset, checkpoint,
lag, sink totals and a crash rollback comparison. With batch size two, the first
batch leaves lag one; recovery reaches lag zero and total ten; replay adds zero.
Another tenant remains unconsumed. These are measured local values, not external
broker metrics or throughput benchmark claims.

Safety boundary: offline single-machine execution, parameterized SQL, bounded
identifiers/counters/batches, fixed reset filenames and synthetic counters only.
The caller supplies tenant scope; this local library is not a public authenticated
API. There is no arbitrary payload, network access, shell input, tool execution,
credential ingestion or automatic worker. Retained event history is tiny here;
production ingestion requires quota, retention and admission controls.

Change `pipeline.py` in the IDE to study transaction boundaries. Run the recovery,
isolation, duplicate, quality and validation regression tests before trusting a
change. See `docs/evolution/data-engineering.md` for progression and next steps.
