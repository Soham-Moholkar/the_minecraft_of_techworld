import { cva, type VariantProps } from "class-variance-authority";
import type { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-lg text-sm font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-cyan-300 px-4 py-2 text-slate-950 hover:bg-cyan-200",
        secondary: "border border-white/10 bg-white/[.05] px-4 py-2 text-slate-100 hover:bg-white/10",
        ghost: "px-3 py-2 text-slate-400 hover:bg-white/[.06] hover:text-white",
      },
    },
    defaultVariants: { variant: "default" },
  },
);

export function Button({ className, variant, ...props }: ButtonHTMLAttributes<HTMLButtonElement> & VariantProps<typeof buttonVariants>) {
  return <button className={cn(buttonVariants({ variant }), className)} {...props} />;
}

