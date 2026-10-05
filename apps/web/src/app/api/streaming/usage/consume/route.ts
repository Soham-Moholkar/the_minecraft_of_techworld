import { streamProxy } from "@/lib/streaming-proxy";
import { consumeSchema } from "@/lib/streaming";
export async function POST(request: Request) { return streamProxy("/consume", request, consumeSchema); }
