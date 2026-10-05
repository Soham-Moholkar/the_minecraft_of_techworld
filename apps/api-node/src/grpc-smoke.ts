/** Exercise the real gRPC wire contract against a running ATLAS Node facade. */

import { fileURLToPath } from "node:url";
import * as grpc from "@grpc/grpc-js";
import * as protoLoader from "@grpc/proto-loader";

type ListResponse = { projects: Array<{ slug: string; name: string }> };
type ProjectClient = grpc.Client & {
  listProjects(
    request: { limit: number },
    metadata: grpc.Metadata,
    callback: (error: grpc.ServiceError | null, response: ListResponse) => void,
  ): grpc.ClientUnaryCall;
};

const protoPath = fileURLToPath(new URL("../contracts/projects.proto", import.meta.url));
const definition = protoLoader.loadSync(protoPath, { defaults: true, keepCase: false });
const descriptor = grpc.loadPackageDefinition(definition) as unknown as {
  atlas: { protocols: { Projects: grpc.ServiceClientConstructor } };
};
const address = process.env.ATLAS_NODE_GRPC_ADDRESS ?? "localhost:8101";
const client = new descriptor.atlas.protocols.Projects(
  address,
  grpc.credentials.createInsecure(),
) as unknown as ProjectClient;
const metadata = new grpc.Metadata();
metadata.set(
  "authorization",
  `Bearer ${process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token"}`,
);

await new Promise<void>((resolve, reject) => {
  client.listProjects({ limit: 10 }, metadata, (error, response) => {
    client.close();
    if (error) {
      reject(error);
      return;
    }
    console.log(JSON.stringify({ protocol: "grpc", projects: response.projects.length }));
    resolve();
  });
});
