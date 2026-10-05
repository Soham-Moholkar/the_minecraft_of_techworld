const apiUrl = process.env.ATLAS_API_URL ?? process.env.NEXT_PUBLIC_ATLAS_API_URL ?? "http://localhost:8000";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const token = process.env.ATLAS_DEV_TOKEN ?? "atlas-local-development-token";
  const requestUrl = new URL(request.url);
  const once = requestUrl.searchParams.get("once") === "true" ? "?once=true" : "";
  const lastEventId = request.headers.get("last-event-id");
  try {
    // Forward the browser-managed cursor while keeping the service credential server-side.
    const upstream = await fetch(`${apiUrl}/v1/events/stream${once}`, {
      cache: "no-store",
      headers: {
        Authorization: `Bearer ${token}`,
        ...(lastEventId ? { "Last-Event-ID": lastEventId } : {}),
      },
    });
    return new Response(upstream.body, {
      status: upstream.status,
      headers: {
        "Content-Type": upstream.headers.get("content-type") ?? "text/event-stream",
        "Cache-Control": "no-cache, no-transform",
      },
    });
  } catch {
    return Response.json({ detail: "event stream unavailable" }, { status: 503 });
  }
}
