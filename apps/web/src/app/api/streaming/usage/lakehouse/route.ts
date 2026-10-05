import { z } from "zod";
import { streamProxy } from "@/lib/streaming-proxy";
import { lakehouseSchema } from "@/lib/streaming";
export async function POST(request: Request) {
  return streamProxy("/lakehouse", request, z.object({}).strict(), lakehouseSchema);
}
