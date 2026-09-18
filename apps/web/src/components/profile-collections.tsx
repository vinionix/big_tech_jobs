"use client";

import { FormEvent } from "react";

import { apiRequest } from "@/lib/api";
import { Onboarding } from "@/lib/profile-api";

interface Props {
  data: Onboarding;
  busy: boolean;
  run: (action: () => Promise<unknown>, success: string) => Promise<void>;
}

const value = (form: FormData, name: string) => String(form.get(name) ?? "").trim();
const optional = (form: FormData, name: string) => value(form, name) || null;

function RemoveButton({ label, path, run }: { label: string; path: string; run: Props["run"] }) {
  return (
    <button
      aria-label={label}
      onClick={() =>
        void run(() => apiRequest(path, { method: "DELETE" }), "Item removido.")
      }
    >
      Excluir
    </button>
  );
}

export function ProfileCollections({ data, busy, run }: Props) {
  async function submit(
    event: FormEvent<HTMLFormElement>,
    path: string,
    payload: (form: FormData) => object,
    message: string,
  ) {
    event.preventDefault();
    const target = event.currentTarget;
    const form = new FormData(target);
    await run(
      () => apiRequest(path, { method: "POST", body: JSON.stringify(payload(form)) }),
      message,
    );
    target.reset();
  }

  return (
    <section className="grid gap-8 lg:grid-cols-2">
      <div className="card">
        <h2 className="section-title">5. Projetos</h2>
        <ul className="mt-5 space-y-3">
          {data.projects.map((item) => (
            <li className="list-item" key={item.id}>
              <div><strong>{item.title}</strong><p className="text-sm text-slate-400">{item.role || item.description}</p></div>
              <RemoveButton label={`Excluir projeto ${item.title}`} path={`/profile/projects/${item.id}`} run={run} />
            </li>
          ))}
        </ul>
        <form className="mt-5 space-y-4" onSubmit={(event) => void submit(event, "/profile/projects", (form) => ({ title: value(form, "project_title"), role: optional(form, "project_role"), description: optional(form, "project_description"), results: optional(form, "project_results"), url: optional(form, "project_url") }), "Projeto adicionado.")}>
          <label>Projeto<input className="field mt-2" name="project_title" required /></label>
          <label>Seu papel<input className="field mt-2" name="project_role" /></label>
          <label>Descrição<textarea className="field mt-2" name="project_description" /></label>
          <label>Resultados<textarea className="field mt-2" name="project_results" /></label>
          <label>Link<input className="field mt-2" name="project_url" type="url" /></label>
          <button className="secondary-button" disabled={busy}>Adicionar projeto</button>
        </form>
      </div>

      <div className="card">
        <h2 className="section-title">6. Formação</h2>
        <ul className="mt-5 space-y-3">
          {data.education.map((item) => (
            <li className="list-item" key={item.id}>
              <div><strong>{item.institution}</strong><p className="text-sm text-slate-400">{[item.degree, item.field_of_study].filter(Boolean).join(" · ")}</p></div>
              <RemoveButton label={`Excluir formação ${item.institution}`} path={`/profile/education/${item.id}`} run={run} />
            </li>
          ))}
        </ul>
        <form className="mt-5 space-y-4" onSubmit={(event) => void submit(event, "/profile/education", (form) => ({ institution: value(form, "institution"), degree: optional(form, "degree"), field_of_study: optional(form, "field_of_study"), start_date: optional(form, "education_start"), end_date: optional(form, "education_end") }), "Formação adicionada.")}>
          <label>Instituição<input className="field mt-2" name="institution" required /></label>
          <label>Curso ou grau<input className="field mt-2" name="degree" /></label>
          <label>Área de estudo<input className="field mt-2" name="field_of_study" /></label>
          <div className="grid grid-cols-2 gap-3"><label>Início<input className="field mt-2" name="education_start" type="date" /></label><label>Fim<input className="field mt-2" name="education_end" type="date" /></label></div>
          <button className="secondary-button" disabled={busy}>Adicionar formação</button>
        </form>
      </div>

      <div className="card">
        <h2 className="section-title">7. Idiomas</h2>
        <ul className="mt-5 space-y-3">
          {data.languages.map((item) => (
            <li className="list-item" key={item.id}><div><strong>{item.name}</strong><p className="text-sm text-slate-400">{item.proficiency}</p></div><RemoveButton label={`Excluir idioma ${item.name}`} path={`/profile/languages/${item.id}`} run={run} /></li>
          ))}
        </ul>
        <form className="mt-5 space-y-4" onSubmit={(event) => void submit(event, "/profile/languages", (form) => ({ name: value(form, "language_name"), proficiency: value(form, "language_proficiency") }), "Idioma adicionado.")}>
          <label>Idioma<input className="field mt-2" name="language_name" required /></label>
          <label>Proficiência<input className="field mt-2" name="language_proficiency" required placeholder="Básico, intermediário, avançado…" /></label>
          <button className="secondary-button" disabled={busy}>Adicionar idioma</button>
        </form>
      </div>

      <div className="card">
        <h2 className="section-title">8. Certificações</h2>
        <ul className="mt-5 space-y-3">
          {data.certifications.map((item) => (
            <li className="list-item" key={item.id}><div><strong>{item.name}</strong><p className="text-sm text-slate-400">{item.issuer}</p></div><RemoveButton label={`Excluir certificação ${item.name}`} path={`/profile/certifications/${item.id}`} run={run} /></li>
          ))}
        </ul>
        <form className="mt-5 space-y-4" onSubmit={(event) => void submit(event, "/profile/certifications", (form) => ({ name: value(form, "certification_name"), issuer: optional(form, "issuer"), issue_date: optional(form, "issue_date"), credential_url: optional(form, "credential_url") }), "Certificação adicionada.")}>
          <label>Certificação<input className="field mt-2" name="certification_name" required /></label>
          <label>Emissor<input className="field mt-2" name="issuer" /></label>
          <label>Emissão<input className="field mt-2" name="issue_date" type="date" /></label>
          <label>Credencial<input className="field mt-2" name="credential_url" type="url" /></label>
          <button className="secondary-button" disabled={busy}>Adicionar certificação</button>
        </form>
      </div>

      <div className="card lg:col-span-2">
        <h2 className="section-title">9. Portfólio, publicações e perfis</h2>
        <ul className="mt-5 grid gap-3 md:grid-cols-2">
          {data.professional_links.map((item) => (
            <li className="list-item" key={item.id}><div><strong>{item.label}</strong><p className="max-w-sm truncate text-sm text-slate-400">{item.url}</p></div><RemoveButton label={`Excluir link ${item.label}`} path={`/profile/links/${item.id}`} run={run} /></li>
          ))}
        </ul>
        <form className="mt-5 grid gap-4 md:grid-cols-3" onSubmit={(event) => void submit(event, "/profile/links", (form) => ({ label: value(form, "link_label"), url: value(form, "link_url"), kind: value(form, "link_kind") }), "Link adicionado.")}>
          <label>Rótulo<input className="field mt-2" name="link_label" required placeholder="GitHub" /></label>
          <label>URL<input className="field mt-2" name="link_url" type="url" required /></label>
          <label>Tipo<select className="field mt-2" name="link_kind"><option value="portfolio">Portfólio</option><option value="publication">Publicação</option><option value="profile">Perfil profissional</option></select></label>
          <button className="secondary-button md:w-fit" disabled={busy}>Adicionar link</button>
        </form>
      </div>
    </section>
  );
}
