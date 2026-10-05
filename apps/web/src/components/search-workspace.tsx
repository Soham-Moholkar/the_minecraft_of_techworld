"use client";

import { FormEvent, useState } from "react";
import { FolderKanban, Search } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

type Result = { id: string; name: string; description: string; status: string };

export function SearchWorkspace() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Result[]>([]);
  const [state, setState] = useState<"idle" | "loading" | "done" | "error">("idle");

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (query.trim().length < 2) return;
    setState("loading");
    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(query.trim())}`);
      if (!response.ok) throw new Error("search failed");
      setResults(await response.json() as Result[]);
      setState("done");
    } catch {
      setState("error");
    }
  }

  return <div className="space-y-5"><form onSubmit={submit} className="flex gap-2"><label className="flex flex-1 items-center gap-3 rounded-xl border border-white/[.09] bg-white/[.035] px-4"><Search size={17} className="text-slate-500"/><span className="sr-only">Search projects</span><input value={query} onChange={(event)=>setQuery(event.target.value)} className="h-12 w-full bg-transparent text-sm outline-none placeholder:text-slate-600" placeholder="Search authoritative project metadata…" minLength={2} maxLength={120}/></label><Button disabled={state === "loading"}>{state === "loading" ? "Searching…" : "Search"}</Button></form>
    <Card className="overflow-hidden">{state === "idle" && <div className="p-10 text-center text-xs text-slate-500">Search begins with persisted projects; datasets, services, runs, and documentation join through provider adapters in later levels.</div>}{state === "error" && <div className="p-8 text-center text-xs text-rose-300">The search provider is unavailable. Check control-plane health and retry.</div>}{state === "done" && results.length === 0 && <div className="p-10 text-center text-xs text-slate-500">No authoritative results matched “{query}”.</div>}{results.map(result=><div key={result.id} className="flex items-center gap-4 border-b border-white/[.06] p-4 last:border-0"><div className="grid size-9 place-items-center rounded-lg bg-cyan-300/[.07] text-cyan-300"><FolderKanban size={16}/></div><div className="min-w-0 flex-1"><div className="text-xs font-semibold">{result.name}</div><div className="mt-1 truncate text-[10px] text-slate-500">{result.description}</div></div><Badge tone="success">{result.status}</Badge></div>)}</Card>
  </div>;
}

