import { RepositoryAIWorkspace } from "@/components/repository-ai-workspace";
import { RepositoryPatchWorkspace } from "@/components/repository-patch-workspace";
import { RepositoryMCPExplorer } from "@/components/repository-mcp-explorer";
import { AgentMemoryWorkspace } from "@/components/agent-memory-workspace";

export default function RepositoryAIPage() {
  return <><RepositoryAIWorkspace /><RepositoryPatchWorkspace /><RepositoryMCPExplorer /><AgentMemoryWorkspace /></>;
}
