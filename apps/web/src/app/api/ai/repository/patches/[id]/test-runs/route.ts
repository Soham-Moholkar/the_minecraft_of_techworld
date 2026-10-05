import { NextResponse } from "next/server";
import { z } from "zod";
import { repositoryTestRunSchema } from "@/lib/repository-ai";
import { allowsMutation } from "@/lib/request-origin";

const apiUrl = process.env.ATLAS_API_URL ?? "http://localhost:8000";
const headers = { "Cache-Control": "no-store" };
const idSchema = z.string().uuid();
const requestSchema = z.object({
  profile_id: z.string().regex(/^[a-z][a-z0-9-]{2,63}$/),
}).strict();

export async function POST(
  request: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  if (!allowsMutation(request)) {
    return NextResponse.json({ detail: "origin not allowed" }, { status: 403, headers });
  }
  try {
    const id = idSchema.parse((await params).id);
    const text = await request.text();
    if (Buffer.byteLength(text) > 1_024) {
      return NextResponse.json({ detail: "request too large" }, { status: 413, headers });
    }
    const input = requestSchema.parse(JSON.parse(text));
    const response = await fetch(`${apiUrl}/v1/ai/repository/patches/${id}/test-runs`, {
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
      return NextResponse.json(
        { detail: response.status === 503 ? "Isolated test tools are disabled." : "Test run could not be requested." },
        { status: response.ok ? 502 : response.status, headers },
      );
    }
    return NextResponse.json(parsed.data, { status: 201, headers });
  } catch {
    return NextResponse.json({ detail: "Invalid test run request." }, { status: 400, headers });
  }
}
