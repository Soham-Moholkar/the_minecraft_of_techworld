import { controlPlaneProxy } from "@/lib/control-plane-proxy";
import { flinkSchema } from "@/lib/usage-flink";
export async function GET() { return controlPlaneProxy("/v1/pipelines/usage/flink", flinkSchema); }
