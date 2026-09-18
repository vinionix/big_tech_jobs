"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useCallback, useEffect, useState } from "react";

import { ApiError, apiRequest } from "@/lib/api";
import { getOnboarding, Onboarding, splitList } from "@/lib/profile-api";

import { ProfileCollections } from "./profile-collections";

function formString(data: FormData, name: string): string {
  return String(data.get(name) ?? "").trim();
}

function optionalNumber(data: FormData, name: string): number | null {
  const value = formString(data, name);
  return value ? Number(value) : null;
}

export function ProfileWorkspace() {
  const router = useRouter();
  const [data, setData] = useState<Onboarding | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      setData(await getOnboarding());
      setError(null);
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 401) {
        router.replace("/entrar");
        return;
      }
      setError("Não foi possível carregar seu perfil.");
    }
  }, [router]);

  useEffect(() => {
    let active = true;
    void getOnboarding()
      .then((result) => {
        if (active) setData(result);
      })
      .catch((reason: unknown) => {
        if (!active) return;
        if (reason instanceof ApiError && reason.status === 401) {
          router.replace("/entrar");
        } else {
          setError("Não foi possível carregar seu perfil.");
        }
      });
    return () => {
      active = false;
    };
  }, [router]);

  async function run(action: () => Promise<unknown>, success: string) {
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      await action();
      await load();
      setNotice(success);
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "Não foi possível salvar.");
    } finally {
      setBusy(false);
    }
  }

  async function saveProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await run(
      () =>
        apiRequest("/profile", {
          method: "PUT",
          body: JSON.stringify({
            full_name: formString(form, "full_name") || null,
            phone: formString(form, "phone") || null,
            current_location: formString(form, "current_location") || null,
            professional_summary: formString(form, "professional_summary") || null,
            current_seniority: formString(form, "current_seniority") || null,
            years_experience: optionalNumber(form, "years_experience"),
            countries_of_interest: splitList(formString(form, "countries_of_interest")),
            acceptable_timezones: splitList(formString(form, "acceptable_timezones")),
            desired_work_modes: form.getAll("desired_work_modes"),
            work_authorizations: splitList(formString(form, "work_authorizations")),
            needs_sponsorship: formString(form, "needs_sponsorship") === "unknown" ? null : formString(form, "needs_sponsorship") === "yes",
            willing_to_relocate: formString(form, "willing_to_relocate") === "unknown" ? null : formString(form, "willing_to_relocate") === "yes",
            salary_min: optionalNumber(form, "salary_min"),
            salary_max: optionalNumber(form, "salary_max"),
            salary_currency: formString(form, "salary_currency") || null,
            onboarding_step: Math.max(data?.profile.onboarding_step ?? 1, 2),
            onboarding_completed: data?.profile.onboarding_completed ?? false,
          }),
        }),
      "Dados pessoais salvos.",
    );
  }

  async function saveGoalAndPreferences(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const title = formString(form, "target_title");
    await run(async () => {
      await apiRequest("/career-goals", {
        method: "PUT",
        body: JSON.stringify(
          title
            ? [{ target_title: title, area: formString(form, "area"), target_seniority: formString(form, "target_seniority") || null, priority: 1 }]
            : [],
        ),
      });
      await apiRequest("/search-preferences", {
        method: "PUT",
        body: JSON.stringify({
          desired_job_count: Number(formString(form, "desired_job_count")),
          max_recommendations: Number(formString(form, "max_recommendations")),
          frequency: formString(form, "frequency"),
          search_breadth: formString(form, "search_breadth"),
          minimum_score: Number(formString(form, "minimum_score")),
          preferred_companies: splitList(formString(form, "preferred_companies")),
          blocked_companies: splitList(formString(form, "blocked_companies")),
          preferred_sectors: splitList(formString(form, "preferred_sectors")),
          preferred_company_types: splitList(formString(form, "preferred_company_types")),
          preferred_company_sizes: splitList(formString(form, "preferred_company_sizes")),
          culture_preferences: splitList(formString(form, "culture_preferences")),
          benefit_preferences: splitList(formString(form, "benefit_preferences")),
          work_nature_preferences: splitList(formString(form, "work_nature_preferences")),
          elimination_criteria: splitList(formString(form, "elimination_criteria")),
        }),
      });
      await apiRequest("/profile", {
        method: "PUT",
        body: JSON.stringify({ ...data?.profile, onboarding_step: 3 }),
      });
    }, "Objetivo e preferências salvos.");
  }

  async function addExperience(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const target = event.currentTarget;
    const form = new FormData(target);
    await run(
      () => apiRequest("/profile/experiences", { method: "POST", body: JSON.stringify({ company: formString(form, "company"), title: formString(form, "title"), start_date: formString(form, "start_date"), is_current: form.get("is_current") === "on", responsibilities: formString(form, "responsibilities") || null, results: formString(form, "results") || null }) }),
      "Experiência adicionada.",
    );
    target.reset();
  }

  async function addSkill(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const target = event.currentTarget;
    const form = new FormData(target);
    await run(
      () => apiRequest("/profile/skills", { method: "POST", body: JSON.stringify({ name: formString(form, "skill_name"), category: formString(form, "skill_category"), proficiency: formString(form, "proficiency") || null }) }),
      "Competência adicionada.",
    );
    target.reset();
  }

  async function finish() {
    if (!data) return;
    await run(
      () => apiRequest("/profile", { method: "PUT", body: JSON.stringify({ ...data.profile, onboarding_step: 4, onboarding_completed: true }) }),
      "Onboarding concluído. Você pode editar tudo quando quiser.",
    );
  }

  async function logout() {
    await apiRequest("/auth/logout", { method: "POST" });
    router.push("/");
  }

  if (!data && !error) return <main className="mx-auto max-w-5xl px-6 py-16"><p>Carregando seu perfil…</p></main>;
  if (!data) return <main className="mx-auto max-w-5xl px-6 py-16"><p role="alert">{error}</p><button className="secondary-button mt-4" onClick={() => void load()}>Tentar novamente</button></main>;

  const goal = data.career_goals[0];
  const profile = data.profile;
  const preferences = data.search_preferences;
  const boolValue = (value: boolean | null) => (value === null ? "unknown" : value ? "yes" : "no");

  return (
    <main className="mx-auto min-h-screen w-full max-w-6xl px-6 py-8 md:px-10">
      <nav className="flex items-center justify-between border-b border-slate-800 pb-5">
        <Link href="/" className="font-semibold text-white">Big Tech Jobs</Link>
        <button className="text-sm text-slate-400 hover:text-white" onClick={() => void logout()}>Sair</button>
      </nav>

      <header className="grid gap-8 py-10 md:grid-cols-[1fr_18rem] md:items-end">
        <div><p className="eyebrow">Fase 1B · Seu perfil</p><h1 className="mt-3 text-4xl font-semibold">Conte o que você busca. Sem persona pronta.</h1><p className="mt-4 max-w-2xl text-slate-400">Salve parcialmente e continue depois. Campos opcionais melhoram a recomendação, mas não bloqueiam o uso.</p></div>
        <div className="card"><div className="flex justify-between text-sm"><span>Completude</span><strong>{data.completeness.percentage}%</strong></div><div className="mt-3 h-2 overflow-hidden rounded bg-slate-800"><div className="h-full rounded bg-cyan-400" style={{ width: `${data.completeness.percentage}%` }} /></div><p className="mt-3 text-xs text-slate-500">Falta: {data.completeness.missing.join(", ") || "nada essencial"}.</p></div>
      </header>

      {(error || notice) && <p role={error ? "alert" : "status"} className={`mb-6 rounded-xl px-4 py-3 text-sm ${error ? "bg-red-950 text-red-200" : "bg-emerald-950 text-emerald-200"}`}>{error ?? notice}</p>}

      <div className="space-y-8">
        <section className="card"><h2 className="section-title">1. Identidade profissional</h2><form className="mt-6 grid gap-5 md:grid-cols-2" onSubmit={saveProfile}>
          <label>Nome completo<input className="field mt-2" name="full_name" defaultValue={profile.full_name ?? ""} /></label>
          <label>Telefone<input className="field mt-2" name="phone" defaultValue={profile.phone ?? ""} /></label>
          <label>Localização atual<input className="field mt-2" name="current_location" defaultValue={profile.current_location ?? ""} /></label>
          <label>Senioridade atual<input className="field mt-2" name="current_seniority" defaultValue={profile.current_seniority ?? ""} placeholder="Estágio, júnior, pleno…" /></label>
          <label>Anos de experiência<input className="field mt-2" name="years_experience" type="number" min="0" max="80" step="0.5" defaultValue={profile.years_experience ?? ""} /></label>
          <label>Países de interesse<input className="field mt-2" name="countries_of_interest" defaultValue={profile.countries_of_interest.join(", ")} placeholder="Brasil, Portugal" /></label>
          <label>Fusos aceitáveis<input className="field mt-2" name="acceptable_timezones" defaultValue={profile.acceptable_timezones.join(", ")} placeholder="UTC-3, UTC+0" /></label>
          <label>Autorização de trabalho por país<input className="field mt-2" name="work_authorizations" defaultValue={profile.work_authorizations.join(", ")} /></label>
          <fieldset className="md:col-span-2"><legend>Modalidades desejadas</legend><div className="mt-2 flex flex-wrap gap-4">{[["remote", "Remoto"], ["hybrid", "Híbrido"], ["onsite", "Presencial"]].map(([value, label]) => <label key={value} className="flex items-center gap-2"><input type="checkbox" name="desired_work_modes" value={value} defaultChecked={profile.desired_work_modes.includes(value as "remote" | "hybrid" | "onsite")} />{label}</label>)}</div></fieldset>
          <label>Precisa de sponsorship?<select className="field mt-2" name="needs_sponsorship" defaultValue={boolValue(profile.needs_sponsorship)}><option value="unknown">Prefiro não informar</option><option value="yes">Sim</option><option value="no">Não</option></select></label>
          <label>Aceita relocação?<select className="field mt-2" name="willing_to_relocate" defaultValue={boolValue(profile.willing_to_relocate)}><option value="unknown">Prefiro não informar</option><option value="yes">Sim</option><option value="no">Não</option></select></label>
          <label>Pretensão mínima<input className="field mt-2" name="salary_min" type="number" min="0" defaultValue={profile.salary_min ?? ""} /></label>
          <label>Pretensão máxima<input className="field mt-2" name="salary_max" type="number" min="0" defaultValue={profile.salary_max ?? ""} /></label>
          <label>Moeda<input className="field mt-2 uppercase" name="salary_currency" minLength={3} maxLength={3} defaultValue={profile.salary_currency ?? ""} placeholder="BRL" /></label>
          <label className="md:col-span-2">Resumo profissional<textarea className="field mt-2 min-h-28" name="professional_summary" defaultValue={profile.professional_summary ?? ""} /></label>
          <button className="primary-button md:col-span-2 md:w-fit" disabled={busy}>Salvar e continuar</button>
        </form></section>

        <section className="card"><h2 className="section-title">2. Objetivo e volume da busca</h2><form className="mt-6 grid gap-5 md:grid-cols-2" onSubmit={saveGoalAndPreferences}>
          <label>Cargo-alvo<input className="field mt-2" name="target_title" required defaultValue={goal?.target_title ?? ""} /></label><label>Área<input className="field mt-2" name="area" required defaultValue={goal?.area ?? ""} /></label><label>Senioridade buscada<input className="field mt-2" name="target_seniority" defaultValue={goal?.target_seniority ?? ""} /></label>
          <label>Vagas desejadas por busca<input className="field mt-2" name="desired_job_count" type="number" min="1" max="500" required defaultValue={preferences.desired_job_count} /></label><label>Máximo exibido<input className="field mt-2" name="max_recommendations" type="number" min="1" max="500" required defaultValue={preferences.max_recommendations} /></label><label>Score mínimo<input className="field mt-2" name="minimum_score" type="number" min="0" max="100" step="0.01" defaultValue={preferences.minimum_score} /></label>
          <label>Frequência<select className="field mt-2" name="frequency" defaultValue={preferences.frequency}><option value="manual">Manual</option><option value="daily">Diária</option><option value="weekly">Semanal</option><option value="biweekly">Quinzenal</option></select></label><label>Amplitude<select className="field mt-2" name="search_breadth" defaultValue={preferences.search_breadth}><option value="focused">Poucas e aderentes</option><option value="balanced">Equilibrada</option><option value="broad">Mais ampla</option></select></label>
          <label>Empresas preferidas<input className="field mt-2" name="preferred_companies" defaultValue={preferences.preferred_companies.join(", ")} /></label><label>Empresas bloqueadas<input className="field mt-2" name="blocked_companies" defaultValue={preferences.blocked_companies.join(", ")} /></label><label>Setores preferidos<input className="field mt-2" name="preferred_sectors" defaultValue={preferences.preferred_sectors.join(", ")} /></label><label>Tipos de empresa<input className="field mt-2" name="preferred_company_types" defaultValue={preferences.preferred_company_types.join(", ")} placeholder="Startup, consultoria, produto" /></label><label>Portes de empresa<input className="field mt-2" name="preferred_company_sizes" defaultValue={preferences.preferred_company_sizes.join(", ")} placeholder="Pequena, média, grande" /></label><label>Preferências de cultura<input className="field mt-2" name="culture_preferences" defaultValue={preferences.culture_preferences.join(", ")} /></label><label>Benefícios desejados<input className="field mt-2" name="benefit_preferences" defaultValue={preferences.benefit_preferences.join(", ")} /></label><label>Natureza do trabalho<input className="field mt-2" name="work_nature_preferences" defaultValue={preferences.work_nature_preferences.join(", ")} placeholder="Produto, pesquisa, liderança…" /></label><label>Critérios eliminatórios<input className="field mt-2" name="elimination_criteria" defaultValue={preferences.elimination_criteria.join(", ")} placeholder="Sem sponsorship, presencial obrigatório…" /></label>
          <button className="primary-button md:col-span-2 md:w-fit" disabled={busy}>Salvar objetivo</button>
        </form></section>

        <section className="grid gap-8 lg:grid-cols-2"><div className="card"><h2 className="section-title">3. Experiências</h2><ul className="mt-5 space-y-3">{data.experiences.map((item) => <li className="list-item" key={item.id}><div><strong>{item.title}</strong><p className="text-sm text-slate-400">{item.company}</p></div><button aria-label={`Excluir experiência ${item.title}`} onClick={() => void run(() => apiRequest(`/profile/experiences/${item.id}`, { method: "DELETE" }), "Experiência removida.")}>Excluir</button></li>)}</ul><form className="mt-5 space-y-4" onSubmit={addExperience}><label>Empresa<input className="field mt-2" name="company" required /></label><label>Cargo<input className="field mt-2" name="title" required /></label><label>Início<input className="field mt-2" name="start_date" type="date" required /></label><label className="flex items-center gap-2"><input name="is_current" type="checkbox" />Trabalho aqui atualmente</label><label>Responsabilidades<textarea className="field mt-2" name="responsibilities" /></label><label>Resultados<textarea className="field mt-2" name="results" /></label><button className="secondary-button" disabled={busy}>Adicionar experiência</button></form></div>
          <div className="card"><h2 className="section-title">4. Competências</h2><ul className="mt-5 flex flex-wrap gap-2">{data.skills.map((item) => <li className="tag" key={item.id}>{item.name}<button aria-label={`Excluir competência ${item.name}`} onClick={() => void run(() => apiRequest(`/profile/skills/${item.id}`, { method: "DELETE" }), "Competência removida.")}>×</button></li>)}</ul><form className="mt-5 space-y-4" onSubmit={addSkill}><label>Competência<input className="field mt-2" name="skill_name" required /></label><label>Tipo<select className="field mt-2" name="skill_category"><option value="technical">Técnica</option><option value="behavioral">Comportamental</option></select></label><label>Proficiência<input className="field mt-2" name="proficiency" placeholder="Básico, intermediário, avançado…" /></label><button className="secondary-button" disabled={busy}>Adicionar competência</button></form></div></section>

        <ProfileCollections data={data} busy={busy} run={run} />

        <section className="card flex flex-col gap-5 md:flex-row md:items-center md:justify-between"><div><h2 className="section-title">Pronto por enquanto?</h2><p className="mt-2 text-sm text-slate-400">Você poderá voltar e melhorar o perfil a qualquer momento.</p></div><button className="primary-button" disabled={busy} onClick={() => void finish()}>Concluir onboarding</button></section>
      </div>
    </main>
  );
}
