import { NextResponse } from "next/server";

const apiUrl = process.env.ATLAS_API_URL ?? process.env.NEXT_PUBLIC_ATLAS_API_URL ?? "http://localhost:8000";

export async function GET() {
  try {
    const token = process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token";
    const upstream = await fetch(`${apiUrl}/v1/me`, {
      cache: "no-store",
      headers: { Authorization: `Bearer ${token}` },
      signal: AbortSignal.timeout(3000),
    });
    return NextResponse.json(await upstream.json(), { status: upstream.status });
  } catch {
    return NextResponse.json({ detail: "identity provider unavailable" }, { status: 503 });
  }
}

