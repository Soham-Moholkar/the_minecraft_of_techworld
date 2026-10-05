import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type Tone = "neutral" | "success" | "warning" | "info" | "danger";
const tones: Record<Tone, string> = {
  neutral: "border-white/10 bg-white/[.05] text-slate-300",
  success: "border-emerald-400/20 bg-emerald-400/10 text-emerald-300",
  warning: "border-amber-400/20 bg-amber-400/10 text-amber-300",
  info: "border-cyan-400/20 bg-cyan-400/10 text-cyan-300",
  danger: "border-rose-400/20 bg-rose-400/10 text-rose-300",
};

export function Badge({ tone = "neutral", className, ...props }: HTMLAttributes<HTMLSpanElement> & { tone?: Tone }) {
  return <span className={cn("inline-flex rounded-md border px-2 py-1 text-[10px] font-bold uppercase tracking-[.14em]", tones[tone], className)} {...props} />;
}

