import { controlPlaneProxy } from "@/lib/control-plane-proxy";
import { deploymentReviewSchema } from "@/lib/deployment-review";
export function GET() { return controlPlaneProxy("/v1/infrastructure/deployment", deploymentReviewSchema); }
