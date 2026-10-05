"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import {
  Activity, Bot, Boxes, Bookmark, BookOpen, BrainCircuit, ClipboardCheck, Command,
  Database, FlaskConical, Gauge, Hexagon, Layers3, MoonStar, PanelLeft, Search,
  ShieldCheck, Waypoints, Workflow, X,
} from "lucide-react";
import { cn } from "@/lib/utils";

const operateNavigation = [
  { href: "/", label: "Overview", icon: Gauge },
  { href: "/search", label: "Global search", icon: Search },
  { href: "/projects", label: "Projects", icon: Workflow },
  { href: "/catalog", label: "Domain catalog", icon: Layers3 },
  { href: "/data", label: "Data estate", icon: Database },
  { href: "/datasets", label: "Datasets", icon: FlaskConical },
  { href: "/models", label: "Models", icon: BrainCircuit },
  { href: "/pipelines", label: "Pipelines", icon: Waypoints },
  { href: "/streaming", label: "Usage streaming", icon: Activity },
  { href: "/ai/repository", label: "Repository AI", icon: Bot },
  { href: "/infrastructure", label: "Infrastructure", icon: Boxes },
  { href: "/observability", label: "Observability", icon: Activity },
  { href: "/security", label: "Security", icon: ShieldCheck },
];

const learnNavigation = [
  { href: "/topics/control-plane-api-evolution", label: "Control-plane topic", icon: BookOpen },
  { href: "/topics/python-mastery", label: "Python mastery", icon: Bookmark },
  { href: "/labs/api-foundation", label: "Lab workspace", icon: FlaskConical },
  { href: "/developer/technologies", label: "Engineering", icon: Command },
  { href: "/tests", label: "Test center", icon: ClipboardCheck },
];

const commands = [...operateNavigation, ...learnNavigation];

