# Decisões arquiteturais

## ADR-001 — Monólito modular

- **Status:** aceito.
- **Decisão:** FastAPI e Next.js em monorepo; sem microserviços no MVP.
- **Motivo:** reduz complexidade operacional e mantém transações e testes simples.

## ADR-002 — PostgreSQL como fonte de verdade

- **Status:** aceito.
- **Decisão:** dados de negócio nunca existirão somente no Redis.
- **Motivo:** durabilidade, auditoria e integridade relacional.

## ADR-003 — Ollama opcional e sem fallback pago

- **Status:** aceito.
- **Decisão:** `OLLAMA_BASE_URL` e `OLLAMA_MODEL` são configuráveis; nenhuma API paga será integrada no MVP.
- **Motivo:** requisito de custo zero por token e funcionamento determinístico sem LLM.

## ADR-004 — Proxy same-origin no frontend

- **Status:** aceito.
- **Decisão:** o navegador acessa a API por `/backend/*`, encaminhado pelo Next.js.
- **Motivo:** simplifica desenvolvimento, cookies futuros e política de origem.

## ADR-005 — Implementação por gates

- **Status:** aceito.
- **Decisão:** a Fase 1 foi dividida em 1A a 1D e cada subfase exige validação antes da próxima.
- **Motivo:** reduzir escopo por execução e evitar fundações superficiais.

## Decisões para fases futuras

- autenticação por sessão opaca e cookie HTTP-only;
- interface inicial em português;
- score e cobertura/confiança como valores separados;
- frequência persistida antes de existir scheduler;
- migrações apenas para entidades em uso;
- nenhum deploy de produção antes de política de retenção, modelo de ameaça e proteção adequada de dados sensíveis.
