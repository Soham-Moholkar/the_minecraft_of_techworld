import { NextResponse } from "next/server";
import { z } from "zod";
import { datasetListSchema, datasetSchema } from "@/lib/datasets";
import { allowsMutation } from "@/lib/request-origin";

const apiUrl = process.env.ATLAS_API_URL ?? "http://localhost:8000";
const headers = { "Cache-Control": "no-store" };

export async function GET(request: Request) {
  const id = new URL(request.url).searchParams.get("id");
  if (id !== null && !z.string().uuid().safeParse(id).success) {
    return NextResponse.json({ detail: "invalid dataset ID" }, { status: 400, headers });
  }
  return proxy(id ? `/v1/datasets/${id}` : "/v1/datasets", undefined, Boolean(id));
}

export async function POST(request: Request) {
  if (!allowsMutation(request)) {
    return NextResponse.json({ detail: "origin not allowed" }, { status: 403, headers });
  }
  // Count streamed bytes before JSON parsing; Content-Length can be absent or
  // forged. Stop reading oversized imports so they cannot consume unlimited RAM.
  const reader = request.body?.getReader();
  if (!reader) return NextResponse.json({ detail: "missing import" }, { status: 400, headers });
  let size = 0;
  const chunks: Uint8Array[] = [];
  try {
    while (true) {
      const chunk = await reader.read();
      if (chunk.done) break;
      size += chunk.value.byteLength;
      if (size > 300000) {
        await reader.cancel();
        return NextResponse.json({ detail: "import too large" }, { status: 413, headers });
      }
      chunks.push(chunk.value);
    }
    const body: unknown = JSON.parse(Buffer.concat(chunks).toString("utf8"));
    const parsed = z.object({ name: z.string().trim().min(2).max(120),
      csv_text: z.string().min(1).max(262144) }).strict().safeParse(body);
    if (!parsed.success) return NextResponse.json({ detail: "invalid dataset import" }, { status: 400, headers });
    return proxy("/v1/datasets", JSON.stringify(parsed.data), true);
  } catch {
    return NextResponse.json({ detail: "invalid dataset import" }, { status: 400, headers });
  } finally {
    reader.releaseLock();
  }
}

async function proxy(path: string, body: string | undefined, single: boolean) {
  try {
    const response = await fetch(`${apiUrl}${path}`, {
      method: body ? "POST" : "GET", body, cache: "no-store",
      headers: { Authorization: `Bearer ${process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token"}`,
        "Content-Type": "application/json" }, signal: AbortSignal.timeout(15000),
    });
    const payload: unknown = await response.json();
    if (!response.ok) {
      const detail = response.status === 422 ? "Check the CSV header, dates, finite costs, and integer request counts."
        : response.status === 404 ? "Dataset not found."
        : response.status === 409 ? "Dataset catalog limit reached."
        : "Dataset service could not complete this request.";
      return NextResponse.json({ detail }, { status: response.status, headers });
    }
    const parsed = (single ? datasetSchema : datasetListSchema).safeParse(payload);
    if (!parsed.success) return NextResponse.json({ detail: "invalid dataset response" }, { status: 502, headers });
    return NextResponse.json(parsed.data, { status: response.status, headers });
  } catch {
    return NextResponse.json({ detail: "Dataset service unavailable." }, { status: 503, headers });
  }
}
