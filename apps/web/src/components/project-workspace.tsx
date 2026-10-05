"use client";

import { type FormEvent, useEffect, useState } from "react";
import { CalendarClock, FilePlus2, FolderKanban, MessageSquareText, Plus, RefreshCw } from "lucide-react";
import { z } from "zod";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type Project = {
  id: string;
  organization_id: string;
  slug: string;
  name: string;
  description: string;
  status: string;
  created_at: string;
};
type Note = { id: string; author: string; body: string; created_at: string };
type Identity = { subject: string; organization_id: string; organization_slug: string; roles: string[] };

const fieldClass = "w-full rounded-lg border border-white/[.09] bg-white/[.035] px-3 py-2.5 text-xs text-slate-100 outline-none placeholder:text-slate-600 focus:border-cyan-300/40 focus:ring-2 focus:ring-cyan-300/10";
const projectInput = z.object({
  organization_id: z.string().uuid(),
  slug: z.string().min(2).max(64).regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/),
  name: z.string().min(2).max(160),
  description: z.string().max(2000),
});
const noteInput = z.object({ author: z.string().min(1).max(160), body: z.string().min(1).max(4000) });

async function fetchWorkspace(): Promise<{ projects: Project[]; identity: Identity }> {
  const [projectsResponse, identityResponse] = await Promise.all([
    fetch("/api/projects"),
    fetch("/api/session"),
  ]);
  if (!projectsResponse.ok || !identityResponse.ok) throw new Error("workspace unavailable");
  const page = await projectsResponse.json() as { items: Project[] };
  return { projects: page.items, identity: await identityResponse.json() as Identity };
}

