import { NextResponse } from "next/server";
import { concurrencyProfileSchema } from "@/lib/concurrency-profile";

const apiUrl =
  process.env.ATLAS_API_URL ??
  process.env.NEXT_PUBLIC_ATLAS_API_URL ??
  "http://localhost:8000";

export async function GET() {
  try {
    // Credentials stay inside the BFF. The browser only receives the bounded,
    // read-only profile and can never choose a SQL statement or database pragma.
    const token = process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token";
    const upstream = await fetch(`${apiUrl}/v1/database/concurrency-profile`, {
      cache: "no-store",
      headers: { Authorization: `Bearer ${token}` },
      signal: AbortSignal.timeout(3000),
    });
    const payload: unknown = await upstream.json().catch(() => ({
      detail: "concurrency-profile service returned an unreadable response",
    }));
    if (!upstream.ok) {
      return NextResponse.json(payload, { status: upstream.status });
    }

    // Validate at the service boundary so backend contract drift cannot silently
    // produce an authoritative-looking but misleading isolation comparison.
    const parsedProfile = concurrencyProfileSchema.safeParse(payload);
    if (!parsedProfile.success) {
      return NextResponse.json({ detail: "invalid concurrency-profile response" }, { status: 502 });
    }

    return NextResponse.json(parsedProfile.data, {
      headers: { "Cache-Control": "no-store" },
    });
  } catch {
    return NextResponse.json({ detail: "concurrency-profile service unavailable" }, { status: 503 });
  }
}

