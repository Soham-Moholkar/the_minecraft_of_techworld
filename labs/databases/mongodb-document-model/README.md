# MongoDB document model, index, and atomic update lab

This disposable lab uses ATLAS's optional pinned MongoDB 8.0 service. It creates
an embedded order document model, then proves three behaviors against real
connections:

- a tenant/status/date compound index changes the winning query plan without
  changing results;
- collection JSON Schema validation rejects a malformed order with code `121`;
- a single-document version predicate prevents a stale inventory update, after
  which a fresh-read retry preserves the quantity invariant.

## Run the lifecycle

From the repository root, with Docker Desktop's Linux engine running:

```powershell
.\.venv\Scripts\python labs\databases\mongodb-document-model\run.py start
.\.venv\Scripts\python labs\databases\mongodb-document-model\run.py test
.\.venv\Scripts\python labs\databases\mongodb-document-model\run.py reset
```

Use `run.py verify` to start, test, and guarantee cleanup as one operation. The
`start` command writes sanitized evidence to
`.lab-state/mongodb-document-model-evidence.json`; it contains plan stage names,
counts, validation codes, and inventory versions, never a connection string,
credential, query document, tenant value, or raw driver error.

The lifecycle connects only as the non-root `atlas_document_lab` user and refuses
any database except `atlas_document_lab`. Reset removes only the fixed `atlas_orders`
and `atlas_inventory` collections plus allowlisted generated evidence.

## Exercise the product projection

Start the optional service together with the product:

```powershell
docker compose --profile database up -d --build mongodb api web
```

Open `http://localhost:3000/data`, find **MongoDB project projection**, and choose
**Publish projection**. PostgreSQL remains authoritative. ATLAS writes a complete
new generation, atomically switches the tenant's projection pointer, then removes
older generations, so a reader never selects a partially written refresh.

MongoDB server releases use the Server Side Public License (SSPL). Review that
license and your organization's deployment policy before using this optional
provider outside the local learning environment.
