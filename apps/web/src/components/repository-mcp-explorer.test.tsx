import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { RepositoryMCPExplorer } from "./repository-mcp-explorer";
import { mcpCatalogFixture } from "@/lib/repository-mcp.fixture";

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

describe("RepositoryMCPExplorer", () => {
  it("inspects schemas and permissions without calling any tools", async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(new Response(JSON.stringify(mcpCatalogFixture))));
    vi.stubGlobal("fetch", fetchMock);
    render(<RepositoryMCPExplorer />);
    expect(screen.getByRole("status")).toHaveTextContent("Loading");
    await screen.findByText("repository.patch.apply");
    expect(screen.getByLabelText("Tool input schema")).toHaveTextContent("APPLY EXACT PATCH");
    expect(screen.getByText("Invocation disabled")).toBeInTheDocument();
    expect(screen.getByText(/Required flags disabled/)).toBeInTheDocument();
    fireEvent.change(screen.getByRole("combobox", { name: "Tool contract" }), {
      target: { value: "repository.test.approve" },
    });
    expect(screen.getByLabelText("Tool input schema")).toHaveTextContent("RUN ISOLATED TEST PROFILE");
    expect(screen.getByText(/Required flags enabled/)).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(screen.getAllByRole("button")).toHaveLength(1);
    fireEvent.click(screen.getByRole("button", { name: "Refresh contracts" }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
    await screen.findByText("repository.test.approve");
    for (const [url, options] of fetchMock.mock.calls) {
      expect(url).toBe("/api/ai/repository/mcp/catalog");
      expect(options.method).toBeUndefined();
      expect(options.body).toBeUndefined();
      expect(options.headers).toBeUndefined();
    }
  });

  it("filters contracts and handles an empty result", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(mcpCatalogFixture))));
    render(<RepositoryMCPExplorer />);
    await screen.findByText("repository.patch.apply");
    fireEvent.change(screen.getByRole("textbox", { name: "Filter tool contracts" }), { target: { value: "test" } });
    expect(screen.getByText("repository.test.approve")).toBeInTheDocument();
    fireEvent.change(screen.getByRole("textbox", { name: "Filter tool contracts" }), { target: { value: "missing" } });
    expect(screen.getByRole("status")).toHaveTextContent("No tool contracts match");
    expect(screen.queryByLabelText("Selected tool contract")).not.toBeInTheDocument();
  });

  it("fails closed on an invocation-capable response", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ ...mcpCatalogFixture, invocation_enabled: true }))));
    render(<RepositoryMCPExplorer />);
    expect(await screen.findByRole("alert")).toHaveTextContent("unavailable");
    expect(screen.queryByRole("combobox")).not.toBeInTheDocument();
  });

  it("renders schema markup as inert text", async () => {
    const tool = mcpCatalogFixture.tools[0];
    const catalog = { ...mcpCatalogFixture, tools: [{ ...tool, inputSchema: { ...tool.inputSchema, description: "<script>attack()</script>" } }] };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(catalog))));
    render(<RepositoryMCPExplorer />);
    const schema = await screen.findByLabelText("Tool input schema");
    expect(schema).toHaveTextContent("<script>attack()</script>");
    expect(schema.querySelector("script")).toBeNull();
  });

  it("allows retry after a transport failure", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValueOnce(new Error("transport"))
      .mockResolvedValueOnce(new Response(JSON.stringify({ ...mcpCatalogFixture, tools: [] }))));
    render(<RepositoryMCPExplorer />);
    await screen.findByRole("alert");
    fireEvent.click(screen.getByRole("button", { name: "Refresh contracts" }));
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("No tool contracts match"));
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});
