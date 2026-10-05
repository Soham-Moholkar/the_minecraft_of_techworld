import { NextResponse } from "next/server";
import { z } from "zod";

const apiUrl =
  process.env.ATLAS_API_URL ??
  process.env.NEXT_PUBLIC_ATLAS_API_URL ??
  "http://localhost:8000";
const browserWebSocketUrl =
  process.env.ATLAS_BROWSER_WS_URL ?? "ws://localhost:8000/v1/realtime/ws";

const upstreamTicket = z.object({
  ticket: z.string().min(32).max(128),
  expires_in_seconds: z.number().int().positive(),
});

export async function POST(request: Request) {
  const requestOrigin = new URL(request.url).origin;
  const origin = request.headers.get("origin");
  const fetchSite = request.headers.get("sec-fetch-site");
  // In a container the framework's internal request URL uses the container host,
  // while Origin correctly names the public browser host. Trust only the explicit
  // deployment allowlist plus the directly observed origin for non-proxied setups.
  const allowedOrigins = new Set([
    requestOrigin,
    ...(process.env.ATLAS_ALLOWED_ORIGINS ?? "http://localhost:3000")
      .split(",")
      .map((value) => value.trim())
      .filter(Boolean),
  ]);
  // The route uses no browser credential today, but rejecting cross-site issuance
  // prevents it becoming a CSRF primitive when signed sessions replace local auth.
  if ((origin && !allowedOrigins.has(origin)) || fetchSite === "cross-site") {
    return NextResponse.json({ detail: "cross-site ticket request rejected" }, { status: 403 });
  }

  try {
    const token = process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token";
    const upstream = await fetch(`${apiUrl}/v1/realtime/tickets`, {
      method: "POST",
      cache: "no-store",
      headers: { Authorization: `Bearer ${token}` },
      signal: AbortSignal.timeout(3000),
    });
    const payload: unknown = await upstream.json();
    if (!upstream.ok) {
      return NextResponse.json(payload, { status: upstream.status });
    }
    const parsed = upstreamTicket.safeParse(payload);
    if (!parsed.success) {
      return NextResponse.json({ detail: "invalid realtime ticket response" }, { status: 502 });
    }
    const separator = browserWebSocketUrl.includes("?") ? "&" : "?";
    return NextResponse.json(
      {
        url: `${browserWebSocketUrl}${separator}ticket=${encodeURIComponent(parsed.data.ticket)}`,
        expires_in_seconds: parsed.data.expires_in_seconds,
      },
      { headers: { "Cache-Control": "no-store" } },
    );
  } catch {
    return NextResponse.json({ detail: "realtime ticket service unavailable" }, { status: 503 });
  }
}
