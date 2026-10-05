import { NextResponse } from "next/server";
import { z } from "zod";
import { controlPlaneProxy } from "@/lib/control-plane-proxy";
import { noteInput, noteSchema } from "@/lib/control-plane";
type Context = { params: Promise<{ projectId: string }> };
async function notes(context: Context, request?: Request) {
  const { projectId } = await context.params;
  if (!z.uuid().safeParse(projectId).success) return NextResponse.json({ detail: "Invalid project identifier." }, { status: 400, headers: { "Cache-Control": "no-store" } });
  return controlPlaneProxy(`/v1/projects/${projectId}/notes`, request ? noteSchema : z.array(noteSchema), request, noteInput);
}
export async function GET(_request: Request, context: Context) { return notes(context); }
export async function POST(request: Request, context: Context) { return notes(context, request); }
