import { NextResponse } from "next/server";
import { z } from "zod";
import { repositoryRetrievalSchema } from "@/lib/repository-ai";
import { allowsMutation } from "@/lib/request-origin";

const apiUrl = process.env.ATLAS_API_URL ?? "http://localhost:8000";
const headers = { "Cache-Control": "no-store" };
const requestSchema = z.object({
  query: z.string().trim().min(3).max(300),
  top_k: z.number().int().min(1).max(12).default(6),
  mode: z.enum(["lexical", "hybrid"]).default("hybrid"),
  path_prefix: z.string().trim().min(1).max(120).nullable().optional(),
}).strict();

export async function POST(request: Request) {
  if (!allowsMutation(request)) {
    return NextResponse.json({ detail: "origin not allowed" }, { status: 403, headers });
  }
  try {
    const text = await request.text();
    if (new TextEncoder().encode(text).byteLength > 2_048) {
      return NextResponse.json({ detail: "request too large" }, { status: 413, headers });
    }
    const body = requestSchema.parse(JSON.parse(text));
    const response = await fetch(`${apiUrl}/v1/ai/repository/retrieval/search`, {
      method: "POST",
      cache: "no-store",
      headers: {
        Authorization: `Bearer ${process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token"}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(10_000),
    });
    const parsed = repositoryRetrievalSchema.safeParse(await response.json());
    if (!response.ok || !parsed.success) {
      return NextResponse.json(
        { detail: "Repository retrieval could not complete." },
        { status: response.ok ? 502 : response.status, headers },
      );
    }
    return NextResponse.json(parsed.data, { headers });
  } catch {
    return NextResponse.json(
      { detail: "Invalid repository retrieval request." },
      { status: 400, headers },
    );
  }
}
