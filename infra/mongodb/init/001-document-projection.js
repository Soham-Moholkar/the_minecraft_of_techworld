// Product and lab users are isolated at the database boundary. Neither receives
// admin/cluster roles, and the product user cannot access the lab database.
const product = db.getSiblingDB("atlas_document");
product.createUser({
  user: "atlas_projection",
  pwd: "atlas_projection_dev_only",
  roles: [{ role: "readWrite", db: "atlas_document" }],
});

product.createCollection("project_snapshots", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["organization_slug", "generation", "project_id", "project_slug", "name", "status", "note_count", "created_at", "published_at"],
      properties: {
        organization_slug: { bsonType: "string", maxLength: 64 },
        generation: { bsonType: "string", minLength: 32, maxLength: 32 },
        project_id: { bsonType: "string", maxLength: 64 },
        project_slug: { bsonType: "string", maxLength: 64 },
        name: { bsonType: "string", maxLength: 160 },
        status: { bsonType: "string", maxLength: 24 },
        note_count: { bsonType: "int", minimum: 0 },
        created_at: { bsonType: "date" },
        published_at: { bsonType: "date" },
      },
    },
  },
  validationAction: "error",
});
product.project_snapshots.createIndex(
  { organization_slug: 1, generation: 1, project_id: 1 },
  { name: "uq_tenant_generation_project", unique: true },
);
product.project_snapshots.createIndex(
  { organization_slug: 1, generation: 1, created_at: -1 },
  { name: "ix_tenant_generation_created" },
);

product.createCollection("projection_state", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["organization_slug", "generation", "published_at", "document_count"],
      properties: {
        organization_slug: { bsonType: "string", maxLength: 64 },
        generation: { bsonType: "string", minLength: 32, maxLength: 32 },
        published_at: { bsonType: "date" },
        document_count: { bsonType: "int", minimum: 0 },
      },
    },
  },
  validationAction: "error",
});
product.projection_state.createIndex(
  { organization_slug: 1 },
  { name: "uq_projection_state_tenant", unique: true },
);

const lab = db.getSiblingDB("atlas_document_lab");
lab.createUser({
  user: "atlas_document_lab",
  pwd: "atlas_document_lab_dev_only",
  roles: [{ role: "readWrite", db: "atlas_document_lab" }],
});
