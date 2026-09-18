# Estado da implementação

## Fase atual

Fase 1B — identidade e perfil, implementada e em validação.

## Implementado

- estrutura do monorepo;
- FastAPI e endpoints de health;
- Next.js e painel de saúde;
- configuração de PostgreSQL, Redis e Ollama opcional;
- Alembic sem tabelas especulativas;
- testes e ferramentas de qualidade;
- documentação inicial.
- contas com senha Argon2 e sessões opacas revogáveis;
- cadastro, login, logout e consulta da sessão;
- onboarding retomável e completude determinística;
- edição do perfil, experiências, projetos, formação, competências, idiomas, certificações e links;
- objetivos de carreira e preferências de busca configuráveis;
- isolamento de recursos por usuário;
- migração relacional da Fase 1B;
- telas de cadastro, login, onboarding e perfil.

## Não implementado

Busca de vagas, matching, agentes, currículos e candidaturas ainda não foram implementados. A importação assistida e os múltiplos currículos-base permanecem na Fase 2.

## Validação

Executado com sucesso em 18 de setembro de 2026 para a Fase 1B:

- `uv run ruff check .`;
- `uv run mypy src tests`;
- `uv run pytest -q` — 8 testes aprovados, incluindo sessão, retomada e isolamento;
- `pnpm lint:web`;
- `pnpm typecheck:web`;
- `pnpm test:web` — 4 testes aprovados;
- `pnpm build:web` — build de produção concluído;
- `pnpm audit --prod` — nenhuma vulnerabilidade conhecida;
- `uvx pip-audit` — nenhuma vulnerabilidade conhecida;
- geração SQL offline completa da migração PostgreSQL — 226 linhas;
- parse estrutural de `compose.yaml`;
- execução real da API e confirmação de HTTP 503 no readiness quando PostgreSQL e Redis estão indisponíveis.

## Limitações do ambiente

- Docker não está instalado, então `docker compose config` e a inicialização conjunta dos containers não puderam ser executados localmente.
- O build do Next.js passou, mas o servidor Next.js não inicia neste sandbox porque a chamada do Node a `uv_interface_addresses` é bloqueada pelo ambiente. O CI executará a validação fora desse sandbox.
- A integração real com PostgreSQL, Redis e Ollama será confirmada por Compose/CI; nesta execução foi validado o comportamento seguro quando estão indisponíveis.

## Próximo gate

Não iniciar a Fase 1C antes da revisão da Fase 1B e da confirmação do workflow de CI.
