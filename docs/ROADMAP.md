# Roadmap

## Fase 1A — Fundação

**Concluída.**

- monorepo, API e frontend;
- PostgreSQL, Redis e Ollama opcional;
- health checks;
- Alembic, testes, lint e tipos;
- documentação operacional.

## Fase 1B — Identidade e perfil

**Implementada; aguardando aprovação.**

- conta, login, logout e sessão opaca;
- onboarding retomável;
- perfil, experiências e competências;
- objetivos e preferências de busca;
- isolamento entre usuários.

## Fase 1C — Descoberta e recomendação fake

- fonte fake determinística;
- normalização, validação e deduplicação;
- matching explicável;
- score e cobertura separados;
- execuções persistidas e ranking personalizado.

## Fase 1D — Integração e endurecimento

- dashboard, vagas, detalhes e execuções;
- acessibilidade e testes end-to-end;
- idempotência, sanitização e observabilidade;
- validação dos critérios completos da primeira entrega.

## Fase 2 — Fontes reais e currículos

- conectores estruturados;
- importação e múltiplos currículos-base;
- adaptação rastreável, diff e aprovação.

## Fase 3 — Candidatura assistida

- planejamento, adaptadores e Playwright em `dry-run`;
- aprovação humana e histórico.

## Fase 4 — Automação operacional

- scheduler, filas duráveis, retomada, métricas e alertas.
