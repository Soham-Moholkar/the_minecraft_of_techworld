import { memoryProxy } from "@/lib/agent-memory-proxy";
import { memoryPurgeSchema, memoryRemovalSchema } from "@/lib/agent-memory";

export async function POST(request: Request) {
  return memoryProxy("/purge-expired", memoryRemovalSchema, request, memoryPurgeSchema);
}
