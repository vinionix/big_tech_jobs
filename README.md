# Big Tech Jobs

Plataforma multiusuário para descoberta, recomendação e acompanhamento de vagas de tecnologia. O projeto está sendo construído em fatias verificáveis; a Fase 1A entrega somente a fundação executável.

## Estado atual

Implementado:

- monorepo com FastAPI e Next.js;
- PostgreSQL e Redis no Docker Compose;
- health checks da API, banco, Redis e Ollama;
- frontend consumindo a API real por proxy same-origin;
- configuração de Alembic, testes e análise estática;
- Ollama opcional, sem fallback para APIs pagas.

Ainda não implementado:

- autenticação e perfis;
- busca e recomendação de vagas;
- LangGraph;
- adaptação de currículo;
- candidaturas e automação.

Consulte [ROADMAP.md](docs/ROADMAP.md) para o recorte das próximas entregas.

## Requisitos

- Docker com Compose v2; ou
- Python 3.12, `uv`, Node.js compatível com Next.js e `pnpm` para execução sem Docker.

O Ollama é opcional na Fase 1A. Modelos locais não cobram por requisição, mas exigem memória e processamento da máquina. Nenhum modelo é baixado automaticamente.

## Executar com Docker

```bash
cp .env.example .env
docker compose up --build
```

Serviços:

- frontend: <http://localhost:3000>
- API: <http://localhost:8000>
- OpenAPI: <http://localhost:8000/docs>
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

Para iniciar também o Ollama:

```bash
docker compose --profile local-llm up --build
```

Depois, baixe manualmente um modelo compatível com seu hardware e configure `OLLAMA_MODEL`. A aplicação permanece disponível quando o Ollama estiver desligado.

## Executar sem Docker

Backend:

```bash
cd apps/api
uv sync --all-groups
uv run uvicorn big_tech_jobs_api.main:app --reload
```

Frontend, em outro terminal:

```bash
pnpm install
API_INTERNAL_URL=http://localhost:8000 pnpm dev:web
```

PostgreSQL e Redis ainda precisam estar acessíveis nas URLs configuradas.

## Qualidade

```bash
cd apps/api
uv run ruff check .
uv run mypy src
uv run pytest

cd ../..
pnpm lint:web
pnpm typecheck:web
pnpm test:web
pnpm build:web
```

O ambiente usado para criar a Fase 1A não possui Docker; portanto, a configuração foi validada estruturalmente e o workflow de CI executará `docker compose config`. A inicialização conjunta dos containers ainda deve ser confirmada antes da aprovação definitiva.

## Configuração

Copie `.env.example` para `.env`. O arquivo `.env` é ignorado pelo Git. Os valores versionados são apenas padrões locais e não são adequados para produção.

Decisões arquiteturais estão registradas em [DECISIONS.md](docs/DECISIONS.md).