export function ProjectWorkspace() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [identity, setIdentity] = useState<Identity | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [creating, setCreating] = useState(false);
  const [notesLoading, setNotesLoading] = useState(true);
  const [savingNote, setSavingNote] = useState(false);

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      const workspace = await fetchWorkspace();
      setProjects(workspace.projects);
      setIdentity(workspace.identity);
      setSelectedId((current) => current ?? workspace.projects[0]?.id ?? null);
    } catch {
      setError("The control plane or identity provider is unavailable.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let active = true;
    void fetchWorkspace()
      .then((workspace) => {
        if (!active) return;
        setProjects(workspace.projects);
        setIdentity(workspace.identity);
        setSelectedId(workspace.projects[0]?.id ?? null);
      })
      .catch(() => { if (active) setError("The control plane or identity provider is unavailable."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);
  useEffect(() => {
    if (!selectedId) return;
    let active = true;
    void fetch(`/api/projects/${encodeURIComponent(selectedId)}/notes`)
      .then(async (response) => {
        if (!response.ok) throw new Error("notes unavailable");
        const nextNotes = await response.json() as Note[];
        if (active) setNotes(nextNotes);
      })
      .catch(() => { if (active) setError("Project notes could not be loaded."); })
      .finally(() => { if (active) setNotesLoading(false); });
    return () => { active = false; };
  }, [selectedId]);

  function selectProject(projectId: string) {
    if (projectId === selectedId) return;
    setNotes([]);
    setNotesLoading(true);
    setSelectedId(projectId);
  }

  async function createProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!identity) return;
    const form = event.currentTarget;
    const data = new FormData(form);
    const parsed = projectInput.safeParse({
      organization_id: identity.organization_id,
      slug: data.get("slug"),
      name: data.get("name"),
      description: data.get("description"),
    });
    if (!parsed.success) {
      setError("Check the project name, stable lowercase slug, and description length.");
      return;
    }
    const optimisticId = `optimistic-${crypto.randomUUID()}`;
    const optimisticProject: Project = {
      ...parsed.data,
      id: optimisticId,
      status: "creating",
      created_at: new Date().toISOString(),
    };
    // Render immediately, then replace or remove this client-only id after the API settles.
    setProjects((current) => [optimisticProject, ...current]);
    setCreating(true);
    setError(null);
    try {
      const response = await fetch("/api/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(parsed.data),
      });
      if (response.ok) {
        const project = await response.json() as Project;
        setProjects((current) => current.map((item) => item.id === optimisticId ? project : item));
        setNotes([]);
        setNotesLoading(true);
        setSelectedId(project.id);
        setShowCreate(false);
        form.reset();
      } else {
        setProjects((current) => current.filter((item) => item.id !== optimisticId));
        const problem = await response.json() as { detail?: string };
        setError(problem.detail ?? "Project could not be created.");
      }
    } catch {
      setProjects((current) => current.filter((item) => item.id !== optimisticId));
      setError("Project could not be created because the control plane is unavailable.");
    } finally {
      setCreating(false);
    }
  }

  async function addNote(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedId) return;
    const form = event.currentTarget;
    const data = new FormData(form);
    const parsed = noteInput.safeParse({
      author: identity?.subject ?? "local-developer",
      body: data.get("body"),
    });
    if (!parsed.success) {
      setError("The note must contain between 1 and 4,000 characters.");
      return;
    }
    const optimisticId = `optimistic-${crypto.randomUUID()}`;
    const optimisticNote: Note = {
      id: optimisticId,
      author: parsed.data.author,
      body: parsed.data.body,
      created_at: new Date().toISOString(),
    };
    // Keeping rollback local makes a failed note impossible to masquerade as persisted data.
    setNotes((current) => [optimisticNote, ...current]);
    setSavingNote(true);
    setError(null);
    try {
      const response = await fetch(`/api/projects/${encodeURIComponent(selectedId)}/notes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(parsed.data),
      });
      if (response.ok) {
        const note = await response.json() as Note;
        setNotes((current) => current.map((item) => item.id === optimisticId ? note : item));
        form.reset();
      } else {
        setNotes((current) => current.filter((item) => item.id !== optimisticId));
        setError("Note could not be saved.");
      }
    } catch {
      setNotes((current) => current.filter((item) => item.id !== optimisticId));
      setError("Note could not be saved because the control plane is unavailable.");
    } finally {
      setSavingNote(false);
    }
  }

  const selected = projects.find((project) => project.id === selectedId);
  return <div className="space-y-4">
    <div className="flex flex-wrap items-center justify-between gap-3"><div className="flex items-center gap-2">{identity && <><Badge tone="info">{identity.organization_slug}</Badge><span className="text-[10px] text-slate-500">{identity.subject} · {identity.roles.join(", ")}</span></>}</div><div className="flex gap-2"><Button variant="secondary" onClick={() => void refresh()}><RefreshCw size={14}/>Refresh</Button><Button onClick={() => setShowCreate((current) => !current)}><Plus size={14}/>New project</Button></div></div>
    {error && <div role="alert" className="rounded-lg border border-rose-400/20 bg-rose-400/[.06] px-4 py-3 text-xs text-rose-200">{error}</div>}
    {showCreate && <Card className="p-5"><form onSubmit={createProject} className="grid gap-3 md:grid-cols-2"><div><label htmlFor="project-name" className="mb-1.5 block text-[10px] font-semibold text-slate-400">Project name</label><input id="project-name" name="name" required minLength={2} maxLength={160} className={fieldClass} placeholder="Risk intelligence"/></div><div><label htmlFor="project-slug" className="mb-1.5 block text-[10px] font-semibold text-slate-400">Stable slug</label><input id="project-slug" name="slug" required minLength={2} maxLength={64} pattern="[a-z0-9]+(?:-[a-z0-9]+)*" className={fieldClass} placeholder="risk-intelligence"/></div><div className="md:col-span-2"><label htmlFor="project-description" className="mb-1.5 block text-[10px] font-semibold text-slate-400">Description</label><textarea id="project-description" name="description" maxLength={2000} rows={3} className={fieldClass} placeholder="What this workspace owns and operates."/></div><div className="md:col-span-2 flex justify-end gap-2"><Button type="button" variant="ghost" onClick={() => setShowCreate(false)}>Cancel</Button><Button disabled={creating} type="submit">{creating ? "Creating…" : "Create project"}</Button></div></form></Card>}
    <div className="grid min-h-[560px] gap-4 lg:grid-cols-[360px_1fr]">
      <Card className="overflow-hidden"><div className="border-b border-white/[.07] p-4"><h2 className="text-sm font-semibold">Portfolio</h2><p className="mt-1 text-[10px] text-slate-500">{projects.length} tenant-scoped workspaces</p></div>{loading ? <div className="p-8 text-center text-xs text-slate-500">Loading authoritative projects…</div> : projects.length === 0 ? <div className="p-8 text-center"><FilePlus2 className="mx-auto text-slate-600"/><div className="mt-3 text-xs text-slate-500">Create the first workspace.</div></div> : <div>{projects.map((project)=><button key={project.id} onClick={()=>selectProject(project.id)} className={cn("flex w-full items-start gap-3 border-b border-white/[.06] p-4 text-left transition last:border-0", selectedId === project.id ? "bg-cyan-300/[.07]" : "hover:bg-white/[.025]")}><div className="mt-0.5 grid size-8 place-items-center rounded-lg bg-indigo-400/[.08] text-indigo-300"><FolderKanban size={15}/></div><div className="min-w-0 flex-1"><div className="truncate text-xs font-semibold">{project.name}</div><div className="mt-1 truncate text-[10px] text-slate-500">{project.description || "No description"}</div><div className="mt-2 font-mono text-[9px] text-slate-600">{project.slug}</div></div><span className="mt-1 size-1.5 rounded-full bg-emerald-400"/></button>)}</div>}</Card>
      <Card className="overflow-hidden">{selected ? <><div className="border-b border-white/[.07] p-5"><div className="flex items-start justify-between gap-4"><div><div className="flex items-center gap-2"><h2 className="text-lg font-semibold">{selected.name}</h2><Badge tone="success">{selected.status}</Badge></div><p className="mt-2 max-w-2xl text-xs leading-relaxed text-slate-500">{selected.description || "No description has been supplied."}</p></div><div className="flex items-center gap-1 text-[9px] text-slate-600"><CalendarClock size={12}/>{new Date(selected.created_at).toLocaleDateString()}</div></div></div><div className="grid gap-5 p-5 xl:grid-cols-[1fr_300px]"><div><div className="mb-3 flex items-center gap-2"><MessageSquareText size={15} className="text-cyan-300"/><h3 className="text-xs font-semibold">Engineering notes</h3></div>{notesLoading ? <div className="rounded-lg border border-dashed border-white/[.09] p-8 text-center text-[10px] text-slate-500">Loading project notes…</div> : notes.length === 0 ? <div className="rounded-lg border border-dashed border-white/[.09] p-8 text-center text-[10px] text-slate-500">No notes yet. Record a decision or operational observation.</div> : <div className="space-y-2">{notes.map(note=><div key={note.id} className="rounded-lg border border-white/[.07] bg-white/[.02] p-3"><div className="flex items-center justify-between"><span className="text-[10px] font-semibold text-cyan-200">{note.author}</span><time className="text-[9px] text-slate-600">{new Date(note.created_at).toLocaleString()}</time></div><p className="mt-2 text-xs leading-relaxed text-slate-300">{note.body}</p></div>)}</div>}</div><form onSubmit={addNote} className="rounded-lg border border-white/[.07] bg-white/[.02] p-4"><label htmlFor="note-body" className="text-[10px] font-semibold text-slate-400">Add an engineering note</label><textarea id="note-body" name="body" required minLength={1} maxLength={4000} rows={6} className={`${fieldClass} mt-2 resize-none`} placeholder="Decision, risk, incident context, or follow-up…"/><Button className="mt-3 w-full" disabled={savingNote || notesLoading} type="submit">{savingNote ? "Saving…" : "Save note"}</Button><p className="mt-2 text-[9px] leading-relaxed text-slate-600">The mutation and its audit event commit atomically.</p></form></div></> : <div className="grid h-full place-items-center p-10 text-center text-xs text-slate-500">Select a project to inspect its workspace.</div>}</Card>
    </div>
  </div>;
}
