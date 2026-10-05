# Agent boundary regression exercise

Run with the repository virtual environment: `python labs/security/agent-boundaries/run.py verify`.
The start/test/reset lifecycle owns only `.lab-state/memory.db` and `state.json`.

A synthetic instruction is persisted through the actual memory service. It stays
untrusted and outside automatic inference context. The exercise verifies tenant
isolation, expiry and content-free audit records; rejects credentials and approval
material; rejects patch approval reuse as test approval and a wrong execution
digest; and denies a direct submitted-to-applied workflow shortcut. A correct
separate execution approval queues an in-memory record without applying a patch.

The assertions call production policy code. No model, worker, external target or
network is involved. API endpoint and container isolation tests remain additional
gates. Changing the service boundaries must preserve these security assertions.
