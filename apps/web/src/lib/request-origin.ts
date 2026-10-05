/** Explicit public origins also work when a reverse proxy rewrites request.url. */
export function allowsMutation(request: Request): boolean {
  const allowed = new Set((process.env.ATLAS_ALLOWED_ORIGINS ?? "http://localhost:3000")
    .split(",").map((value) => value.trim()).filter(Boolean));
  const origin = request.headers.get("origin");
  return request.headers.get("sec-fetch-site") !== "cross-site"
    && (origin === null || allowed.has(origin));
}
