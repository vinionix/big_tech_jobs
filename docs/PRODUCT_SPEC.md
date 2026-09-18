# Prompt para o Codex — Big Tech Jobs

Trabalhe no repositório `https://github.com/vinionix/big_tech_jobs`.

O repositório está vazio. Crie do zero uma aplicação web full-stack, multiagente, chamada **Big Tech Jobs**, destinada a profissionais de tecnologia de qualquer nível de experiência. A plataforma deve encontrar, avaliar, recomendar, priorizar e acompanhar vagas de acordo com o perfil individual de cada usuário. Também deve preparar currículos adaptados e permitir automação assistida do preenchimento de candidaturas, sempre com revisão humana antes do envio final.

## Público-alvo e personalização

A aplicação não deve assumir uma persona fixa. Ela deve atender profissionais de tecnologia em diferentes momentos de carreira, incluindo:

- estudantes, aprendizes, estagiários e trainees;
- early career, new grad e profissionais juniores;
- profissionais plenos e seniores;
- staff, principal e especialistas;
- tech leads, gestores, heads e diretores;
- pessoas em transição de carreira ou buscando uma nova especialização.

O sistema deve suportar tanto carreiras técnicas quanto de liderança. Cargo, área, senioridade, localização, modalidade, pretensão, disponibilidade, preferência por empresas, relocação e sponsorship são características do perfil de cada usuário, não regras globais fixas.

Nenhuma região, senioridade ou cargo deve estar codificado como preferência universal. Cada usuário define seus próprios objetivos.

## Cadastro e construção do perfil

Crie autenticação e um onboarding guiado para que cada usuário construa seu perfil profissional. O formulário deve permitir preencher e editar:

- nome e informações de contato necessárias;
- localização atual, países de interesse e fusos horários aceitáveis;
- modalidades desejadas: presencial, híbrido e remoto;
- áreas de atuação e cargos-alvo;
- senioridade atual e senioridades buscadas;
- anos de experiência, sem usar isso isoladamente para determinar senioridade;
- experiências profissionais, responsabilidades e resultados;
- projetos pessoais, acadêmicos e profissionais;
- formação acadêmica;
- competências técnicas e comportamentais;
- idiomas e níveis de proficiência;
- certificações, publicações, portfólio e links profissionais;
- autorização de trabalho por país;
- necessidade de sponsorship;
- disponibilidade e interesse em relocação;
- faixa salarial desejada, sempre opcional e protegida;
- tipos e portes de empresa de interesse;
- setores e empresas preferidos ou bloqueados;
- preferências de cultura, benefícios e natureza do trabalho;
- currículo-base e, opcionalmente, diferentes currículos-base por objetivo profissional.

O usuário deve poder salvar o onboarding incompleto e continuar depois. Mostre a completude do perfil e explique quais informações melhorariam as recomendações, sem impedir o uso quando dados opcionais estiverem ausentes.

O sistema pode extrair sugestões de um currículo enviado, mas cada informação extraída deve ser apresentada para revisão antes de integrar o perfil. Nunca transforme inferências em fatos automaticamente.

## Quantidade configurável de vagas

Não limite o produto a cinco vagas por semana. O usuário deve escolher:

- quantas vagas deseja receber por busca ou período;
- frequência da busca;
- quantidade máxima apresentada em cada recomendação;
- se prefere poucas recomendações altamente aderentes ou uma busca mais ampla;
- score mínimo e critérios eliminatórios.

Não use `5` como constante ou regra de negócio. Limites técnicos de proteção contra abuso, sobrecarga ou rate limit podem existir, mas devem ser configuráveis, documentados e diferenciados da meta escolhida pelo usuário.

## Objetivo do produto

Criar um sistema cujo fluxo principal seja:

1. cadastrar ou autenticar o usuário;
2. construir e validar seu perfil profissional;
3. registrar seus objetivos e parâmetros de busca;
4. descobrir a quantidade configurada de vagas em fontes confiáveis;
5. normalizar e deduplicar os anúncios;
6. confirmar que a vaga continua aberta e que o link é oficial;
7. analisar a aderência entre vaga, perfil e currículo;
8. recomendar e ordenar as oportunidades mais próximas do perfil;
9. explicar pontos fortes, lacunas, incertezas e requisitos eliminatórios;
10. gerar uma versão adaptada do currículo sem inventar experiências;
11. preparar respostas para a candidatura;
12. solicitar aprovação humana quando necessário;
13. preencher a candidatura quando houver um adaptador compatível;
14. nunca enviar definitivamente sem confirmação explícita do usuário;
15. registrar o histórico e os resultados no dashboard.

