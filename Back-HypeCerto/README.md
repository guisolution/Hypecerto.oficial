# HypeCerto

Plataforma SaaS de automação de marketing: o usuário cria postagens, agenda a publicação em redes sociais (Facebook e Instagram via Graph API da Meta), gera legendas e ideias com IA e acompanha resultados em um dashboard.

O repositório é um monorepo com duas aplicações independentes:

| Parte | Pasta | Stack |
|---|---|---|
| Back-end (API REST) | `Back-HypeCerto/` | Python 3.10+, FastAPI, SQLAlchemy, PostgreSQL (Supabase), APScheduler |
| Front-end (SPA) | `Front-HypeCerto/` | React 19, TypeScript, Vite, Tailwind, Wouter |

---

## Estrutura do repositório

```
Hypecerto.oficial/
├── Back-HypeCerto/              # API FastAPI
│   ├── run.py                   # Ponto de entrada (uvicorn)
│   ├── requirements.txt         # Dependências de produção
│   ├── requirements-dev.txt     # pytest, flake8 etc.
│   ├── .env.example             # Modelo de variáveis de ambiente
│   ├── scripts/
│   │   └── seed.py              # Popula o banco com dados iniciais
│   └── app/
│       ├── main.py              # App FastAPI, CORS, routers, scheduler
│       ├── config.py            # Configurações (pydantic-settings)
│       ├── database/            # Conexão SQLAlchemy (engine, sessão)
│       ├── models/              # Modelos ORM (tabelas do Supabase)
│       ├── schemas/             # Schemas Pydantic (entrada/saída)
│       ├── routers/             # Endpoints: auth, posts, agendamentos,
│       │                        #   meta, ia, channels, projetos, resultados
│       ├── services/            # Regras de negócio: auth_service, crypto,
│       │                        #   dependencies, ia_service, rate_limit,
│       │                        #   scheduler
│       └── integrations/
│           └── meta_api.py      # Graph API (Facebook/Instagram), modo mock ou real
├── Front-HypeCerto/             # SPA React
│   ├── client/                  # Código-fonte (src/pages, components, lib, hooks)
│   ├── shared/                  # Tipos e utilitários compartilhados
│   └── package.json
├── testes/                      # Testes automatizados (pytest e vitest)
├── evidencias/                  # Saídas de testes, build e capturas de tela
├── Fotos para tela de login/    # Imagens de apoio ao layout
└── .github/workflows/           # CI (lint + testes)
```

---

## Como rodar

### Pré-requisitos

- Python 3.10+
- Node.js e pnpm
- Um banco PostgreSQL (o projeto usa o Supabase)

### Back-end

```bash
cd Back-HypeCerto

python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

pip install -r requirements.txt

cp .env.example .env            # depois edite o .env
python scripts/seed.py          # opcional: dados iniciais
python run.py
```

A API sobe em `http://localhost:8000`. Documentação interativa em `/docs` (Swagger) e `/redoc`.

O ambiente virtual (`venv/`) é local de cada máquina e está no `.gitignore`; não deve ser versionado.

### Variáveis de ambiente (`Back-HypeCerto/.env`)

Use o `.env.example` como modelo. Nunca versione o `.env`.

