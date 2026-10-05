import { NextResponse } from "next/server";
import { z } from "zod";
import { repositoryTestRunSchema } from "@/lib/repository-ai";
import { allowsMutation } from "@/lib/request-origin";

const apiUrl = process.env.ATLAS_API_URL ?? "http://localhost:8000";
const headers = { "Cache-Control": "no-store" };
const idSchema = z.string().uuid();

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
    const response = await fetch(`${apiUrl}/v1/ai/repository/test-runs/${id}/retry`, {
      method: "POST",
      cache: "no-store",
      headers: { Authorization: `Bearer ${process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token"}` },
      signal: AbortSignal.timeout(10_000),
    });
    const payload: unknown = await response.json();
    const parsed = repositoryTestRunSchema.safeParse(payload);
    if (!response.ok || !parsed.success) {
      return NextResponse.json(
        { detail: "Fresh test retry could not be created." },
        { status: response.ok ? 502 : response.status, headers },
      );
    }
    return NextResponse.json(parsed.data, { status: 201, headers });
  } catch {
    return NextResponse.json({ detail: "Invalid test retry request." }, { status: 400, headers });
  }
}
