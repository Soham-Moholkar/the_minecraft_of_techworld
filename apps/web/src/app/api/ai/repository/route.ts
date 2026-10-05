import { NextResponse } from "next/server";
import { z } from "zod";
import {
  repositoryCatalogSchema,
  repositoryExplanationSchema,
} from "@/lib/repository-ai";
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

async function proxy(path: string, init?: RequestInit) {
  try {
    const response = await fetch(`${apiUrl}${path}`, {
      ...init,
      cache: "no-store",
      headers: {
        Authorization: `Bearer ${process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token"}`,
        "Content-Type": "application/json",
      },
      signal: AbortSignal.timeout(95_000),
    });
    const payload: unknown = await response.json();
    if (!response.ok) {
      const detail = response.status === 503
        ? "Repository AI is not configured. Add ATLAS_OPENAI_API_KEY to the API environment."
        : response.status === 429
          ? "The repository model is busy. Retry shortly."
          : "Repository AI could not complete this request.";
      return NextResponse.json({ detail }, { status: response.status, headers: responseHeaders });
    }
    const schema = path.endsWith("/files") ? repositoryCatalogSchema : repositoryExplanationSchema;
    const parsed = schema.safeParse(payload);
    if (!parsed.success) {
      return NextResponse.json(
        { detail: "Repository AI returned an invalid contract." },
        { status: 502, headers: responseHeaders },
      );
    }
    return NextResponse.json(parsed.data, { status: response.status, headers: responseHeaders });
  } catch {
    return NextResponse.json(
      { detail: "Repository AI service is unavailable." },
      { status: 503, headers: responseHeaders },
    );
  }
}

export async function GET() {
  return proxy("/v1/ai/repository/files");
}

export async function POST(request: Request) {
  if (!allowsMutation(request)) {
    return NextResponse.json({ detail: "origin not allowed" }, { status: 403, headers: responseHeaders });
  }
  const reader = request.body?.getReader();
  if (!reader) {
    return NextResponse.json({ detail: "missing request" }, { status: 400, headers: responseHeaders });
  }
  const chunks: Uint8Array[] = [];
  let size = 0;
  try {
    while (true) {
      const chunk = await reader.read();
      if (chunk.done) break;
      size += chunk.value.byteLength;
      if (size > 4_096) {
        await reader.cancel();
        return NextResponse.json({ detail: "request too large" }, { status: 413, headers: responseHeaders });
      }
      chunks.push(chunk.value);
    }
    const body: unknown = JSON.parse(Buffer.concat(chunks).toString("utf8"));
    const parsed = requestSchema.safeParse(body);
    if (!parsed.success) {
      return NextResponse.json({ detail: "invalid repository request" }, { status: 400, headers: responseHeaders });
    }
    return proxy("/v1/ai/repository/explain", {
      method: "POST",
      body: JSON.stringify(parsed.data),
    });
  } catch {
    return NextResponse.json({ detail: "invalid repository request" }, { status: 400, headers: responseHeaders });
  } finally {
    reader.releaseLock();
  }
}
