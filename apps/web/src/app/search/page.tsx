import { SearchWorkspace } from "@/components/search-workspace";

export default function SearchPage() {
  return <div className="space-y-6"><section className="border-b border-white/[.07] pb-6"><div className="text-[10px] font-bold uppercase tracking-[.18em] text-cyan-300">Global discovery</div><h1 className="mt-2 text-3xl font-semibold">Search ATLAS</h1><p className="mt-2 text-sm text-slate-500">One bounded query contract, expanding through interchangeable search providers.</p></section><SearchWorkspace/></div>;
}