## Stack recomendada

Use uma arquitetura de monorepo:

- `apps/api`: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 e Alembic;
- `apps/web`: Next.js com App Router, TypeScript, Tailwind CSS e componentes acessíveis;
- `packages/` ou módulos compartilhados quando isso realmente reduzir duplicação;
- PostgreSQL como banco principal;
- Redis para filas, locks e tarefas assíncronas;
- LangGraph para orquestração do workflow multiagente;
- Ollama como runtime local dos modelos de linguagem;
- Playwright somente para adaptadores de candidatura que exigirem navegador;
- Docker Compose para desenvolvimento local;
- pytest para o backend e Vitest/Testing Library para o frontend;
- ESLint, Prettier, Ruff e mypy ou Pyright para qualidade estática.

## Restrição obrigatória de custo dos agentes

Todo o sistema multiagente deve funcionar sem APIs pagas e sem gerar cobrança por token.

- Use somente modelos locais e de pesos abertos executados por meio do Ollama.
- O provedor padrão e único do MVP deve ser `ollama`.
- O nome do modelo deve ser configurável por `OLLAMA_MODEL`, sem acoplamento a um modelo específico.
- Não integre OpenAI, Anthropic, Gemini pago ou qualquer serviço que exija saldo, cartão ou cobrança por uso.
- Não trate testes gratuitos temporários ou créditos promocionais como solução gratuita.
- Não faça fallback silencioso para uma API externa.
- Se o modelo local estiver indisponível, a execução deve falhar de forma clara ou usar um fake determinístico somente em ambiente de desenvolvimento/teste.
- Mantenha uma interface interna de modelo para permitir evolução futura, mas não implemente provedores pagos.
- Minimize o uso de LLM: tarefas de filtragem, deduplicação, validação, cálculo de score e transição de estado devem ser determinísticas sempre que possível.
- Inclua o Ollama no ambiente de desenvolvimento ou documente claramente como conectá-lo ao Docker Compose, considerando que a configuração de GPU varia por máquina.
- O README deve informar requisitos aproximados de memória e permitir selecionar um modelo menor quando o computador não suportar o modelo recomendado.

Modelos locais não cobram por requisição, mas consomem recursos do próprio computador. A aplicação deve continuar navegável e permitir o uso das funções determinísticas mesmo quando o Ollama estiver desligado.

Todas as configurações devem vir de variáveis de ambiente. Crie apenas `.env.example`; nunca versione segredos.

Se alguma escolha da stack se mostrar incompatível durante a implementação, explique o motivo e proponha a menor mudança possível antes de alterar a direção.

## Arquitetura multiagente

Implemente agentes com responsabilidades claras e estado tipado. Evite criar agentes artificiais para tarefas determinísticas que podem ser funções comuns.

### 1. Orchestrator

- controla o workflow;
- mantém o estado da execução;
- decide quais nós executar;
- registra eventos, erros, tentativas e duração;
- permite retomar uma execução interrompida.

### 2. Job Discovery

- consulta fontes configuradas conforme objetivos, filtros, frequência e quantidade definidos pelo usuário;
- começa por fontes oficiais e integrações estruturadas, como páginas de carreiras, Greenhouse e Lever;
- guarda URL de origem, data da coleta e conteúdo bruto necessário para auditoria;
- respeita limites de requisição e termos aplicáveis;
- informa quando não conseguiu encontrar a quantidade solicitada com qualidade suficiente, em vez de preencher a meta com vagas ruins;
- não tenta contornar autenticação, CAPTCHA, bloqueios ou controles anti-bot.

### 3. Job Normalizer and Validator

- converte fontes diferentes para um modelo único;
- identifica empresa, cargo, senioridade, localização, modalidade, descrição, requisitos, data e URL;
- deduplica anúncios por identificadores externos, URL canônica e similaridade controlada;
- verifica se a vaga ainda está disponível;
- distingue vaga oficial de agregador;
- rejeita ou sinaliza anúncios incompletos e suspeitos.

