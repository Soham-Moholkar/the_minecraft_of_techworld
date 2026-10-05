import { controlPlaneProxy } from "@/lib/control-plane-proxy";
import { biSchema } from "@/lib/usage-bi";
export async function GET() { return controlPlaneProxy("/v1/pipelines/usage/bi", biSchema); }
