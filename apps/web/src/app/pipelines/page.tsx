import { UsageDagWorkspace } from "@/components/usage-dag-workspace";
import { UsageComputeWorkspace } from "@/components/usage-compute-workspace";
import { UsageFlinkWorkspace } from "@/components/usage-flink-workspace";
import { UsageBiWorkspace } from "@/components/usage-bi-workspace";
import { UsagePipelineCanvas } from "@/components/usage-pipeline-canvas";
export default function PipelinesPage() {
  return <div className="space-y-6"><header><h1 className="text-3xl font-semibold">Pipelines</h1><p className="mt-2 text-sm text-slate-500">Inspect bounded usage processing and orchestration evidence.</p></header><UsagePipelineCanvas/><UsageDagWorkspace/><UsageComputeWorkspace/><UsageFlinkWorkspace/><UsageBiWorkspace/></div>;
}
