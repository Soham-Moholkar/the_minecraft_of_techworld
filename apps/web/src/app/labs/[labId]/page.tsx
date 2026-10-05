import { notFound } from "next/navigation";
import { LabWorkspace } from "@/components/lab-workspace";
import { labs } from "@/data/learning";

export function generateStaticParams() {
  return Object.keys(labs).map((labId) => ({ labId }));
}

export default async function LabPage({ params }: { params: Promise<{ labId: string }> }) {
  const { labId } = await params;
  const lab = labs[labId as keyof typeof labs];
  if (!lab) notFound();
  return <LabWorkspace lab={lab}/>;
}
