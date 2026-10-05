import "server-only";
import { NextResponse } from "next/server";
import { z } from "zod";
import { allowsMutation } from "@/lib/request-origin";

const headers = { "Cache-Control": "no-store" };

/** Server-only credential and fixed path fragments; note text is never logged. */
export async function memoryProxy<T>(
  suffix: string, output: z.ZodType<T>, request?: Request, input?: z.ZodType,
) {
  if (request && !allowsMutation(request)) {
    return NextResponse.json({ detail: "origin not allowed" }, { status: 403, headers });
  }
  let body: string | undefined;
  if (request) {
    try {
      const text = await request.text();
      if (new TextEncoder().encode(text).byteLength > 12_000) {
        return NextResponse.json({ detail: "request too large" }, { status: 413, headers });
      }
      const parsed = input?.safeParse(JSON.parse(text));
      if (!parsed?.success) throw new Error("invalid input");
      body = JSON.stringify(parsed.data);
    } catch {
      return NextResponse.json({ detail: "Invalid memory request." }, { status: 400, headers });
    }
  }
  try {
    const response = await fetch(
      `${process.env.ATLAS_API_URL ?? "http://localhost:8000"}/v1/ai/repository/memory${suffix}`,
      {
        method: request?.method ?? "GET", body, cache: "no-store",
        headers: {
          Authorization: `Bearer ${process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token"}`,
          "Content-Type": "application/json",
        },
        signal: AbortSignal.timeout(10_000),
      },
    );
    if (!response.ok) {
      // Do not forward upstream validation bodies: they can contain rejected secrets.
      const detail = response.status === 400 ? "Memory rejected: review for credentials or approval material."
        : response.status === 409 ? "Memory capacity or write conflict; refresh and retry."
        : response.status === 404 ? "Memory not found." : "Local memory request failed.";
      return NextResponse.json({ detail }, { status: response.status, headers });
    }
    const parsed = output.safeParse(await response.json());
    if (!parsed.success) {
      return NextResponse.json({ detail: "Invalid memory response." }, { status: 502, headers });
    }
    return NextResponse.json(parsed.data, { status: response.status, headers });
  } catch {
    return NextResponse.json({ detail: "Local operator memory is unavailable." }, { status: 503, headers });
  }
}
