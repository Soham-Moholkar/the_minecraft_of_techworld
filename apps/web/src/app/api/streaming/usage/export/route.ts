import "server-only";
import { NextResponse } from "next/server";
import { boundedBytes } from "@/lib/control-plane-proxy";

/** Fixed tenant-authenticated download; no filename or remote URL from callers. */
export async function GET() {
  const headers = { "Cache-Control": "no-store" };
  try {
    const response = await fetch(`${process.env.ATLAS_API_URL ?? "http://localhost:8000"}/v1/streaming/usage/export`, {
      cache: "no-store", redirect: "error", signal: AbortSignal.timeout(15_000),
      headers: { Authorization: `Bearer ${process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token"}` },
    });
    if (!response.ok) {
      await response.body?.cancel();
      return NextResponse.json({ detail: "Parquet export unavailable; verify local streaming and Arrow installation." }, { status: response.status, headers });
    }
    if (response.headers.get("Content-Type") !== "application/vnd.apache.parquet") {
      await response.body?.cancel();
      throw new Error("invalid export");
    }
    const content = await boundedBytes(response.body, 2_000_000);
    return new Response(content.buffer, { headers: { ...headers,
      "Content-Type": "application/vnd.apache.parquet",
      "Content-Disposition": 'attachment; filename="atlas-usage.parquet"',
      "X-Content-Type-Options": "nosniff",
    } });
  } catch { return NextResponse.json({ detail: "Parquet export unavailable." }, { status: 503, headers }); }
}
