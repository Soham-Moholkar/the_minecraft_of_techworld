import { NextResponse } from "next/server";
import { databaseCacheProfileSchema } from "@/lib/phase-four";

const apiUrl =
  process.env.ATLAS_API_URL ??
  process.env.NEXT_PUBLIC_ATLAS_API_URL ??
  "http://localhost:8000";

export async function GET() {
  try {
    // Authentication remains server-side. The browser receives only the
    // bounded portfolio aggregate, never a Redis URL, credential, or key.
    const token = process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token";
    const upstream = await fetch(`${apiUrl}/v1/database/cache-profile`, {
      cache: "no-store",
      headers: { Authorization: `Bearer ${token}` },
      signal: AbortSignal.timeout(3000),
    });
    const payload: unknown = await upstream.json().catch(() => ({
      detail: "cache profile returned an unreadable response",
    }));
    if (!upstream.ok) return NextResponse.json(
      { detail: "cache profile request failed" },
      { status: upstream.status, headers: { "Cache-Control": "no-store" } },
    );

    const parsed = databaseCacheProfileSchema.safeParse(payload);
    if (!parsed.success) {
      return NextResponse.json({ detail: "invalid cache profile response" }, { status: 502 });
    }
    return NextResponse.json(parsed.data, { headers: { "Cache-Control": "no-store" } });
  } catch {
    return NextResponse.json({ detail: "cache profile service unavailable" }, { status: 503 });
  }
}
