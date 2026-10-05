# Full-stack event delivery evolution

- L0: authenticated REST mutations create durable audit records.
- L1: FastAPI encodes tenant-scoped records as SSE; Next.js streams them through a
  credential-isolating BFF; React EventSource renders and reconnects.
- L2 active: browsers resume with `Last-Event-ID`; the BFF forwards the cursor,
  tenant-aware repository ordering prevents replay, and unknown/cross-tenant cursors
  share one non-disclosing response. Reconnect delay is declared in the SSE stream.
- L2 next: backpressure limits, connection metrics, and database notification/broker
  adapters.
- L3 active: WebSocket presence uses short-lived one-use tickets, exact origin
  validation, connection/message limits, typed envelopes, metrics, and structured
  lifecycle logs. The Node facade exposes one project provider through REST,
  GraphQL, and gRPC for contract comparison.
- L3 next: event contracts, idempotent consumers, GraphQL subscriptions,
  trace propagation, and measured protocol load/failure comparisons.
