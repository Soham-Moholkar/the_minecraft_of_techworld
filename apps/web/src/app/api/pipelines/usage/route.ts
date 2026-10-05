import { controlPlaneProxy } from "@/lib/control-plane-proxy";
import { dagSchema } from "@/lib/usage-dag";
export async function GET() { return controlPlaneProxy("/v1/pipelines/usage", dagSchema); }
