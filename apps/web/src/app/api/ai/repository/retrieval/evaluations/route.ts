import { NextResponse } from "next/server";
import {
  repositoryRetrievalEvaluationSchema,
  repositoryRetrievalEvaluationsSchema,
} from "@/lib/repository-ai";
import { allowsMutation } from "@/lib/request-origin";

const apiUrl = process.env.ATLAS_API_URL ?? "http://localhost:8000";
const headers = { "Cache-Control": "no-store" };

async function upstream(method = "GET") {
  return fetch(`${apiUrl}/v1/ai/repository/retrieval/evaluations`, {
    method,
    cache: "no-store",
    headers: {
      Authorization: `Bearer ${process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token"}`,
      "Content-Type": "application/json",
    },
    signal: AbortSignal.timeout(15_000),
  });
}

export async function GET() {
  try {
    const response = await upstream();
    const parsed = repositoryRetrievalEvaluationsSchema.safeParse(await response.json());
    if (!response.ok || !parsed.success) throw new Error("invalid evaluation history");
    return NextResponse.json(parsed.data, { headers });
  } catch {
    return NextResponse.json(
      { detail: "Retrieval evaluation history is unavailable." },
      { status: 503, headers },
    );
  }
}

export async function POST(request: Request) {
  if (!allowsMutation(request)) {
    return NextResponse.json({ detail: "origin not allowed" }, { status: 403, headers });
  }
  try {
    const response = await upstream("POST");
    const parsed = repositoryRetrievalEvaluationSchema.safeParse(await response.json());
    if (!response.ok || !parsed.success) {
      return NextResponse.json(
        { detail: "Retrieval evaluation could not complete." },
        { status: response.ok ? 502 : response.status, headers },
      );
    }
    return NextResponse.json(parsed.data, { status: 201, headers });
  } catch {
    return NextResponse.json(
      { detail: "Retrieval evaluation service is unavailable." },
      { status: 503, headers },
    );
  }
}
