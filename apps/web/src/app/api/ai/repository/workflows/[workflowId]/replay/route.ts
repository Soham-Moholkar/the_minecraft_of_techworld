import { NextResponse } from "next/server";
import { z } from "zod";
import { repositoryWorkflowReplaySchema } from "@/lib/repository-ai";

const apiUrl = process.env.ATLAS_API_URL ?? "http://localhost:8000";
const headers = { "Cache-Control": "no-store" };
const uuidSchema = z.string().uuid();

/** Read-only BFF: the bearer token stays on the server and replay cannot mutate. */
export async function GET(
  _request: Request,
  { params }: { params: Promise<{ workflowId: string }> },
) {
  const { workflowId } = await params;
  if (!uuidSchema.safeParse(workflowId).success) {
    return NextResponse.json({ detail: "invalid workflow id" }, { status: 400, headers });
  }
  try {
    const response = await fetch(`${apiUrl}/v1/ai/repository/workflows/${workflowId}/replay`, {
      cache: "no-store",
      headers: { Authorization: `Bearer ${process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token"}` },
      signal: AbortSignal.timeout(10_000),
    });
    const payload: unknown = await response.json();
    if (!response.ok) {
      return NextResponse.json(
        { detail: response.status === 409 ? "Workflow history failed policy validation." : "Workflow replay unavailable." },
        { status: response.status, headers },
      );
    }
    const parsed = repositoryWorkflowReplaySchema.safeParse(payload);
    if (!parsed.success || parsed.data.workflow_id !== workflowId) {
      return NextResponse.json({ detail: "Invalid workflow replay response." }, { status: 502, headers });
    }
    return NextResponse.json(parsed.data, { headers });
  } catch {
    return NextResponse.json({ detail: "Workflow replay unavailable." }, { status: 503, headers });
  }
}
