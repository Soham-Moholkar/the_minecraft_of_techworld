import { DomainWorkspace } from "@/components/domain-workspace";
import { DatabaseProviderComparisonViewer } from "@/components/database-provider-comparison";
import { DatabaseOperationsWorkbench } from "@/components/database-operations-workbench";
import { DocumentProjectionViewer } from "@/components/document-projection-viewer";
import { ExplainPlanViewer } from "@/components/explain-plan-viewer";
import { IsolationVisualizer } from "@/components/isolation-visualizer";
import { LockActivityViewer } from "@/components/lock-activity-viewer";
import { operationalDomains } from "@/data/operations";

export default function DataEstatePage() {
  return (
    <div className="space-y-6">
      <DomainWorkspace domain={operationalDomains.data} />
      <DatabaseProviderComparisonViewer />
      <DatabaseOperationsWorkbench />
      <DocumentProjectionViewer />
      <ExplainPlanViewer />
      <IsolationVisualizer />
      <LockActivityViewer />
    </div>
  );
}
