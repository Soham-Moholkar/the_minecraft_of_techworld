import "server-only";
import { NextResponse } from "next/server";
import { z } from "zod";
import { allowsMutation } from "@/lib/request-origin";

/** Stop reading before allocating an unbounded JSON request or provider response. */
export async function boundedBytes(body: ReadableStream<Uint8Array> | null, limit: number): Promise<Uint8Array<ArrayBuffer>> {
  if (!body) return new Uint8Array(0);
  const reader = body.getReader();
  const chunks: Uint8Array[] = [];
  let size = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > limit) { await reader.cancel(); throw new RangeError("payload limit"); }
      chunks.push(value);
    }
  } finally { reader.releaseLock(); }
  const data = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) { data.set(chunk, offset); offset += chunk.byteLength; }
  return data;
}

export async function boundedText(body: ReadableStream<Uint8Array> | null, limit: number): Promise<string> {
  return new TextDecoder().decode(await boundedBytes(body, limit));
}

/** Callers pass source-owned paths only; credentials never enter browser props. */
export async function controlPlaneProxy(path: string, output: z.ZodType, request?: Request, input?: z.ZodType) {
  const headers = { "Cache-Control": "no-store" };
  let body: string | undefined;
  if (request) {
    if (!allowsMutation(request)) return NextResponse.json({ detail: "origin not allowed" }, { status: 403, headers });
    try {
      const parsed = input?.safeParse(JSON.parse(await boundedText(request.body, 16_000)));
      if (!parsed?.success) throw new Error("invalid request");
      body = JSON.stringify(parsed.data);
    } catch (error) {
      return NextResponse.json({ detail: "Invalid request." }, { status: error instanceof RangeError ? 413 : 400, headers });
    }
  }
  try {
    const response = await fetch(`${process.env.ATLAS_API_URL ?? "http://localhost:8000"}${path}`, {
      method: request ? "POST" : "GET", body, cache: "no-store", redirect: "error",
      headers: { Authorization: `Bearer ${process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token"}`, "Content-Type": "application/json" },
      signal: AbortSignal.timeout(3000),
    });
    if (!response.ok) {
      await response.body?.cancel();
      return NextResponse.json({ detail: "Control plane request failed." }, { status: response.status, headers });
    }
    const parsed = output.safeParse(JSON.parse(await boundedText(response.body, 1_000_000)));
    if (!parsed.success) return NextResponse.json({ detail: "Invalid control plane response." }, { status: 502, headers });
    return NextResponse.json(parsed.data, { status: response.status, headers });
  } catch {
    return NextResponse.json({ detail: "Control plane unavailable." }, { status: 503, headers });
  }
}
