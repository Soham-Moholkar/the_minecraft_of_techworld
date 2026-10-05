import { NextResponse } from "next/server";
import {
  documentProjectionPublishSchema,
  documentProjectionSnapshotSchema,
} from "@/lib/document-projection";

const apiUrl =
  process.env.ATLAS_API_URL ??
  process.env.NEXT_PUBLIC_ATLAS_API_URL ??
  "http://localhost:8000";

const token = process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token";

async function readPayload(response: Response): Promise<unknown> {
  return response.json().catch(() => ({ detail: "document projection returned an unreadable response" }));
}

export async function GET() {
  try {
    // Keep the development credential on the server and proxy only the API's
    // allowlisted document projection contract into the browser.
    const upstream = await fetch(`${apiUrl}/v1/database/document-projection`, {
      cache: "no-store",
      headers: { Authorization: `Bearer ${token}` },
      signal: AbortSignal.timeout(4000),
    });
    const payload = await readPayload(upstream);
    if (!upstream.ok) return NextResponse.json(payload, { status: upstream.status });

    const parsed = documentProjectionSnapshotSchema.safeParse(payload);
    if (!parsed.success) {
      return NextResponse.json({ detail: "invalid document projection response" }, { status: 502 });
    }
    return NextResponse.json(parsed.data, { headers: { "Cache-Control": "no-store" } });
  } catch {
    return NextResponse.json({ detail: "document projection service unavailable" }, { status: 503 });
  }
}

export async function POST() {
  try {
    // Publication is an authenticated product mutation. The upstream API still
    // performs the authoritative role check and tenant scoping.
    const upstream = await fetch(`${apiUrl}/v1/database/document-projection/publish`, {
      method: "POST",
      cache: "no-store",
      headers: { Authorization: `Bearer ${token}` },
      signal: AbortSignal.timeout(4000),
    });
    const payload = await readPayload(upstream);
    if (!upstream.ok) return NextResponse.json(payload, { status: upstream.status });

    const parsed = documentProjectionPublishSchema.safeParse(payload);
    if (!parsed.success) {
      return NextResponse.json({ detail: "invalid document projection publish response" }, { status: 502 });
    }
    return NextResponse.json(parsed.data, { headers: { "Cache-Control": "no-store" } });
  } catch {
    return NextResponse.json({ detail: "document projection service unavailable" }, { status: 503 });
  }
}
