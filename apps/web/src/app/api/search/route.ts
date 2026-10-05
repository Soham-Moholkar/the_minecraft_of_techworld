import { type NextRequest, NextResponse } from "next/server";

const apiUrl = process.env.ATLAS_API_URL ?? process.env.NEXT_PUBLIC_ATLAS_API_URL ?? "http://localhost:8000";

export async function GET(request: NextRequest) {
  const query = request.nextUrl.searchParams.get("q")?.trim() ?? "";
  if (query.length < 2 || query.length > 120) {
    return NextResponse.json({ detail: "query must contain 2 to 120 characters" }, { status: 422 });
  }
  try {
    const token = process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token";
    const upstream = await fetch(`${apiUrl}/v1/search?q=${encodeURIComponent(query)}`, {
      cache: "no-store",
      headers: { Authorization: `Bearer ${token}` },
      signal: AbortSignal.timeout(3000),
    });
    return NextResponse.json(await upstream.json(), { status: upstream.status });
  } catch {
    return NextResponse.json({ detail: "search provider unavailable" }, { status: 503 });
  }
}

