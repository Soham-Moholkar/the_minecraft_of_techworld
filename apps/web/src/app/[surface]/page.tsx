import { notFound } from "next/navigation";
import { DomainWorkspace } from "@/components/domain-workspace";
import { operationalDomains } from "@/data/operations";

export default async function SurfacePage({ params }: { params: Promise<{ surface: string }> }) {
  const { surface } = await params;
  const domain = operationalDomains[surface];
  if (!domain || surface === "security") notFound();
  return <DomainWorkspace domain={domain}/>;
}
