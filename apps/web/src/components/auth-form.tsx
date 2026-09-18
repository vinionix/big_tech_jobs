"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { ApiError, apiRequest } from "@/lib/api";

interface AuthFormProps {
  mode: "login" | "register";
}

export function AuthForm({ mode }: AuthFormProps) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const isRegister = mode === "register";

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    const data = new FormData(event.currentTarget);
    try {
      await apiRequest(`/auth/${isRegister ? "register" : "login"}`, {
        method: "POST",
        body: JSON.stringify({ email: data.get("email"), password: data.get("password") }),
      });
      router.push(isRegister ? "/onboarding" : "/perfil");
      router.refresh();
    } catch (reason) {
      setError(
        reason instanceof ApiError && reason.status === 401
          ? "E-mail ou senha incorretos."
          : reason instanceof ApiError && reason.status === 409
            ? "Este e-mail já possui uma conta."
            : "Não foi possível concluir. Tente novamente.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-md items-center px-6 py-12">
      <section className="w-full rounded-3xl border border-slate-700/80 bg-slate-900/80 p-7 shadow-2xl">
        <Link href="/" className="text-sm text-cyan-300 hover:text-cyan-200">
          ← Big Tech Jobs
        </Link>
        <h1 className="mt-6 text-3xl font-semibold">{isRegister ? "Crie sua conta" : "Entre na sua conta"}</h1>
        <p className="mt-2 text-sm leading-6 text-slate-400">
          {isRegister
            ? "Comece com o essencial e complete seu perfil no seu ritmo."
            : "Continue de onde parou no seu perfil profissional."}
        </p>
        <form className="mt-8 space-y-5" onSubmit={submit}>
          <label className="block text-sm font-medium">
            E-mail
            <input className="field mt-2" name="email" type="email" autoComplete="email" required />
          </label>
          <label className="block text-sm font-medium">
            Senha
            <input
              className="field mt-2"
              name="password"
              type="password"
              autoComplete={isRegister ? "new-password" : "current-password"}
              minLength={isRegister ? 12 : undefined}
              required
            />
            {isRegister && <span className="mt-2 block text-xs text-slate-500">Use pelo menos 12 caracteres.</span>}
          </label>
          {error && <p role="alert" className="rounded-xl bg-red-950/70 px-4 py-3 text-sm text-red-200">{error}</p>}
          <button className="primary-button w-full" disabled={submitting} type="submit">
            {submitting ? "Enviando…" : isRegister ? "Criar conta" : "Entrar"}
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-slate-400">
          {isRegister ? "Já tem uma conta?" : "Ainda não tem conta?"}{" "}
          <Link className="text-cyan-300 hover:underline" href={isRegister ? "/entrar" : "/cadastro"}>
            {isRegister ? "Entrar" : "Criar conta"}
          </Link>
        </p>
      </section>
    </main>
  );
}
