import { NextResponse } from "next/server";
import { z } from "zod";
import { repositoryPromptVersionSchema, repositoryPromptVersionsSchema } from "@/lib/repository-ai";
import { allowsMutation } from "@/lib/request-origin";

const apiUrl = process.env.ATLAS_API_URL ?? "http://localhost:8000";
const headers = { "Cache-Control": "no-store" };
const createSchema = z.object({
  prompt_key: z.string().regex(/^[a-z][a-z0-9-]{2,63}$/),
  name: z.string().trim().min(3).max(120),
  instruction: z.string().trim().min(10).max(500),
}).strict();

async function upstream(path: string, init?: RequestInit) {
  return fetch(`${apiUrl}${path}`, {
    ...init,
    cache: "no-store",
    headers: {
      Authorization: `Bearer ${process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token"}`,
      "Content-Type": "application/json",
    },
    signal: AbortSignal.timeout(5_000),
  });
}

export async function GET() {
  try {
    const response = await upstream("/v1/ai/repository/prompts");
    const parsed = repositoryPromptVersionsSchema.safeParse(await response.json());
    if (!response.ok || !parsed.success) throw new Error("invalid prompt registry response");
    return NextResponse.json(parsed.data, { headers });
  } catch {
    return NextResponse.json({ detail: "Prompt registry is unavailable." }, { status: 503, headers });
  }
}

export async function POST(request: Request) {
  if (!allowsMutation(request)) {
    return NextResponse.json({ detail: "origin not allowed" }, { status: 403, headers });
  }
  try {
    const text = await request.text();
    if (new TextEncoder().encode(text).byteLength > 2_048) {
      return NextResponse.json({ detail: "request too large" }, { status: 413, headers });
    }
    const body = createSchema.parse(JSON.parse(text));
    const response = await upstream("/v1/ai/repository/prompts", {
      method: "POST",
      body: JSON.stringify(body),
    });
    const parsed = repositoryPromptVersionSchema.safeParse(await response.json());
    if (!response.ok || !parsed.success) {
      return NextResponse.json({ detail: "Prompt version could not be saved." }, { status: response.status || 502, headers });
    }
    return NextResponse.json(parsed.data, { status: 201, headers });
  } catch {
    return NextResponse.json({ detail: "Invalid prompt version." }, { status: 400, headers });
  }
}
