import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { HealthDashboard } from "./health-dashboard";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("HealthDashboard", () => {
  it("exibe loading e depois os serviços retornados pela API", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          status: "degraded",
          ready: true,
          checked_at: "2026-09-18T00:00:00Z",
          services: {
            postgres: { status: "healthy", required: true, detail: null },
            redis: { status: "healthy", required: true, detail: null },
            ollama: { status: "unavailable", required: false, detail: "ConnectError" },
          },
        }),
        { status: 200 },
      ),
    );

    render(<HealthDashboard />);

    expect(screen.getByRole("status")).toHaveTextContent("Consultando a API");
    expect(await screen.findByText("PostgreSQL")).toBeInTheDocument();
    expect(screen.getByText("Ollama")).toBeInTheDocument();
    expect(screen.getByText("API pronta")).toBeInTheDocument();
  });

  it("exibe um erro seguro quando a API falha", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("conexão recusada"));

    render(<HealthDashboard />);

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent("Não foi possível consultar a API");
    });
  });
});
