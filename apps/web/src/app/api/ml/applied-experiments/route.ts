import { NextResponse } from "next/server";
import { z } from "zod";
import { appliedExperimentSchema, appliedListSchema } from "@/lib/applied-ai";
import { allowsMutation } from "@/lib/request-origin";

const apiUrl = process.env.ATLAS_API_URL ?? "http://localhost:8000";
const headers = { "Cache-Control": "no-store" };

export async function GET(request: Request) {
  const id = new URL(request.url).searchParams.get("id");
  if (id !== null && !z.string().uuid().safeParse(id).success) {
    return NextResponse.json({ detail: "invalid applied experiment ID" }, { status: 400, headers });
  }
  return proxy(id ? `/v1/ml/applied-experiments/${id}` : "/v1/ml/applied-experiments", undefined, Boolean(id));
}

export async function POST(request: Request) {
  if (!allowsMutation(request)) {
    return NextResponse.json({ detail: "origin not allowed" }, { status: 403, headers });
  }
  const reader = request.body?.getReader();
  if (!reader) return NextResponse.json({ detail: "missing request" }, { status: 400, headers });
  let size = 0;
  const chunks: Uint8Array[] = [];
  try {
    while (true) {
      const chunk = await reader.read();
      if (chunk.done) break;
      size += chunk.value.byteLength;
      if (size > 2048) {
        await reader.cancel();
        return NextResponse.json({ detail: "request too large" }, { status: 413, headers });
      }
      chunks.push(chunk.value);
    }
    const parsed = z.object({ name: z.string().trim().min(2).max(120) }).strict()
      .safeParse(JSON.parse(Buffer.concat(chunks).toString("utf8")));
    if (!parsed.success) {
      return NextResponse.json({ detail: "invalid applied experiment request" }, { status: 400, headers });
    }
    return proxy("/v1/ml/applied-experiments", JSON.stringify(parsed.data), true);
  } catch {
    return NextResponse.json({ detail: "invalid applied experiment request" }, { status: 400, headers });
  } finally {
    reader.releaseLock();
  }
}

async function proxy(path: string, body: string | undefined, single: boolean) {
  try {
    const response = await fetch(`${apiUrl}${path}`, {
      method: body ? "POST" : "GET", body, cache: "no-store",
      headers: { Authorization: `Bearer ${process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token"}`,
        "Content-Type": "application/json" }, signal: AbortSignal.timeout(100000),
    });
    const payload: unknown = await response.json();
    if (!response.ok) {
      const detail = response.status === 409 ? "Applied experiment catalog limit reached."
        : response.status === 429 ? "Neural training is busy. Retry shortly."
        : "Applied AI service could not complete this request.";
      return NextResponse.json({ detail }, { status: response.status, headers });
    }
    const parsed = (single ? appliedExperimentSchema : appliedListSchema).safeParse(payload);
    if (!parsed.success) {
      return NextResponse.json({ detail: "invalid applied AI response" }, { status: 502, headers });
    }
    return NextResponse.json(parsed.data, { status: response.status, headers });
  } catch {
    return NextResponse.json({ detail: "Applied AI service unavailable." }, { status: 503, headers });
  }
}
