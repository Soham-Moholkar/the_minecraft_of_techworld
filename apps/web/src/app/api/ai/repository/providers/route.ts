import { NextResponse } from "next/server";
import { repositoryProviderHealthSchema } from "@/lib/repository-ai";

const apiUrl = process.env.ATLAS_API_URL ?? "http://localhost:8000";
const headers = { "Cache-Control": "no-store" };

export async function GET() {
  try {
    const response = await fetch(`${apiUrl}/v1/ai/repository/providers`, {
      cache: "no-store",
      headers: {
        Authorization: `Bearer ${process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token"}`,
      },
      signal: AbortSignal.timeout(5_000),
    });
    const payload: unknown = await response.json();
    if (!response.ok) {
      return NextResponse.json({ detail: "Provider health is unavailable." }, { status: response.status, headers });
    }
    const parsed = repositoryProviderHealthSchema.safeParse(payload);
    if (!parsed.success) {
      return NextResponse.json({ detail: "Provider health returned an invalid contract." }, { status: 502, headers });
    }
    return NextResponse.json(parsed.data, { headers });
  } catch {
    return NextResponse.json({ detail: "Provider health is unavailable." }, { status: 503, headers });
  }
}
