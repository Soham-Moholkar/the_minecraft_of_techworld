import { memoryProxy } from "@/lib/agent-memory-proxy";
import { memoryCreateSchema, memoryReadSchema, memorySnapshotSchema } from "@/lib/agent-memory";

export async function GET() {
  return memoryProxy("", memorySnapshotSchema);
}

export async function POST(request: Request) {
  return memoryProxy("", memoryReadSchema, request, memoryCreateSchema);
}
