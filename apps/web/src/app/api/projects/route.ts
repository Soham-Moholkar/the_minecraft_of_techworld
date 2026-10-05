import { controlPlaneProxy } from "@/lib/control-plane-proxy";
import { projectInput, projectPageSchema, projectSchema } from "@/lib/control-plane";
export async function GET() { return controlPlaneProxy("/v1/projects", projectPageSchema); }
export async function POST(request: Request) { return controlPlaneProxy("/v1/projects", projectSchema, request, projectInput); }
