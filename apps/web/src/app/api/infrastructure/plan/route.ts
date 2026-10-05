import { controlPlaneProxy } from "@/lib/control-plane-proxy";
import { infrastructurePlanSchema } from "@/lib/infrastructure-plan";
export function GET() { return controlPlaneProxy("/v1/infrastructure/plan", infrastructurePlanSchema); }
