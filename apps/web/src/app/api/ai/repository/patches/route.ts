import { NextResponse } from "next/server";
import { z } from "zod";
import {
  repositoryPatchProposalSchema,
  repositoryPatchProposalsSchema,
} from "@/lib/repository-ai";
import { allowsMutation } from "@/lib/request-origin";

const apiUrl = process.env.ATLAS_API_URL ?? "http://localhost:8000";
const headers = { "Cache-Control": "no-store" };
const proposalSchema = z.object({
  path: z.string().min(1).max(240),
  expected_sha256: z.string().regex(/^[0-9a-f]{64}$/),
  start_line: z.number().int().positive(),
  end_line: z.number().int().positive(),
  replacement: z.string().max(100_000),
  summary: z.string().trim().min(5).max(200),
  rationale: z.string().trim().min(10).max(2_000),
}).strict().refine((value) => value.end_line >= value.start_line, "invalid line range");

async function upstream(path: string, init?: RequestInit) {
  return fetch(`${apiUrl}${path}`, {
    ...init,
    cache: "no-store",
    headers: {
      Authorization: `Bearer ${process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token"}`,
      "Content-Type": "application/json",
    },
    signal: AbortSignal.timeout(10_000),
  });
}

export async function GET() {
  try {
    const response = await upstream("/v1/ai/repository/patches");
    const parsed = repositoryPatchProposalsSchema.safeParse(await response.json());
    if (!response.ok || !parsed.success) throw new Error("invalid patch response");
    return NextResponse.json(parsed.data, { headers });
  } catch {
    return NextResponse.json({ detail: "Patch proposals are unavailable." }, { status: 503, headers });
  }
}

export async function POST(request: Request) {
  if (!allowsMutation(request)) {
    return NextResponse.json({ detail: "origin not allowed" }, { status: 403, headers });
  }
  try {
    const text = await request.text();
    if (Buffer.byteLength(text) > 110_000) {
      return NextResponse.json({ detail: "request too large" }, { status: 413, headers });
    }
    const parsed = proposalSchema.safeParse(JSON.parse(text));
    if (!parsed.success) {
      return NextResponse.json({ detail: "invalid patch proposal" }, { status: 400, headers });
    }
    const response = await upstream("/v1/ai/repository/patches", {
      method: "POST", body: JSON.stringify(parsed.data),
    });
    const payload: unknown = await response.json();
    const result = repositoryPatchProposalSchema.safeParse(payload);
    if (!response.ok || !result.success) {
      return NextResponse.json(
        { detail: response.status === 503 ? "Local patch tools are disabled." : "Patch proposal was rejected." },
        { status: response.ok ? 502 : response.status, headers },
      );
    }
    return NextResponse.json(result.data, { status: 201, headers });
  } catch {
    return NextResponse.json({ detail: "Invalid patch proposal." }, { status: 400, headers });
  }
}
