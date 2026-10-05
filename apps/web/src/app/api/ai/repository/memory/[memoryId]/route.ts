import { NextResponse } from "next/server";
import { z } from "zod";
import { memoryProxy } from "@/lib/agent-memory-proxy";
import { memoryDeleteSchema, memoryRemovalSchema } from "@/lib/agent-memory";

export async function DELETE(request: Request, { params }: { params: Promise<{ memoryId: string }> }) {
  const { memoryId } = await params;
  // Validate before interpolation; identifiers cannot select arbitrary upstream paths.
  if (!z.string().uuid().safeParse(memoryId).success) {
    return NextResponse.json({ detail: "Invalid memory identifier." }, {
      status: 400, headers: { "Cache-Control": "no-store" },
    });
  }
  return memoryProxy(`/${memoryId}`, memoryRemovalSchema, request, memoryDeleteSchema);
}