| Variável | Descrição |
|---|---|
| `DATABASE_URL` | String de conexão do PostgreSQL |
| `SECRET_KEY` | Chave do JWT (obrigatória em produção; gere com `secrets.token_urlsafe(48)`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Validade do token (padrão 60) |
| `ENVIRONMENT` | `development` ativa o auto-reload |
| `ALLOWED_ORIGINS` | Origens liberadas no CORS (ex.: `http://localhost:5173`) |
| `MAX_UPLOAD_MB` | Tamanho máximo de upload de mídia |
| `USE_MOCK_META_API` | `True` simula a publicação; `False` usa a Graph API real |
| `META_APP_ID` / `META_APP_SECRET` / `META_API_VERSION` | Credenciais e versão da Graph API |
| `OPENAI_API_KEY` | Opcional; sem ela a IA responde em modo demonstração |
| `PUBLIC_BASE_URL` | URL pública da API (usada em callbacks OAuth) |

### Front-end

```bash
cd Front-HypeCerto
pnpm install
pnpm run dev
```

O Vite mostra no terminal o endereço local (por padrão `http://localhost:5173`). Para build de produção: `pnpm run build`.

Páginas: `/` (landing), `/login`, `/signup`, `/forgot-password` e, após login, `/dashboard`, `/create`, `/publish`, `/results`, `/channels` e `/guide`.

---

## Endpoints da API

Todos os endpoints protegidos exigem o header `Authorization: Bearer <token>`.

| Grupo | Prefixo | Principais rotas |
|---|---|---|
| Autenticação | `/auth` | `POST /login`, `POST /signup`, `GET /me`, `POST /logout`, `POST /forgot-password`, `POST /oauth/facebook` |
| Postagens | `/posts` | CRUD em `/posts` e `/posts/{id}`, `POST /posts/{id}/midia` (upload) |
| Projetos | `/projetos` | CRUD em `/projetos` e `/projetos/{id}` |
| Agendamentos | `/agendamentos` | CRUD em `/agendamentos` e `/agendamentos/{id}` |
| Meta API | `/meta` | `POST /publicar`, `POST /publicar-direto`, `GET /status`, `GET /callback/facebook` |
| IA | `/ia` | `POST /legenda`, `POST /ideias`, `GET /historico`, `DELETE /historico/{id}` |
| Canais | `/channels` | `GET /channels`, `POST /conectar`, `GET /plataformas`, `DELETE /{id}` |
| Resultados | `/resultados` | `GET /dashboard`, `GET /metricas`, `GET /relatorios`, `POST /relatorios/gerar`, `GET /projetos` |

A lista completa e atualizada está sempre em `/docs`.

---

## Publicação: modo mock x real

- **Mock** (`USE_MOCK_META_API=True`): simula o envio, atualiza o status do agendamento e gera um `post_id_externo` fictício. Use em desenvolvimento e testes.
- **Real** (`USE_MOCK_META_API=False`): exige `access_token` válido da Meta (via OAuth) e publica pela Graph API.

O `APScheduler` roda a cada 60 segundos, busca agendamentos com `status_envio = "agendado"` e `data_agendada <= agora`, publica e registra `status_envio`, `data_publicacao_real`, `post_id_externo` e, em caso de erro, `erro_mensagem` e `tentativas`.

---

## Arquitetura

```
Front-end (React + Vite + Wouter)
        │  HTTP REST (JSON) + JWT
        ▼
Back-end (FastAPI)
  routers → services → models (SQLAlchemy)
  scheduler (APScheduler) ──► integrations/meta_api ──► Graph API (Meta)
        │
        ▼
PostgreSQL (Supabase)
```

O front-end se comunica apenas com a API REST. O back-end é o único componente que acessa o banco e as APIs externas, o que mantém as credenciais fora do navegador.

---

## Testes e CI

```bash
# Back-end (a partir da raiz do repositório)
pip install -r Back-HypeCerto/requirements.txt -r Back-HypeCerto/requirements-dev.txt
pytest testes/

# Front-end
cd Front-HypeCerto && pnpm test
```

O workflow `.github/workflows/python-app.yml` roda em push e pull request para `main`: instala as dependências, executa o flake8 (erros de sintaxe bloqueiam o build) e roda o `pytest`. As saídas de testes e capturas de tela estão em `evidencias/`.

---

## Fluxo de trabalho no Git

- `main` é a branch estável; o desenvolvimento acontece em branches de feature (`feature`, `feature/<nome>`).
- Mudanças entram por Pull Request, com o CI rodando antes do merge.
- Commits seguem o padrão `tipo(escopo): descrição` (`feat`, `fix`, `chore`, `docs`).
- Arquivos locais ficam fora do Git: `venv/`, `.env`, `node_modules/`, `uploads/`.

---

## Origem do front-end

O front-end foi iniciado a partir de um template que incluía um servidor Node.js (Express/tRPC) e o Drizzle ORM (pastas `server/` e `drizzle/`). Como o back-end do projeto é a API FastAPI, essas pastas eram redundantes e foram removidas no commit `c66bf47`. O front consome apenas a API REST do back-end.

---

## Equipe

- Guilherme de Paula Inocêncio ([@guisolution](https://github.com/guisolution))
- Felipe ([@FellipeOliveirax](https://github.com/FellipeOliveirax))