### 4. Match Analyst

- compara a vaga com o perfil e os currículos cadastrados;
- produz score de 0 a 100 com justificativa rastreável;
- separa requisitos atendidos, parcialmente atendidos, ausentes e desconhecidos;
- diferencia requisito obrigatório de desejável;
- detecta possíveis eliminatórios, como senioridade, localização e autorização de trabalho;
- considera objetivos de carreira, preferências declaradas e transferibilidade de competências;
- funciona para qualquer senioridade e não penaliza automaticamente candidatos por terem experiência acima do exigido;
- permite comparar a vaga contra o currículo-base mais adequado ao objetivo profissional;
- não usa somente similaridade textual: aplique regras determinísticas para critérios objetivos e LLM para análise semântica estruturada.

Sugestão inicial de composição do score, configurável:

- 35% competências técnicas;
- 20% senioridade e experiência;
- 15% área e natureza do trabalho;
- 15% localização, remoto e relocação;
- 10% formação e idiomas;
- 5% preferências do usuário.

Não esconda incerteza. Quando um dado não existir, marque como desconhecido em vez de inferir.

As recomendações devem ser personalizadas por usuário. Exiba por que a vaga foi recomendada, quais informações do perfil influenciaram o resultado e quais mudanças nas preferências alterariam o ranking. Não use um ranking global igual para todos.

### 5. Resume Tailor

- seleciona somente fatos presentes no perfil aprovado e no currículo-base escolhido;
- reordena e reformula conteúdo para enfatizar experiências relevantes;
- nunca inventa cargo, projeto, tecnologia, duração, resultado ou métrica;
- gera uma representação estruturada e uma versão visualizável;
- mantém vínculo entre cada afirmação adaptada e sua evidência original;
- mostra um diff entre currículo-base e currículo adaptado;
- exige aprovação antes de usar a nova versão.

A adaptabilidade de currículo é uma funcionalidade central e não deve ser removida ou reduzida a uma simples troca de palavras-chave. O sistema deve permitir múltiplos currículos-base, versões por vaga, histórico de alterações, restauração de versões e exportação. Toda adaptação deve preservar veracidade, coerência cronológica e identidade profissional.

### 6. Application Planner

- extrai perguntas e campos previstos;
- classifica cada resposta como conhecida, sugerida ou dependente de confirmação;
- cria um checklist da candidatura;
- pausa quando faltarem dados.

### 7. Application Executor

- use um padrão de adaptadores por ATS ou fonte;
- comece com modo `dry-run` e pelo menos um adaptador demonstrável em ambiente controlado;
- preenche somente campos aprovados;
- captura evidências do que foi preenchido;
- nunca contorna CAPTCHA ou mecanismos de segurança;
- nunca envia a candidatura sem uma ação explícita e recente do usuário no frontend;
- se a estrutura da página mudar, interrompe o fluxo e registra erro em vez de improvisar.

### 8. Application Tracker

- registra status e histórico;
- suporta: `discovered`, `validated`, `analyzed`, `shortlisted`, `resume_ready`, `awaiting_review`, `ready_to_apply`, `applying`, `applied`, `interview`, `rejected`, `offer`, `withdrawn` e `failed`;
- permite notas, próximas ações e datas;
- calcula métricas sem transformar quantidade de candidaturas em objetivo cego.

## Aprovação humana obrigatória

O sistema deve pausar e pedir confirmação para:

- pretensão salarial;
- autorização de trabalho e sponsorship;
- disponibilidade para mudança ou início;
- deficiência, raça, gênero, veteran status e outras perguntas demográficas;
- antecedentes e declarações legais;
- acordos, termos e consentimentos;
- qualquer resposta com baixa confiança;
- qualquer informação ausente do perfil;
- versão final do currículo;
- envio definitivo da candidatura.

Dados demográficos opcionais devem permanecer sem resposta por padrão. Não armazene credenciais de plataformas de vagas. Não registre cookies, tokens, documentos pessoais ou respostas sensíveis em logs.

## Frontend obrigatório

Crie uma interface responsiva e funcional. Não entregue apenas telas estáticas.

### Páginas mínimas

1. **Autenticação e onboarding**
   - criação de conta e login;
   - formulário guiado e salvamento parcial;
   - importação assistida de currículo;
   - revisão das informações extraídas;
   - indicador de completude do perfil.

