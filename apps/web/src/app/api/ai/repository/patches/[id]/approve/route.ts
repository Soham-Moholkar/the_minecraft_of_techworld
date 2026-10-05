import { NextResponse } from "next/server";
import { z } from "zod";
import { repositoryPatchProposalSchema } from "@/lib/repository-ai";
import { allowsMutation } from "@/lib/request-origin";

const apiUrl = process.env.ATLAS_API_URL ?? "http://localhost:8000";
const headers = { "Cache-Control": "no-store" };
const bodySchema = z.object({
  proposal_digest: z.string().regex(/^[0-9a-f]{64}$/),
  confirmation: z.literal("APPLY EXACT PATCH"),
}).strict();

export async function POST(request: Request, context: { params: Promise<{ id: string }> }) {
  if (!allowsMutation(request)) return NextResponse.json({ detail: "origin not allowed" }, { status: 403, headers });
  const { id } = await context.params;
  if (!z.string().uuid().safeParse(id).success) return NextResponse.json({ detail: "invalid proposal" }, { status: 400, headers });
  try {
    const body = bodySchema.parse(await request.json());
    const response = await fetch(`${apiUrl}/v1/ai/repository/patches/${id}/approve`, {
      method: "POST", cache: "no-store", body: JSON.stringify(body),
      headers: { Authorization: `Bearer ${process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token"}`, "Content-Type": "application/json" },
      signal: AbortSignal.timeout(10_000),
    });
    const payload: unknown = await response.json();
    const parsed = repositoryPatchProposalSchema.safeParse(payload);
    if (!response.ok || !parsed.success) return NextResponse.json({ detail: response.status === 409 ? "Patch is stale or no longer pending." : "Patch could not be applied." }, { status: response.ok ? 502 : response.status, headers });
    return NextResponse.json(parsed.data, { headers });
  } catch {
    return NextResponse.json({ detail: "Invalid patch approval." }, { status: 400, headers });
  }
}
