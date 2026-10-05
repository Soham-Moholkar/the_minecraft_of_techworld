/** Synthetic operator note for tests; never production seed data. */
export const memoryFixture = {
  id: "550e8400-e29b-41d4-a716-446655440000", title: "Worker observation",
  content: "The reviewed worker needs Docker to execute tests.", provenance: "Local operator review",
  created_by: "local-developer", created_at: "2026-10-01T10:00:00Z", expires_at: "2099-10-08T10:00:00Z",
};
export const memorySnapshotFixture = {
  items: [memoryFixture], expired_count: 0, capacity: 50,
  mode: "operator-managed", automatic_context: false,
};
export const memoryInputFixture = {
  title: memoryFixture.title, content: memoryFixture.content, provenance: memoryFixture.provenance,
  retention_days: 7, confirmation: "NO SECRETS OR APPROVALS",
};
