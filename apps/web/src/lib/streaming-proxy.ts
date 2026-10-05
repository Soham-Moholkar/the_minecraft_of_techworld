import "server-only";
import { NextResponse } from "next/server";
import { z } from "zod";
import { allowsMutation } from "@/lib/request-origin";
import { streamSchema } from "@/lib/streaming";
import { boundedText } from "@/lib/control-plane-proxy";

/** Fixed operations keep credentials, tenant/topic selection and URLs on the server. */
export async function streamProxy(suffix: "" | "/events" | "/consume" | "/lakehouse", request?: Request, input?: z.ZodType, output: z.ZodType = streamSchema) {
  const headers = { "Cache-Control": "no-store" };
  let body: string | undefined;
  if (request) {
    if (!allowsMutation(request)) return NextResponse.json({ detail: "origin not allowed" }, { status: 403, headers });
    try {
      const raw = await boundedText(request.body, 16_000);
      const parsed = input?.safeParse(JSON.parse(raw));
      if (!parsed?.success) throw new Error("invalid batch");
      body = JSON.stringify(parsed.data);
    } catch (error) {
      return NextResponse.json({ detail: "Invalid stream request." }, { status: error instanceof RangeError ? 413 : 400, headers });
    }
  }
  try {
    const result = await fetch(`${process.env.ATLAS_API_URL ?? "http://localhost:8000"}/v1/streaming/usage${suffix}`, {
      method: request ? "POST" : "GET", body, cache: "no-store", redirect: "error",
      headers: { Authorization: `Bearer ${process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token"}`, "Content-Type": "application/json" },
      signal: AbortSignal.timeout(15_000),
    });
    if (!result.ok) {
      await result.body?.cancel();
      return NextResponse.json({ detail: result.status === 403
      ? "Local streaming is disabled or access was denied."
      : result.status === 409 ? "Conflicting event identity or storage quota; inspect before retrying."
      : "Stream unavailable. Retry with the same event IDs; check broker retention and configuration." }, { status: result.status, headers });
    }
    const parsed = output.safeParse(JSON.parse(await boundedText(result.body, 1_000_000)));
    if (!parsed.success) return NextResponse.json({ detail: "Invalid stream response." }, { status: 502, headers });
    return NextResponse.json(parsed.data, { headers });
  } catch {
    return NextResponse.json({ detail: "Usage streaming is unavailable." }, { status: 503, headers });
  }
}
