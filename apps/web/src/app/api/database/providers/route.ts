import { NextResponse } from "next/server";
import { databaseProviderComparisonSchema } from "@/lib/database-providers";

const apiUrl =
  process.env.ATLAS_API_URL ??
  process.env.NEXT_PUBLIC_ATLAS_API_URL ??
  "http://localhost:8000";

export async function GET() {
  try {
    // The BFF retains product credentials. The browser receives only normalized
    // capabilities and never sees provider connection strings or driver errors.
    const token = process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token";
    const upstream = await fetch(`${apiUrl}/v1/database/providers`, {
      cache: "no-store",
      headers: { Authorization: `Bearer ${token}` },
      signal: AbortSignal.timeout(4000),
    });
    const payload: unknown = await upstream.json().catch(() => ({
      detail: "database-provider service returned an unreadable response",
    }));
    if (!upstream.ok) return NextResponse.json(payload, { status: upstream.status });

    const parsed = databaseProviderComparisonSchema.safeParse(payload);
    if (!parsed.success) {
      return NextResponse.json({ detail: "invalid database-provider response" }, { status: 502 });
    }
    return NextResponse.json(parsed.data, { headers: { "Cache-Control": "no-store" } });
  } catch {
    return NextResponse.json({ detail: "database-provider service unavailable" }, { status: 503 });
  }
}
