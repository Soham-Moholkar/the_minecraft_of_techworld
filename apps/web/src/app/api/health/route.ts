import { controlPlaneProxy } from "@/lib/control-plane-proxy";
import { healthSchema } from "@/lib/control-plane";
export async function GET() { return controlPlaneProxy("/health", healthSchema); }
