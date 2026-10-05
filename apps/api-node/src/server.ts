import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { fileURLToPath } from "node:url";
import * as grpc from "@grpc/grpc-js";
import * as protoLoader from "@grpc/proto-loader";
import {
  HttpProjectProvider,
  authenticated,
  boundedLimit,
  executeProjectGraphQL,
  type ProjectProvider,
} from "./protocols.js";

const token = process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token";
const provider = new HttpProjectProvider(
  process.env.ATLAS_API_URL ?? "http://localhost:8000",
  token,
);
const httpPort = Number(process.env.ATLAS_NODE_HTTP_PORT ?? 8100);
const grpcPort = Number(process.env.ATLAS_NODE_GRPC_PORT ?? 8101);

function json(response: ServerResponse, status: number, body: unknown): void {
  response.writeHead(status, {
    "Content-Type": "application/json",
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
  });
  response.end(JSON.stringify(body));
}

async function readBody(request: IncomingMessage): Promise<unknown> {
  const chunks: Buffer[] = [];
  let size = 0;
  for await (const chunk of request) {
    const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
    size += buffer.length;
    if (size > 65_536) throw new RangeError("request body too large");
    chunks.push(buffer);
  }
  return JSON.parse(Buffer.concat(chunks).toString("utf8")) as unknown;
}

const httpServer = createServer(async (request, response) => {
  const started = performance.now();
  try {
    const url = new URL(request.url ?? "/", `http://${request.headers.host ?? "localhost"}`);
    if (request.method === "GET" && url.pathname === "/health") {
      json(response, 200, { status: "ok", service: "atlas-api-node" });
      return;
    }
    if (!authenticated(request.headers.authorization, token)) {
      json(response, 401, { detail: "invalid credentials" });
      return;
    }
    if (request.method === "GET" && url.pathname === "/v1/projects") {
      json(response, 200, { projects: await provider.list(boundedLimit(url.searchParams.get("limit"))) });
      return;
    }
    if (request.method === "POST" && url.pathname === "/graphql") {
      const body = await readBody(request);
      if (!body || typeof body !== "object" || typeof (body as { query?: unknown }).query !== "string") {
        json(response, 400, { detail: "GraphQL query is required" });
        return;
      }
      const input = body as { query: string; variables?: Record<string, unknown> };
      json(response, 200, await executeProjectGraphQL(provider, input.query, input.variables));
      return;
    }
    json(response, 404, { detail: "route not found" });
  } catch (error) {
    const detail = error instanceof RangeError ? error.message : "protocol request failed";
    json(response, error instanceof RangeError ? 400 : 502, { detail });
  } finally {
    console.log(JSON.stringify({
      event: "node_http_request",
      method: request.method,
      route: request.url,
      status: response.statusCode,
      duration_ms: Math.round((performance.now() - started) * 100) / 100,
    }));
  }
});

type ListRequest = { limit?: number };
type GrpcProject = {
  id: string; slug: string; name: string; description: string; status: string; createdAt: string;
};
type ListResponse = { projects: GrpcProject[] };

export function createGrpcListHandler(projects: ProjectProvider, expectedToken: string) {
  return async (
    call: grpc.ServerUnaryCall<ListRequest, ListResponse>,
    callback: grpc.sendUnaryData<ListResponse>,
  ): Promise<void> => {
    const authorization = call.metadata.get("authorization")[0];
    if (!authenticated(typeof authorization === "string" ? authorization : undefined, expectedToken)) {
      callback({ code: grpc.status.UNAUTHENTICATED, message: "invalid credentials" });
      return;
    }
    try {
      callback(null, { projects: await projects.list(boundedLimit(call.request.limit)) });
    } catch (error) {
      callback({
        code: error instanceof RangeError ? grpc.status.INVALID_ARGUMENT : grpc.status.UNAVAILABLE,
        message: error instanceof Error ? error.message : "protocol request failed",
      });
    }
  };
}

const protoPath = fileURLToPath(new URL("../contracts/projects.proto", import.meta.url));
const definition = protoLoader.loadSync(protoPath, {
  defaults: true,
  keepCase: false,
  longs: String,
});
const descriptor = grpc.loadPackageDefinition(definition) as unknown as {
  atlas: { protocols: { Projects: grpc.ServiceClientConstructor } };
};
const grpcServer = new grpc.Server();
grpcServer.addService(descriptor.atlas.protocols.Projects.service, {
  listProjects: createGrpcListHandler(provider, token),
});

httpServer.listen(httpPort, "0.0.0.0", () => {
  console.log(JSON.stringify({ event: "node_http_started", port: httpPort }));
});
grpcServer.bindAsync(`0.0.0.0:${grpcPort}`, grpc.ServerCredentials.createInsecure(), (error) => {
  if (error) throw error;
  console.log(JSON.stringify({ event: "node_grpc_started", port: grpcPort }));
});
