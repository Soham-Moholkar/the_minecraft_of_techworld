"use client";

import { useState } from "react";
import { Check, Copy } from "lucide-react";

export function CodeBlock({ code, language = "text" }: { code: string; language?: string }) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1200);
  }

  return <div className="overflow-hidden rounded-xl border border-white/[.09] bg-[#050c12]">
    <div className="flex items-center justify-between border-b border-white/[.07] px-4 py-2"><span className="font-mono text-[9px] uppercase tracking-[.16em] text-slate-500">{language}</span><button onClick={() => void copy()} className="flex items-center gap-1.5 rounded px-2 py-1 text-[10px] text-slate-400 hover:bg-white/[.06]" aria-label="Copy code">{copied ? <Check size={12}/> : <Copy size={12}/>} {copied ? "Copied" : "Copy"}</button></div>
    <pre className="overflow-x-auto p-4 text-xs leading-6 text-cyan-100"><code>{code}</code></pre>
  </div>;
}
