"use client";
import { CircleAlert } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function ErrorPage({ reset }: { reset: () => void }) {
  return <div className="grid min-h-[60vh] place-items-center"><div className="max-w-md text-center"><CircleAlert className="mx-auto text-rose-300"/><h1 className="mt-4 text-xl font-semibold">This workspace could not load</h1><p className="mt-2 text-sm text-slate-500">The failure is isolated. Retry the view or inspect correlated service logs.</p><Button className="mt-5" onClick={reset}>Retry workspace</Button></div></div>;
}

