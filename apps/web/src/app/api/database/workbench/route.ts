import { NextResponse } from "next/server";
import { allowsMutation } from "@/lib/request-origin";
import {
  databaseWorkbenchRequestSchema,
  databaseWorkbenchSchema,
} from "@/lib/phase-four";

const apiUrl =
  process.env.ATLAS_API_URL ??
  process.env.NEXT_PUBLIC_ATLAS_API_URL ??
  "http://localhost:8000";

export async function POST(request: Request) {
  if (!allowsMutation(request)) {
    return NextResponse.json({ detail: "origin not allowed" }, { status: 403 });
  }
  const body: unknown = await request.json().catch(() => null);
  const parsedRequest = databaseWorkbenchRequestSchema.safeParse(body);
  if (!parsedRequest.success) {
    return NextResponse.json({ detail: "invalid workbench parameters" }, { status: 400 });
  }

  try {
    // This is deliberately not a generic SQL proxy. Both BFF and API accept
    // one source-reviewed query name with typed, bounded parameters only.
    const token = process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token";
    const upstream = await fetch(`${apiUrl}/v1/database/workbench`, {
      method: "POST",
      cache: "no-store",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(parsedRequest.data),
      signal: AbortSignal.timeout(3000),
    });
    const payload: unknown = await upstream.json().catch(() => ({
      detail: "database workbench returned an unreadable response",
    }));
    if (!upstream.ok) return NextResponse.json(
      { detail: "database workbench request failed" },
      { status: upstream.status, headers: { "Cache-Control": "no-store" } },
    );

    const parsed = databaseWorkbenchSchema.safeParse(payload);
    if (!parsed.success) {
      return NextResponse.json({ detail: "invalid database workbench response" }, { status: 502 });
    }
    return NextResponse.json(parsed.data, { headers: { "Cache-Control": "no-store" } });
  } catch {
    return NextResponse.json({ detail: "database workbench service unavailable" }, { status: 503 });
  }
}