2. **Perfil profissional**
   - visualização e edição das informações cadastradas;
   - experiências, projetos, competências, formação, idiomas e certificações;
   - objetivos de carreira e preferências;
   - autorização de trabalho, sponsorship e relocação tratados como dados protegidos;
   - gerenciamento de múltiplos currículos-base.

3. **Dashboard**
   - número de vagas descobertas, analisadas e candidaturas;
   - funil por status;
   - recomendações mais aderentes ao perfil;
   - tarefas aguardando revisão;
   - erros recentes dos agentes.

4. **Vagas**
   - tabela ou cards com busca, ordenação e filtros;
   - filtros por empresa, função, nível, região, remoto, sponsorship, score e status;
   - indicação visual de vaga expirada, duplicada ou não validada.

5. **Detalhes da vaga**
   - descrição e origem;
   - score e decomposição;
   - requisitos atendidos, lacunas, desconhecidos e eliminatórios;
   - evidências usadas na análise;
   - ações para favoritar, descartar ou iniciar candidatura.

6. **Currículos**
   - cadastro do currículo-base;
   - versões adaptadas por vaga;
   - comparação entre versões;
   - aprovação ou rejeição da versão adaptada.

7. **Central de revisão**
   - fila de perguntas pendentes;
   - valor sugerido, confiança e origem da sugestão;
   - edição e aprovação individual;
   - confirmação final separada para envio.

8. **Candidaturas**
   - quadro Kanban e visualização em lista;
   - linha do tempo por candidatura;
   - notas e próximas ações.

9. **Execuções dos agentes**
   - status, etapas, duração e erros;
   - dados suficientes para depuração, sem expor raciocínio privado do modelo ou segredos.

10. **Configurações**
   - áreas, cargos, países e níveis desejados;
   - empresas prioritárias;
   - frequência, quantidade desejada e amplitude das buscas;
   - score mínimo, critérios eliminatórios e equilíbrio entre precisão e variedade;
   - pesos do score;
   - status do Ollama, modelo local selecionado e teste de conexão;

Inclua estados de loading, vazio e erro. Garanta navegação por teclado, labels acessíveis e contraste adequado.

## Modelos de dados mínimos

Crie modelos e migrações para:

- `UserAccount`;
- `UserProfile`;
- `CareerGoal` e `JobSearchPreference`;
- `WorkExperience`, `Project`, `Education`, `Skill`, `Language` e `Certification`;
- `Resume` e `ResumeVersion`;
- `JobSource`;
- `Company`;
- `JobPosting`;
- `JobRequirement`;
- `JobMatchAnalysis`;
- `Application`;
- `ApplicationAnswer`;
- `ApprovalRequest`;
- `AgentRun` e `AgentStep`;
- `AuditEvent`;
- preferências e configurações de busca.

Inclua timestamps, estados explícitos, restrições de unicidade e relacionamentos. Não armazene tudo como JSON; use colunas relacionais para campos consultados e JSON apenas para payloads variáveis ou evidências.

Todos os dados de perfil, currículo, análise e candidatura devem pertencer explicitamente a uma conta. Consultas e endpoints não podem permitir acesso cruzado entre usuários.

## API mínima

Implemente endpoints versionados para:

- autenticação e sessão;
- onboarding, perfil profissional e completude;
- objetivos e preferências de busca, incluindo quantidade e frequência;
- vagas, filtros e detalhes;
- iniciar busca manual;
- recomendações personalizadas;
- iniciar ou consultar análise;
- currículos e versões;
- criar candidatura;
- listar e responder solicitações de aprovação;
- executar `dry-run` de candidatura;
- confirmar envio;
- consultar execuções e eventos;
- dashboard e métricas;
- preferências do usuário.

Use contratos tipados, paginação, validação consistente e códigos HTTP adequados. Gere OpenAPI automaticamente.

## Observabilidade e confiabilidade

- logs estruturados com correlation ID;
- idempotência em coleta, análise e candidatura;
- timeout e retry apenas em operações seguras;
- tratamento explícito de falhas parciais;
- métricas básicas de duração, sucesso e erro;
- histórico auditável de alterações importantes;
- mocks ou fakes determinísticos para o modelo local, fontes e navegador nos testes;
- nenhum teste automatizado deve depender de enviar candidatura real.

