import { NextResponse } from "next/server";
import { z } from "zod";
import { PROJECT_QUERY_NAME, projectStatusSchema, queryPlanSchema } from "@/lib/query-plan";

const apiUrl =
  process.env.ATLAS_API_URL ??
  process.env.NEXT_PUBLIC_ATLAS_API_URL ??
  "http://localhost:8000";

const querySchema = z.object({
  status: projectStatusSchema.default("active"),
});

export async function GET(request: Request) {
  const url = new URL(request.url);
  const parsedQuery = querySchema.safeParse({
    status: url.searchParams.get("status") ?? undefined,
  });
  if (!parsedQuery.success) {
    return NextResponse.json({ detail: "invalid project status filter" }, { status: 400 });
  }

  try {
    // The allowlisted query name is fixed here rather than accepted from the
    // browser. That keeps this product surface from becoming an arbitrary SQL
    // proxy while still letting the status value travel as a bound parameter.
    const upstreamQuery = new URLSearchParams({
      query_name: PROJECT_QUERY_NAME,
      status: parsedQuery.data.status,
    });
    const token = process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token";
    const upstream = await fetch(`${apiUrl}/v1/database/query-plan?${upstreamQuery}`, {
      cache: "no-store",
      headers: { Authorization: `Bearer ${token}` },
      signal: AbortSignal.timeout(3000),
    });
    const payload: unknown = await upstream.json().catch(() => ({
      detail: "query-plan service returned an unreadable response",
    }));
    if (!upstream.ok) {
      return NextResponse.json(payload, { status: upstream.status });
    }

    // Treat the upstream API as a trust boundary. Runtime validation prevents a
    // backend drift from reaching a deeply nested operational visualization.
    const parsedPlan = queryPlanSchema.safeParse(payload);
    if (!parsedPlan.success) {
      return NextResponse.json({ detail: "invalid query-plan response" }, { status: 502 });
    }
    return NextResponse.json(parsedPlan.data, {
      headers: { "Cache-Control": "no-store" },
    });
  } catch {
    return NextResponse.json({ detail: "query-plan service unavailable" }, { status: 503 });
  }
}
