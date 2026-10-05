# Database security boundaries

This offline, process-only exercise demonstrates a SQL-injection tenant escape and then verifies the defensive replacement: bound parameters, an authoritative tenant predicate, a read-only authorizer, and redacted audit evidence. The vulnerable function exists only in this disposable SQLite lab and does not expose a listener.

```powershell
.\.venv\Scripts\python labs\security\database-boundaries\run.py verify
```

Use `start` to retain the local evidence, inspect `.lab-state/evidence.json`, and run `reset` when finished. Do not copy `intentionally_vulnerable_search` into application code.
