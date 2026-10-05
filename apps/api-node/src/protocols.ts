/** Shared project contract executed through REST, GraphQL, and gRPC transports. */

import { timingSafeEqual } from "node:crypto";
import { buildSchema, graphql, type ExecutionResult } from "graphql";

export type ProjectSummary = {
  id: string;
  slug: string;
  name: string;
  description: string;
  status: string;
  createdAt: string;
};

export interface ProjectProvider {
  list(limit: number): Promise<ProjectSummary[]>;
}

export function authenticated(authorization: string | undefined, expectedToken: string): boolean {
  const provided = authorization?.startsWith("Bearer ") ? authorization.slice(7) : "";
  const left = Buffer.from(provided);
  const right = Buffer.from(expectedToken);
  // timingSafeEqual rejects different lengths, so check length without ever falling
  // back to a normal secret comparison for equal-sized candidate tokens.
  return left.length === right.length && timingSafeEqual(left, right);
}

export function boundedLimit(value: unknown): number {
  const parsed = typeof value === "number" ? value : Number(value ?? 25);
  if (!Number.isInteger(parsed) || parsed < 1 || parsed > 100) {
    throw new RangeError("limit must be an integer from 1 to 100");
  }
  return parsed;
}

export const projectSchema = buildSchema(`
  type ProjectSummary {
    id: ID!
    slug: String!
    name: String!
    description: String!
    status: String!
    createdAt: String!
  }

  type Query {
    projects(limit: Int = 25): [ProjectSummary!]!
  }
`);

export async function executeProjectGraphQL(
  provider: ProjectProvider,
  source: string,
  variables: Record<string, unknown> | undefined,
): Promise<ExecutionResult> {
  return graphql({
    schema: projectSchema,
    source,
    variableValues: variables,
    rootValue: {
      projects: ({ limit }: { limit?: number }) => provider.list(boundedLimit(limit)),
    },
  });
}

type UpstreamPage = { items?: unknown };

export class HttpProjectProvider implements ProjectProvider {
  constructor(
    private readonly baseUrl: string,
    private readonly token: string,
  ) {}

  async list(limit: number): Promise<ProjectSummary[]> {
    const response = await fetch(`${this.baseUrl}/v1/projects?limit=${boundedLimit(limit)}`, {
      headers: { Authorization: `Bearer ${this.token}` },
      signal: AbortSignal.timeout(3000),
    });
    if (!response.ok) throw new Error(`project upstream returned ${response.status}`);
    const body = (await response.json()) as UpstreamPage;
    if (!Array.isArray(body.items)) throw new Error("project upstream returned an invalid page");
    return body.items.map(parseProject);
  }
}

function parseProject(value: unknown): ProjectSummary {
  if (!value || typeof value !== "object") throw new Error("invalid project item");
  const item = value as Record<string, unknown>;
  const required = ["id", "slug", "name", "description", "status", "created_at"] as const;
  if (required.some((field) => typeof item[field] !== "string")) {
    throw new Error("invalid project item fields");
  }
  return {
    id: item.id as string,
    slug: item.slug as string,
    name: item.name as string,
    description: item.description as string,
    status: item.status as string,
    createdAt: item.created_at as string,
  };
}
