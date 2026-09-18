import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AuthForm } from "./auth-form";

const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push, refresh: vi.fn() }),
}));

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  push.mockReset();
});

describe("AuthForm", () => {
  it("cria a conta pela API e segue para o onboarding", async () => {
    const request = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ account: { id: "1", email: "ada@example.com" } }), {
        status: 201,
      }),
    );
    render(<AuthForm mode="register" />);

    fireEvent.change(screen.getByLabelText("E-mail"), {
      target: { value: "ada@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/^Senha/), {
      target: { value: "a-secure-password" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Criar conta" }));

    await waitFor(() => expect(push).toHaveBeenCalledWith("/onboarding"));
    expect(request).toHaveBeenCalledWith(
      "/backend/api/v1/auth/register",
      expect.objectContaining({ method: "POST", credentials: "include" }),
    );
  });

  it("não expõe a mensagem interna quando o login falha", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ detail: "Invalid credentials" }), { status: 401 }),
    );
    render(<AuthForm mode="login" />);

    fireEvent.change(screen.getByLabelText("E-mail"), {
      target: { value: "ada@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/^Senha/), { target: { value: "wrong" } });
    fireEvent.click(screen.getByRole("button", { name: "Entrar" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("E-mail ou senha incorretos.");
  });
});
