import Link from "next/link";

import { HealthDashboard } from "@/components/health-dashboard";

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-6 py-10 md:px-10 md:py-16">
      <header className="mb-14 max-w-3xl">
        <p className="mb-4 font-mono text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300">
          Perfil profissional · Fase 1B
        </p>
        <h1 className="text-balance text-4xl font-semibold tracking-tight text-white md:text-6xl">
          Sua carreira não cabe em uma busca genérica.
        </h1>
        <p className="mt-6 max-w-2xl text-pretty text-base leading-7 text-slate-300 md:text-lg">
          Monte um perfil que represente sua experiência real, seus objetivos e o volume de vagas
          que você quer receber. Nenhuma carreira ou senioridade é tratada como padrão universal.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link className="primary-button" href="/cadastro">Criar meu perfil</Link>
          <Link className="secondary-button" href="/entrar">Já tenho uma conta</Link>
        </div>
      </header>

      <HealthDashboard />

      <footer className="mt-auto pt-16 text-sm text-slate-500">
        Sessão segura, dados isolados por conta e nenhuma API paga.
      </footer>
    </main>
  );
}