## Segurança

- valide uploads e limite tamanho e tipo;
- sanitize conteúdo de vagas antes de exibir;
- trate descrições de vagas como entrada não confiável e possível prompt injection;
- nunca permita que instruções presentes em uma vaga alterem regras do sistema;
- use CORS restritivo e configuração por ambiente;
- não exponha stack traces, segredos ou dados sensíveis no frontend;
- implemente autenticação e autorização, pois a aplicação deve suportar contas e perfis distintos;
- aplique isolamento de dados por usuário em todas as consultas e operações;
- proteja informações de salário, autorização de trabalho, sponsorship e relocação.

## Forma de implementação

Antes de codificar:

1. confirme que o repositório continua vazio ou inspecione qualquer mudança nova;
2. escreva um plano curto por fases;
3. registre as principais decisões arquiteturais no `README.md`;
4. crie o esqueleto executável antes das funcionalidades avançadas.

Implemente em fatias verticais funcionais, sem gerar dezenas de arquivos desconectados.

### Fase 1 — fundação e fluxo vertical

- monorepo, Docker Compose, API, frontend, PostgreSQL, Redis e integração local com Ollama;
- modelos e primeira migração;
- criação de conta, login, onboarding e perfil profissional editável;
- preferências de busca com quantidade configurável;
- fonte fake de vagas com dados de demonstração;
- descoberta, normalização, deduplicação, análise e recomendação personalizada usando interfaces substituíveis;
- dashboard, recomendações, lista e detalhes da vaga consumindo a API real;
- testes essenciais;
- instruções de execução no README.

### Fase 2 — fontes reais e currículo

- conectores estruturados para fontes escolhidas;
- importação assistida de perfil e múltiplos currículos-base;
- análise rastreável e adaptação de currículo por vaga;
- central de revisão;
- tratamento de prompt injection.

### Fase 3 — candidatura assistida

- Application Planner;
- adaptadores de ATS;
- Playwright em `dry-run`;
- checkpoints e aprovações humanas;
- histórico e evidências.

### Fase 4 — automação operacional

- agendamento configurável;
- filas robustas e retomada;
- métricas, alertas e melhorias de UX;
- documentação de implantação.

Ao final de cada fase:

- execute formatadores, linters, checagem de tipos e testes;
- corrija as falhas encontradas;
- informe exatamente o que funciona, o que é simulado e o que ainda não foi implementado;
- não afirme que uma integração real funciona sem testá-la;
- mantenha o projeto executável.

## Critérios de aceitação da primeira entrega

A primeira entrega será aceita quando:

- `docker compose up --build` iniciar os serviços documentados;
- o frontend abrir e consumir o backend, sem dados codificados diretamente nos componentes;
- for possível criar uma conta, preencher o perfil e editar objetivos profissionais;
- for possível escolher a quantidade desejada de vagas e disparar uma busca fake;
- a busca respeitar a quantidade configurada ou explicar por que encontrou menos vagas válidas;
- as vagas forem persistidas e exibidas como recomendações personalizadas no dashboard;
- vagas repetidas não forem persistidas novamente;
- dois perfis diferentes puderem receber rankings diferentes para a mesma vaga;
- for possível abrir uma vaga e visualizar score, justificativa, evidências e lacunas;
- uma execução dos agentes puder ser acompanhada;
- os testes principais passarem;
- existir `.env.example`, README claro e nenhuma credencial versionada.

## Restrições de escopo

- Não implemente envio real de candidatura na primeira fase.
- Não adicione dependência de APIs pagas, cobrança por token ou créditos promocionais.
- Não use LinkedIn scraping como dependência do MVP.
- Não invente resultados, integrações ou cobertura de testes.
- Não sacrifique rastreabilidade para criar uma demonstração visual.
- Não crie microserviços sem necessidade; comece com um monólito modular e workers separados apenas quando houver benefício operacional claro.
- Não faça alterações fora deste repositório.

Comece inspecionando o estado atual do repositório, apresente o plano da Fase 1 e então implemente essa fase de maneira autônoma. Faça perguntas apenas quando uma decisão realmente bloquear a implementação; caso contrário, use as escolhas recomendadas acima e documente as suposições.
