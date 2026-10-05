import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { InfrastructurePlanWorkspace } from "./infrastructure-plan-workspace";
const receipt = { schema_version:1, engine:"opentofu",engine_version:"1.13.0",scope:"local-metadata",state_baseline:"empty-disposable-fixture",created:1,changed:0,destroyed:0,configuration_digest:"a".repeat(64),plan_digest:"b".repeat(64),input:{namespace:"atlas-dev",manifest_digest:"c".repeat(64),budget:{cpu_request_millicores:350,cpu_limit_millicores:2000,memory_request_mib:768,memory_limit_mib:1536,storage_mib:1024,replicas:2}},finished_at:"2026-10-04T00:00:00Z" };
const data = {checked_at:"2026-10-04T00:01:00Z",source_current:true,receipt};
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
it("reports actual plan lineage and local-only scope without an apply action", async () => {
  vi.stubGlobal("fetch",vi.fn().mockResolvedValue(new Response(JSON.stringify(data))));
  render(<InfrastructurePlanWorkspace/>);
  expect(await screen.findByText("Matches current deployment source")).toBeVisible();
  expect(screen.getByText(/provisions no cluster or cloud resource/)).toBeVisible();
  expect(screen.getAllByRole("button")).toHaveLength(1);
});
it("distinguishes an older receipt from an absent one and clears a failed refresh", async () => {
  const fetch = vi.fn().mockResolvedValueOnce(new Response(JSON.stringify({...data,source_current:false}))).mockResolvedValueOnce(new Response(JSON.stringify({...data,source_current:null,receipt:null}))).mockResolvedValueOnce(new Response("{}",{status:503}));
  vi.stubGlobal("fetch",fetch); render(<InfrastructurePlanWorkspace/>);
  expect(await screen.findByText("Deployment source has changed since this plan")).toBeVisible();
  fireEvent.click(screen.getByRole("button",{name:"Refresh local plan"}));
  expect(await screen.findByText(/No local plan receipt recorded/)).toBeVisible();
  fireEvent.click(screen.getByRole("button",{name:"Refresh local plan"}));
  expect(await screen.findByRole("alert")).toHaveTextContent("unavailable or disabled");
  expect(screen.queryByText(/No local plan receipt recorded/)).not.toBeInTheDocument();
});
