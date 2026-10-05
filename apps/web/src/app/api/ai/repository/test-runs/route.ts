import { NextResponse } from "next/server";
import { repositoryTestRunsSchema } from "@/lib/repository-ai";

const apiUrl = process.env.ATLAS_API_URL ?? "http://localhost:8000";
const headers = { "Cache-Control": "no-store" };

export async function GET() {
  try {
    const response = await fetch(`${apiUrl}/v1/ai/repository/test-runs`, {
      cache: "no-store",
      headers: { Authorization: `Bearer ${process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token"}` },
      signal: AbortSignal.timeout(10_000),
    });
    const parsed = repositoryTestRunsSchema.safeParse(await response.json());
    if (!response.ok || !parsed.success) throw new Error("invalid test run response");
    return NextResponse.json(parsed.data, { headers });
  } catch {
    return NextResponse.json({ detail: "Test runs are unavailable." }, { status: 503, headers });
  }
}
