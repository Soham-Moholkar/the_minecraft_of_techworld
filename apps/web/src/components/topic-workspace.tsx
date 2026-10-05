"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { Bookmark, BookmarkCheck, CheckCircle2, Circle, FlaskConical, Save } from "lucide-react";
import type { Topic } from "@/data/learning";
import { completionPercent } from "@/lib/learning";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { CodeBlock } from "@/components/code-block";

type SavedTopic = { completed: string[]; bookmarked: boolean; note: string };

export function TopicWorkspace({ topic }: { topic: Topic }) {
  const [completed, setCompleted] = useState<string[]>([]);
  const [bookmarked, setBookmarked] = useState(false);
  const [note, setNote] = useState("");
  const [savedNotice, setSavedNotice] = useState(false);
  const hydrated = useRef(false);
  const storageKey = `atlas-topic:${topic.slug}`;

  useEffect(() => {
    // Learning state is intentionally browser-local until user accounts gain sync APIs.
    queueMicrotask(() => {
      const raw = localStorage.getItem(storageKey);
      if (raw) {
        try {
          const saved = JSON.parse(raw) as SavedTopic;
          setCompleted(saved.completed ?? []);
          setBookmarked(Boolean(saved.bookmarked));
          setNote(saved.note ?? "");
        } catch {
          localStorage.removeItem(storageKey);
        }
      }
      hydrated.current = true;
    });
  }, [storageKey]);

  function persist(next: SavedTopic) {
    localStorage.setItem(storageKey, JSON.stringify(next));
  }

  function toggleSection(sectionId: string) {
    const next = completed.includes(sectionId)
      ? completed.filter((id) => id !== sectionId)
      : [...completed, sectionId];
    setCompleted(next);
    persist({ completed: next, bookmarked, note });
  }

  function toggleBookmark() {
    const next = !bookmarked;
    setBookmarked(next);
    persist({ completed, bookmarked: next, note });
  }

  function saveNote() {
    persist({ completed, bookmarked, note });
    setSavedNotice(true);
    window.setTimeout(() => setSavedNotice(false), 1400);
  }

  const percentage = completionPercent(topic.sections.length, completed.length);

  return <div className="space-y-5">
    <section className="flex flex-col justify-between gap-4 border-b border-white/[.07] pb-6 md:flex-row md:items-end">
      <div><div className="flex flex-wrap items-center gap-2"><Badge tone="info">{topic.domain}</Badge><Badge>{topic.level}</Badge></div><h1 className="mt-3 text-3xl font-semibold">{topic.title}</h1><p className="mt-2 max-w-3xl text-sm leading-relaxed text-slate-500">{topic.summary}</p></div>
      <Button variant="secondary" onClick={toggleBookmark}>{bookmarked ? <BookmarkCheck size={15}/> : <Bookmark size={15}/>} {bookmarked ? "Bookmarked" : "Bookmark"}</Button>
    </section>
    <div className="grid gap-5 xl:grid-cols-[1fr_300px]">
      <div className="space-y-4">{topic.sections.map((section, index) => {
        const done = completed.includes(section.id);
        return <Card key={section.id} className="overflow-hidden"><div className="flex items-start gap-3 border-b border-white/[.07] p-5"><button onClick={() => toggleSection(section.id)} aria-label={`${done ? "Mark incomplete" : "Mark complete"}: ${section.title}`} className={done ? "text-emerald-300" : "text-slate-600"}>{done ? <CheckCircle2 size={19}/> : <Circle size={19}/>}</button><div><div className="text-[9px] font-bold uppercase tracking-[.16em] text-slate-600">Section {index + 1}</div><h2 className="mt-1 text-base font-semibold">{section.title}</h2></div></div><div className="space-y-4 p-5"><p className="text-sm leading-7 text-slate-400">{section.explanation}</p>{section.code && <CodeBlock code={section.code} language={section.language}/>}</div></Card>;
      })}</div>
      <aside className="space-y-4">
        <Card className="p-5"><div className="flex items-center justify-between"><h2 className="text-sm font-semibold">Your progress</h2><span className="text-xl font-semibold text-cyan-300">{percentage}%</span></div><div className="mt-4 h-2 overflow-hidden rounded-full bg-white/[.06]"><div className="h-full rounded-full bg-cyan-300 transition-[width]" style={{ width: `${percentage}%` }}/></div><p className="mt-3 text-[10px] text-slate-500">{completed.length} of {topic.sections.length} sections complete. Saved in this browser.</p></Card>
        <Card className="p-5"><div className="flex items-center gap-2"><FlaskConical size={15} className="text-cyan-300"/><h2 className="text-sm font-semibold">Practice lab</h2></div><p className="mt-2 text-[10px] leading-relaxed text-slate-500">Use the controlled, resettable environment associated with this topic.</p><Link href={`/labs/${topic.labId}`} className="mt-4 inline-flex text-xs font-semibold text-cyan-300">Open lab workspace →</Link></Card>
        <Card className="p-5"><label htmlFor="topic-note" className="text-sm font-semibold">Private note</label><textarea id="topic-note" value={note} onChange={(event) => setNote(event.target.value)} rows={7} className="mt-3 w-full resize-none rounded-lg border border-white/[.09] bg-white/[.035] p-3 text-xs leading-relaxed outline-none focus:border-cyan-300/40" placeholder="Capture a decision, question, or follow-up…"/><Button onClick={saveNote} className="mt-3 w-full"><Save size={14}/>{savedNotice ? "Saved" : "Save note"}</Button></Card>
        <p className="break-all px-1 font-mono text-[9px] text-slate-600">Source: {topic.sourcePath}</p>
      </aside>
    </div>
  </div>;
}
