import { NextResponse } from "next/server";
import { repositoryAIOperationsSchema } from "@/lib/repository-ai";

const apiUrl = process.env.ATLAS_API_URL ?? "http://localhost:8000";
const headers = { "Cache-Control": "no-store" };

export async function GET() {
  try {
    const response = await fetch(`${apiUrl}/v1/ai/repository/operations`, {
      cache: "no-store",
      headers: {
        Authorization: `Bearer ${process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token"}`,
      },
      signal: AbortSignal.timeout(5_000),
    });
    const parsed = repositoryAIOperationsSchema.safeParse(await response.json());
    if (!response.ok || !parsed.success) {
      return NextResponse.json(
        { detail: "Repository AI operations are unavailable." },
        { status: response.ok ? 502 : response.status, headers },
      );
    }
    return NextResponse.json(parsed.data, { headers });
  } catch {
    return NextResponse.json(
      { detail: "Repository AI operations are unavailable." },
      { status: 503, headers },
    );
  }
}
