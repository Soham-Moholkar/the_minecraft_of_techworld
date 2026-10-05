export default function Loading() {
  return <div aria-live="polite" className="space-y-4"><div className="h-9 w-72 animate-pulse rounded-lg bg-white/[.05]"/><div className="grid grid-cols-4 gap-3">{Array.from({length:4}).map((_,i)=><div key={i} className="h-32 animate-pulse rounded-xl border border-white/[.06] bg-white/[.025]"/>)}</div></div>;
}

