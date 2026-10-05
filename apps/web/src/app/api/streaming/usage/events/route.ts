import { streamProxy } from "@/lib/streaming-proxy";
import { eventBatchSchema } from "@/lib/streaming";
export async function POST(request: Request) { return streamProxy("/events", request, eventBatchSchema); }
