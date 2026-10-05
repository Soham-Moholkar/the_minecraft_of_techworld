import { NextResponse } from "next/server";
import { z } from "zod";
import { experimentListSchema, experimentSchema } from "@/lib/machine-learning";
import { allowsMutation } from "@/lib/request-origin";

const apiUrl = process.env.ATLAS_API_URL ?? "http://localhost:8000";
const responseHeaders = { "Cache-Control": "no-store" };

export async function GET(request: Request) {
  const id = new URL(request.url).searchParams.get("id");
  if (id !== null && !z.string().uuid().safeParse(id).success) {
    return NextResponse.json({ detail: "invalid experiment ID" }, { status: 400, headers: responseHeaders });
  }
  return proxy(id ? `/v1/ml/experiments/${id}` : "/v1/ml/experiments", undefined, Boolean(id));
}

export async function POST(request: Request) {
  if (!allowsMutation(request)) {
    return NextResponse.json({ detail: "origin not allowed" }, { status: 403, headers: responseHeaders });
  }
  const reader = request.body?.getReader();
  if (!reader) return NextResponse.json({ detail: "missing experiment request" }, { status: 400, headers: responseHeaders });
  let size = 0;
  const chunks: Uint8Array[] = [];
  try {
    while (true) {
      const chunk = await reader.read();
      if (chunk.done) break;
      size += chunk.value.byteLength;
      if (size > 4096) {
        await reader.cancel();
        return NextResponse.json({ detail: "experiment request too large" }, { status: 413, headers: responseHeaders });
      }
      chunks.push(chunk.value);
    }
    const body: unknown = JSON.parse(Buffer.concat(chunks).toString("utf8"));
    const parsed = z.object({
      name: z.string().trim().min(2).max(120), dataset_id: z.string().uuid(),
      suite: z.enum(["classical", "neural", "frameworks"]).default("classical"),
    }).strict().safeParse(body);
    if (!parsed.success) {
      return NextResponse.json({ detail: "invalid experiment request" }, { status: 400, headers: responseHeaders });
    }
    return proxy("/v1/ml/experiments", JSON.stringify(parsed.data), true);
  } catch {
    return NextResponse.json({ detail: "invalid experiment request" }, { status: 400, headers: responseHeaders });
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
      const detail = response.status === 404 ? "Dataset or experiment not found."
        : response.status === 422 ? "Check dataset size and target classes. Neural runs need 20–2,000 rows and at most 32 services."
        : response.status === 409 ? "Experiment catalog limit reached."
        : response.status === 429 ? "Neural training is busy. Retry after the active run."
        : "Model service could not complete this request.";
      return NextResponse.json({ detail }, { status: response.status, headers: responseHeaders });
    }
    const parsed = (single ? experimentSchema : experimentListSchema).safeParse(payload);
    if (!parsed.success) {
      return NextResponse.json({ detail: "invalid model response" }, { status: 502, headers: responseHeaders });
    }
    return NextResponse.json(parsed.data, { status: response.status, headers: responseHeaders });
  } catch {
    return NextResponse.json({ detail: "Model service unavailable." }, { status: 503, headers: responseHeaders });
  }
}
