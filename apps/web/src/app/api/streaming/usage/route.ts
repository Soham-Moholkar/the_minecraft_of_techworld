import { streamProxy } from "@/lib/streaming-proxy";
export async function GET() { return streamProxy(""); }
