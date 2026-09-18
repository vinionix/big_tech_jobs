# Big Tech Jobs

Plataforma multiusuário para descoberta, recomendação e acompanhamento de vagas de tecnologia. O projeto está sendo construído em fatias verificáveis; as Fases 1A e 1B entregam a fundação, identidade e perfil profissional.

## Estado atual

Implementado:

- monorepo com FastAPI e Next.js;
- PostgreSQL e Redis no Docker Compose;
- health checks da API, banco, Redis e Ollama;
- frontend consumindo a API real por proxy same-origin;
- configuração de Alembic, testes e análise estática;
- Ollama opcional, sem fallback para APIs pagas.
- cadastro, login, logout e sessão opaca por cookie seguro;
- onboarding retomável, completude e perfil editável;
- experiências, projetos, formação, competências, idiomas, certificações, links e objetivos;
- quantidade, frequência, amplitude e score mínimo configuráveis por usuário;
- isolamento de recursos entre contas.

Ainda não implementado:

- busca e recomendação de vagas;
- LangGraph;
- adaptação de currículo;
- candidaturas e automação.

Consulte [ROADMAP.md](docs/ROADMAP.md) para o recorte das próximas entregas.

## Requisitos

- Docker com Compose v2; ou
- Python 3.12, `uv`, Node.js compatível com Next.js e `pnpm` para execução sem Docker.

O Ollama é opcional nesta etapa. Modelos locais não cobram por requisição, mas exigem memória e processamento da máquina. Nenhum modelo é baixado automaticamente.

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

Antes de iniciar a API pela primeira vez, aplique as migrações:

```bash
cd apps/api
uv run alembic upgrade head
```

No Docker Compose, essa migração é aplicada automaticamente antes do servidor. Depois, acesse `/cadastro`, crie uma conta e continue pelo onboarding. A quantidade de vagas aceita valores de 1 a 500; esse teto é uma proteção técnica configurada no contrato, não uma meta de produto.

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

O workflow de CI também aplica a migração em PostgreSQL real e valida `docker compose config`.

## Configuração

Copie `.env.example` para `.env`. O arquivo `.env` é ignorado pelo Git. Os valores versionados são apenas padrões locais e não são adequados para produção.

Decisões arquiteturais estão registradas em [DECISIONS.md](docs/DECISIONS.md).
