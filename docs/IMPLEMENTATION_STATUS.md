# Estado da implementação

## Fase atual

Fase 1A — fundação e infraestrutura.

## Implementado

- estrutura do monorepo;
- FastAPI e endpoints de health;
- Next.js e painel de saúde;
- configuração de PostgreSQL, Redis e Ollama opcional;
- Alembic sem tabelas especulativas;
- testes e ferramentas de qualidade;
- documentação inicial.

## Não implementado

Todo o domínio de negócio permanece fora da Fase 1A: autenticação, perfil, vagas, matching, agentes, currículos e candidaturas.

## Validação

Executado com sucesso em 18 de setembro de 2026:

- `uv run ruff check .`;
- `uv run mypy src tests`;
- `uv run pytest -q` — 3 testes aprovados;
- `pnpm lint:web`;
- `pnpm typecheck:web`;
- `pnpm test:web` — 2 testes aprovados;
- `pnpm build:web` — build de produção concluído;
- `pnpm audit --prod` — nenhuma vulnerabilidade conhecida;
- `uvx pip-audit` — nenhuma vulnerabilidade conhecida;
- parse estrutural de `compose.yaml`;
- execução real da API e confirmação de HTTP 503 no readiness quando PostgreSQL e Redis estão indisponíveis.

## Limitações do ambiente

- Docker não está instalado, então `docker compose config` e a inicialização conjunta dos containers não puderam ser executados localmente.
- O build do Next.js passou, mas o servidor Next.js não inicia neste sandbox porque a chamada do Node a `uv_interface_addresses` é bloqueada pelo ambiente. O CI executará a validação fora desse sandbox.
- A integração real com PostgreSQL, Redis e Ollama será confirmada por Compose/CI; nesta execução foi validado o comportamento seguro quando estão indisponíveis.

## Próximo gate

Não iniciar a Fase 1B antes da revisão da Fase 1A e da confirmação do workflow de CI.
