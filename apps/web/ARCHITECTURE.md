# Web architecture

- Server Components render durable shell and registry views.
- Client Components are limited to stateful operational views.
- Same-origin route handlers isolate API credentials and failure timeouts.
- The event-stream route keeps credentials server-side while forwarding SSE without
  buffering; EventSource owns browser reconnect behavior.
- Repository AI uses a same-origin streamed POST because its bounded structured
  request does not fit EventSource's GET-only contract. The browser treats deltas
  as transient progress and renders only the final schema-validated result.
- Owned shadcn-style primitives live in `src/components/ui`; application
  compositions live one layer above them.
- The shell remains usable when an optional backend is degraded and shows an
  explicit dependency error instead of substituting fake authoritative data.
