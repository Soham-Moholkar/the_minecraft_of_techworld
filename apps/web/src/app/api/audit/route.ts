import { controlPlaneProxy } from "@/lib/control-plane-proxy";
import { auditSchema } from "@/lib/control-plane";
export async function GET() { return controlPlaneProxy("/v1/audit", auditSchema); }
