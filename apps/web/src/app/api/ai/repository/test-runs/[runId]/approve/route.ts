import { NextResponse } from "next/server";
import { z } from "zod";
import { repositoryTestRunSchema } from "@/lib/repository-ai";
import { allowsMutation } from "@/lib/request-origin";

const apiUrl = process.env.ATLAS_API_URL ?? "http://localhost:8000";
const headers = { "Cache-Control": "no-store" };
const idSchema = z.string().uuid();
const requestSchema = z.object({
  run_digest: z.string().regex(/^[0-9a-f]{64}$/),
  confirmation: z.literal("RUN ISOLATED TEST PROFILE"),
}).strict();

export async function POST(
  request: Request,
  { params }: { params: Promise<{ runId: string }> },
) {
  if (!allowsMutation(request)) {
    return NextResponse.json({ detail: "origin not allowed" }, { status: 403, headers });
  }
  try {
    const { runId } = await params;
    const id = idSchema.parse(runId);
    const text = await request.text();
    if (Buffer.byteLength(text) > 1_024) {
      return NextResponse.json({ detail: "request too large" }, { status: 413, headers });
    }
    const input = requestSchema.parse(JSON.parse(text));
    const response = await fetch(`${apiUrl}/v1/ai/repository/test-runs/${id}/approve`, {
      method: "POST",
      cache: "no-store",
      headers: {
        Authorization: `Bearer ${process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token"}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(input),
      signal: AbortSignal.timeout(10_000),
    });
    const payload: unknown = await response.json();
    const parsed = repositoryTestRunSchema.safeParse(payload);
    if (!response.ok || !parsed.success) {
      return NextResponse.json({ detail: "Test run approval failed." }, { status: response.ok ? 502 : response.status, headers });
    }
    return NextResponse.json(parsed.data, { headers });
  } catch {
    return NextResponse.json({ detail: "Invalid test run approval." }, { status: 400, headers });
  }
}
