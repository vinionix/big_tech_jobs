import { HealthDashboard } from "@/components/health-dashboard";

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-6 py-10 md:px-10 md:py-16">
      <header className="mb-14 max-w-3xl">
        <p className="mb-4 font-mono text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300">
          Fundação · Fase 1A
        </p>
        <h1 className="text-balance text-4xl font-semibold tracking-tight text-white md:text-6xl">
          Sua carreira não cabe em uma busca genérica.
        </h1>
        <p className="mt-6 max-w-2xl text-pretty text-base leading-7 text-slate-300 md:text-lg">
          O Big Tech Jobs está preparando uma experiência de recomendação explicável, adaptada ao
          perfil de cada profissional. Nesta entrega, validamos a base técnica que sustentará o
          produto.
        </p>
      </header>

      <HealthDashboard />

      <footer className="mt-auto pt-16 text-sm text-slate-500">
        Nenhuma API paga. Ollama local e lógica determinística por padrão.
      </footer>
    </main>
  );
}
