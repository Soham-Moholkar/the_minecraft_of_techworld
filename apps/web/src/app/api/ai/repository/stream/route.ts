import { NextResponse } from "next/server";
import { z } from "zod";
import { allowsMutation } from "@/lib/request-origin";

const apiUrl = process.env.ATLAS_API_URL ?? "http://localhost:8000";
const responseHeaders = { "Cache-Control": "no-store" };
const requestSchema = z.object({
  path: z.string().min(1).max(240),
  start_line: z.number().int().positive(),
  end_line: z.number().int().positive(),
  intent: z.enum(["explain", "review", "change_plan"]),
  tier: z.enum(["auto", "economy", "balanced"]),
  provider: z.enum(["auto", "openai", "local"]),
  instruction: z.string().trim().min(3).max(500),
  prompt_version_id: z.string().uuid().nullable().optional(),
}).strict().superRefine((value, context) => {
  if (value.end_line < value.start_line || value.end_line - value.start_line >= 120) {
    context.addIssue({ code: "custom", message: "invalid line range" });
  }
});

export async function POST(request: Request) {
  if (!allowsMutation(request)) {
    return NextResponse.json({ detail: "origin not allowed" }, { status: 403, headers: responseHeaders });
  }
  let body: unknown;
  try {
    const text = await request.text();
    if (new TextEncoder().encode(text).byteLength > 4_096) {
      return NextResponse.json({ detail: "request too large" }, { status: 413, headers: responseHeaders });
    }
    body = JSON.parse(text);
  } catch {
    return NextResponse.json({ detail: "invalid repository request" }, { status: 400, headers: responseHeaders });
  }
  const parsed = requestSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json({ detail: "invalid repository request" }, { status: 400, headers: responseHeaders });
  }
  try {
    const upstream = await fetch(`${apiUrl}/v1/ai/repository/explain/stream`, {
      method: "POST",
      cache: "no-store",
      headers: {
        Authorization: `Bearer ${process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token"}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(parsed.data),
      signal: AbortSignal.timeout(95_000),
    });
    if (!upstream.ok || !upstream.body) {
      return NextResponse.json(
        { detail: "Repository AI stream could not start." },
        { status: upstream.status || 503, headers: responseHeaders },
      );
    }
    return new Response(upstream.body, {
      status: 200,
      headers: {
        ...responseHeaders,
        "Content-Type": "text/event-stream; charset=utf-8",
        "X-Accel-Buffering": "no",
      },
    });
  } catch {
    return NextResponse.json(
      { detail: "Repository AI stream is unavailable." },
      { status: 503, headers: responseHeaders },
    );
  }
}
