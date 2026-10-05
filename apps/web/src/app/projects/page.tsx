import { ProjectWorkspace } from "@/components/project-workspace";

export default function ProjectsPage() {
  return <div><div className="mb-6"><div className="text-[10px] font-bold uppercase tracking-[.18em] text-cyan-300">Workspaces</div><h1 className="mt-2 text-3xl font-semibold">Projects</h1><p className="mt-2 text-sm text-slate-500">Create and annotate tenant-scoped workspaces through the authenticated control plane.</p></div><ProjectWorkspace/></div>;
}
