import { notFound } from "next/navigation";
import { TopicWorkspace } from "@/components/topic-workspace";
import { findTopic, topics } from "@/data/learning";

export function generateStaticParams() {
  return topics.map((topic) => ({ slug: topic.slug }));
}

export default async function TopicPage({ params }: { params: Promise<{ slug: string }> }) {
  const topic = findTopic((await params).slug);
  if (!topic) notFound();
  return <TopicWorkspace topic={topic}/>;
}
