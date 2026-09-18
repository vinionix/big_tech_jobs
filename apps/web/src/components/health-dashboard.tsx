"use client";

import { useEffect, useState } from "react";

import { fetchHealth, type HealthReport, type ServiceState } from "@/lib/api";

const labels: Record<string, string> = {
  postgres: "PostgreSQL",
  redis: "Redis",
  ollama: "Ollama",
};

const stateLabels: Record<ServiceState, string> = {
  healthy: "Disponível",
  unavailable: "Indisponível",
  disabled: "Desativado",
};

function badgeClass(status: ServiceState): string {
  if (status === "healthy") return "border-emerald-400/30 bg-emerald-400/10 text-emerald-200";
  if (status === "disabled") return "border-slate-400/30 bg-slate-400/10 text-slate-300";
  return "border-amber-400/30 bg-amber-400/10 text-amber-200";
}

export function HealthDashboard() {
  const [report, setReport] = useState<HealthReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();

    fetchHealth(controller.signal)
      .then((result) => setReport(result))
      .catch((reason: unknown) => {
        if (reason instanceof DOMException && reason.name === "AbortError") return;
        setError(reason instanceof Error ? reason.message : "Falha desconhecida ao consultar a API");
      })
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, []);

  return (
    <section aria-labelledby="health-title" className="rounded-3xl border border-white/10 bg-white/[0.04] p-6 shadow-2xl shadow-cyan-950/20 backdrop-blur md:p-8">
      <div className="flex flex-col justify-between gap-4 border-b border-white/10 pb-6 md:flex-row md:items-end">
        <div>
          <p className="text-sm font-medium text-cyan-200">Infraestrutura</p>
          <h2 id="health-title" className="mt-1 text-2xl font-semibold text-white">
            Estado dos serviços
          </h2>
        </div>
        {report ? (
          <p className="text-sm text-slate-400">
            API {report.ready ? "pronta" : "ainda não está pronta"}
          </p>
        ) : null}
      </div>

      {loading ? (
        <p role="status" className="py-10 text-slate-300">
          Consultando a API…
        </p>
      ) : null}

      {error ? (
        <div role="alert" className="mt-6 rounded-2xl border border-rose-400/30 bg-rose-400/10 p-5 text-rose-100">
          <p className="font-semibold">Não foi possível consultar a API.</p>
          <p className="mt-1 text-sm text-rose-200/80">{error}</p>
        </div>
      ) : null}

      {report ? (
        <ul className="grid gap-4 pt-6 md:grid-cols-3">
          {Object.entries(report.services).map(([name, service]) => (
            <li key={name} className="rounded-2xl border border-white/10 bg-slate-950/30 p-5">
              <div className="flex items-center justify-between gap-3">
                <h3 className="font-medium text-white">{labels[name] ?? name}</h3>
                <span className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${badgeClass(service.status)}`}>
                  {stateLabels[service.status]}
                </span>
              </div>
              <p className="mt-4 text-sm text-slate-400">
                {service.required ? "Obrigatório para a API" : "Opcional nesta fase"}
              </p>
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}
