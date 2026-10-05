import { controlPlaneProxy } from "@/lib/control-plane-proxy";
import { computeSchema } from "@/lib/usage-compute";
export async function GET() { return controlPlaneProxy("/v1/pipelines/usage/compute", computeSchema); }
