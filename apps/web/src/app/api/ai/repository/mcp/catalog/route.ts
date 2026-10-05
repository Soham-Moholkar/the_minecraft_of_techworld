import { NextResponse } from "next/server";
import { repositoryMCPCatalogSchema } from "@/lib/repository-mcp";

const headers = { "Cache-Control": "no-store" };

/** Fixed upstream and GET only: browser-supplied URLs/arguments cannot dispatch tools. */
export async function GET() {
  try {
    const response = await fetch(
      `${process.env.ATLAS_API_URL ?? "http://localhost:8000"}/v1/ai/repository/mcp/catalog`,
      {
        cache: "no-store",
        headers: { Authorization: `Bearer ${process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token"}` },
        signal: AbortSignal.timeout(10_000),
      },
    );
    if (!response.ok) throw new Error("catalog unavailable");
    const parsed = repositoryMCPCatalogSchema.safeParse(await response.json());
    if (!parsed.success) {
      return NextResponse.json({ detail: "Invalid MCP catalog contract." }, { status: 502, headers });
    }
    return NextResponse.json(parsed.data, { headers });
  } catch {
    // Do not disclose upstream bodies, tokens, paths or transport errors to clients.
    return NextResponse.json({ detail: "Local MCP catalog is unavailable." }, { status: 503, headers });
  }
}