function isActive(pathname: string, href: string) {
  return pathname === href || (href !== "/" && pathname.startsWith(`${href}/`));
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [query, setQuery] = useState("");

  useEffect(() => {
    const savedTheme = localStorage.getItem("atlas-theme") === "light" ? "light" : "dark";
    document.documentElement.dataset.theme = savedTheme;
    const onKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setPaletteOpen((current) => !current);
      }
      if (event.key === "Escape") setPaletteOpen(false);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const filteredCommands = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return normalized
      ? commands.filter((item) => item.label.toLowerCase().includes(normalized))
      : commands;
  }, [query]);

  function navigate(href: string) {
    setPaletteOpen(false);
    setMobileOpen(false);
    setQuery("");
    router.push(href);
  }

  function toggleTheme() {
    const nextTheme = document.documentElement.dataset.theme === "light" ? "dark" : "light";
    document.documentElement.dataset.theme = nextTheme;
    localStorage.setItem("atlas-theme", nextTheme);
  }

  const navLink = ({ href, label, icon: Icon }: (typeof commands)[number]) => (
    <Link
      key={href}
      href={href}
      aria-current={isActive(pathname, href) ? "page" : undefined}
      onClick={() => setMobileOpen(false)}
      className={cn(
        "mb-0.5 flex items-center gap-3 rounded-lg px-3 py-2 text-xs transition",
        isActive(pathname, href)
          ? "bg-cyan-300/[.09] text-cyan-200"
          : "text-slate-400 hover:bg-white/[.04] hover:text-slate-100",
      )}
    >
      <Icon size={16}/><span>{label}</span>
      {isActive(pathname, href) && <span className="ml-auto size-1.5 rounded-full bg-cyan-300"/>}
    </Link>
  );

  return (
    <div className="atlas-shell min-h-screen bg-[#071018] text-slate-100">
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:bg-cyan-300 focus:p-3 focus:text-slate-950">Skip to content</a>
      {mobileOpen && <button aria-label="Close navigation overlay" className="fixed inset-0 z-20 bg-slate-950/70 lg:hidden" onClick={() => setMobileOpen(false)}/>} 
      <aside className={cn("atlas-sidebar fixed inset-y-0 left-0 z-30 flex w-[244px] flex-col border-r border-white/[.07] bg-[#08131d] transition-transform lg:visible lg:translate-x-0", mobileOpen ? "visible translate-x-0" : "invisible -translate-x-full")}>
        <div className="flex h-16 items-center gap-3 border-b border-white/[.07] px-5">
          <div className="grid size-8 place-items-center rounded-lg bg-cyan-300 text-slate-950 shadow-[0_0_24px_rgba(103,232,249,.25)]"><Hexagon size={18} strokeWidth={2.4}/></div>
          <div><div className="text-sm font-black tracking-[.22em]">ATLAS</div><div className="text-[10px] uppercase tracking-[.16em] text-slate-500">Control plane</div></div>
          <button className="ml-auto rounded-md p-1 text-slate-400 lg:hidden" aria-label="Close navigation" onClick={() => setMobileOpen(false)}><X size={18}/></button>
        </div>
        <div className="mx-3 mt-4 flex items-center gap-3 rounded-lg border border-white/[.08] bg-white/[.035] px-3 py-2.5 text-left" aria-label="Development workspace">
          <div className="grid size-7 place-items-center rounded-md bg-indigo-400/15 text-xs font-bold text-indigo-300">NS</div>
          <div className="min-w-0 flex-1"><div className="truncate text-xs font-semibold">Northstar Systems</div><div className="text-[10px] text-slate-500">Development workspace</div></div>
        </div>
        <nav aria-label="Primary navigation" className="mt-5 flex-1 overflow-y-auto px-3">
          <div className="mb-2 px-3 text-[9px] font-bold uppercase tracking-[.2em] text-slate-600">Operate</div>
          {operateNavigation.map(navLink)}
          <div className="mb-2 mt-6 px-3 text-[9px] font-bold uppercase tracking-[.2em] text-slate-600">Learn & build</div>
          {learnNavigation.map(navLink)}
        </nav>
        <div className="border-t border-white/[.07] p-3">
          <button onClick={toggleTheme} className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-xs text-slate-400 hover:bg-white/[.04]"><MoonStar size={16}/>Toggle color mode</button>
        </div>
      </aside>
      <div className="lg:pl-[244px]">
        <header className="atlas-header sticky top-0 z-20 flex h-16 items-center gap-4 border-b border-white/[.07] bg-[#071018]/90 px-4 backdrop-blur-xl md:px-7">
          <button className="rounded-md p-2 text-slate-400 lg:hidden" aria-label="Open navigation" onClick={() => setMobileOpen(true)}><PanelLeft size={20}/></button>
          <button onClick={() => setPaletteOpen(true)} className="flex max-w-[460px] flex-1 items-center gap-3 rounded-lg border border-white/[.08] bg-white/[.035] px-3 py-2 text-left text-xs text-slate-500"><Search size={15}/><span className="min-w-0 flex-1 truncate">Search and run a command…</span><kbd className="rounded border border-white/10 px-1.5 py-0.5 text-[9px]">⌘ K</kbd></button>
          <div className="ml-auto flex items-center gap-3"><div className="hidden items-center gap-2 text-[10px] text-slate-500 sm:flex"><Link href="/observability" className="text-cyan-300">Service diagnostics</Link></div><div className="grid size-8 place-items-center rounded-full bg-gradient-to-br from-indigo-300 to-cyan-300 text-[10px] font-black text-slate-950">LD</div></div>
        </header>
        <main id="main" className="mx-auto max-w-[1500px] p-4 md:p-7">{children}</main>
      </div>
      {paletteOpen && <div className="fixed inset-0 z-50 grid place-items-start bg-slate-950/75 px-4 pt-[12vh] backdrop-blur-sm" role="presentation" onMouseDown={() => setPaletteOpen(false)}>
        <section role="dialog" aria-modal="true" aria-label="Command palette" className="w-full max-w-xl overflow-hidden rounded-xl border border-white/10 bg-[#0b1722] shadow-2xl" onMouseDown={(event) => event.stopPropagation()}>
          <label htmlFor="command-query" className="sr-only">Search commands</label>
          <div className="flex items-center gap-3 border-b border-white/[.08] px-4"><Search size={17} className="text-cyan-300"/><input autoFocus id="command-query" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Navigate to a domain, topic, lab, or tool…" className="h-14 flex-1 bg-transparent text-sm outline-none placeholder:text-slate-600"/><kbd className="text-[10px] text-slate-600">ESC</kbd></div>
          <div className="max-h-[420px] overflow-y-auto p-2">{filteredCommands.length === 0 ? <div className="p-8 text-center text-xs text-slate-500">No matching command.</div> : filteredCommands.map(({ href, label, icon: Icon }) => <button key={href} onClick={() => navigate(href)} className="flex w-full items-center gap-3 rounded-lg px-3 py-3 text-left text-xs text-slate-300 hover:bg-white/[.05]"><Icon size={16} className="text-cyan-300"/><span className="flex-1">{label}</span><span className="font-mono text-[9px] text-slate-600">{href}</span></button>)}</div>
        </section>
      </div>}
    </div>
  );
}
