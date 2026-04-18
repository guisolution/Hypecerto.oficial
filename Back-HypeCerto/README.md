# 🚀 HypeCerto — Backend API

**Plataforma SaaS de Automação de Marketing**  
Backend desenvolvido em **Python + FastAPI**, conectado ao **Supabase (PostgreSQL)**,
com integração à **Graph API da Meta** e geração de conteúdo via **IA**.

---

## 📁 Estrutura do Projeto

```
backend/
├── run.py                          # Ponto de entrada
├── requirements.txt                # Dependências Python
├── .env.example                    # Variáveis de ambiente (copie para .env)
├── scripts/
│   └── seed.py                     # Popula banco com dados iniciais
└── app/
    ├── main.py                     # FastAPI app, CORS, routers, scheduler
    ├── config.py                   # Configurações centralizadas (pydantic-settings)
    ├── database/
    │   └── connection.py           # SQLAlchemy engine + SessionLocal
    ├── models/
    │   └── models.py               # Modelos ORM (tabelas existentes do Supabase)
    ├── schemas/
    │   └── schemas.py              # Schemas Pydantic (request/response)
    ├── routers/
    │   ├── auth.py                 # POST /auth/login, /signup, /me
    │   ├── posts.py                # CRUD /posts + upload de mídia
    │   ├── agendamentos.py         # CRUD /agendamentos
    │   ├── meta.py                 # POST /meta/publicar (mock ou real)
    │   ├── ia.py                   # POST /ia/legenda, /ia/ideias
    │   ├── channels.py             # /channels (contas sociais)
    │   ├── projetos.py             # CRUD /projetos
    │   └── resultados.py           # /resultados/dashboard, metricas, relatorios
    ├── services/
    │   ├── auth_service.py         # JWT, bcrypt, autenticação
    │   ├── dependencies.py         # FastAPI Dependency: get_current_user
    │   ├── scheduler.py            # APScheduler: publicação automática
    │   └── ia_service.py           # Geração de conteúdo (OpenAI ou demo)
    └── integrations/
        └── meta_api.py             # Graph API: Facebook + Instagram (mock/real)
```

---

## ⚙️ Como Rodar

### 1. Pré-requisitos
- Python 3.10+
- Conta no Supabase com banco já configurado

### 2. Instalação

```bash
# Clonar o projeto
cd backend/

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env`:

```env
DATABASE_URL=postgresql://postgres:SUA_SENHA@db.SEU_PROJECT.supabase.co:5432/postgres
SECRET_KEY=chave-secreta-super-segura
USE_MOCK_META_API=True          # False para integração real
OPENAI_API_KEY=sk-...           # Opcional (IA de verdade)
ALLOWED_ORIGINS=http://localhost:5173,https://seudominio.com
```

### 4. Popular banco com dados iniciais

```bash
python scripts/seed.py
```

Isso cria:
- ✅ 6 plataformas (Facebook, Instagram, TikTok, YouTube, WhatsApp, LinkedIn)
- ✅ 3 planos (Grátis, Pro, Enterprise)
- ✅ Usuário de teste: `admin@hypecerto.com` / `hypecerto123`

### 5. Rodar o servidor

```bash
python run.py
```

Acesse:
Hypecerto 'http://localhost:3000'
- **API:** `http://localhost:8000`
- **Documentação interativa:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

FRONT END
pnpm install
pnpm run dev




---

## 📡 Endpoints da API

### 🔐 Autenticação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/auth/login` | Login com email/senha → retorna JWT |
| POST | `/auth/signup` | Cadastro de novo usuário |
| GET | `/auth/me` | Dados do usuário logado |
| POST | `/auth/logout` | Logout (invalida sessão no frontend) |
| POST | `/auth/forgot-password` | Inicia recuperação de senha |

**Exemplo — Login:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@hypecerto.com", "password": "hypecerto123"}'
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "nome": "Admin HypeCerto",
    "email": "admin@hypecerto.com"
  }
}

Register
{
    "nome": "HypeCerto",
    "email": "admin@hypecerto.com",
    "password": "teste123",
    "confirmPassword": "teste123"
 
}
```

---

### 📝 Postagens

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/projetos` | Lista postagens (filtro: status, projeto_id) |
| POST | `/projetos` | Cria nova postagem |
| GET | `/projetos/{id}` | Busca postagem por ID |
| PUT | `/projetos/{id}` | Edita postagem |
| DELETE | `/projetos/{id}` | Exclui postagem |
| POST | `/projetos/{id}/midia` | Upload de imagem/vídeo |

**Exemplo — Criar postagem:**
```bash
curl -X POST http://localhost:8000/posts \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d 
  {
  "nome_do_projeto": "Teste",
  "area_do_projeto": "Software",
  "responsavel": "Felipe",
  "descricao": "postagem"
}
```

---

### 📅 Agendamentos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/agendamentos` | Lista agendamentos (filtros: status_envio, data) |
| POST | `/agendamentos` | Cria novo agendamento |
| GET | `/agendamentos/{id}` | Busca agendamento |
| PUT | `/agendamentos/{id}` | Edita data/status |
| DELETE | `/agendamentos/{id}` | Cancela agendamento |

**Exemplo — Agendar postagem:**
```bash
curl -X POST http://localhost:8000/agendamentos \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "postagem_id": 1,
    "conta_social_id": 2,
    "data_agendada": "2025-06-01T14:00:00Z"
  }'
```

---

### 📣 Meta API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/meta/publicar` | Publica agendamento agora (mock ou real) |
| POST | `/meta/publicar-direto` | Publica postagem diretamente |
| GET | `/meta/status` | Status da integração Meta |

**Exemplo — Publicar:**
```bash
curl -X POST http://localhost:8000/meta/publicar \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"agendamento_id": 1}'
```

**Resposta (modo mock):**
```json
{
  "success": true,
  "message": "Publicado com sucesso em facebook",
  "post_id_externo": "mock_facebook_a3f9d12b4c",
  "mock": true
}
```

---

### 🤖 Inteligência Artificial

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/ia/legenda` | Gera legenda para postagem |
| POST | `/ia/ideias` | Gera ideias de conteúdo |
| GET | `/ia/historico` | Histórico de sugestões geradas |

**Exemplo — Gerar legenda:**
```bash
curl -X POST http://localhost:8000/ia/legenda \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tema": "promoção de matrícula em curso de inglês",
    "plataforma": "instagram",
    "tom": "engajador",
    "incluir_hashtags": true
  }'
```

**Resposta:**
```json
{
  "id": 12,
  "tipo": "legenda",
  "conteudo_gerado": "✨ Sua jornada no inglês começa AGORA!\n\n🎓 Garanta 50% OFF na matrícula...\n\n#Inglês #Desconto #Idiomas",
  "criado_em": "2025-05-01T10:30:00"
}
```

---

### 📊 Resultados e Métricas

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/resultados/dashboard` | Métricas consolidadas do dashboard |
| GET | `/resultados/metricas` | Lista métricas por postagem |
| GET | `/resultados/relatorios` | Lista relatórios gerados |
| POST | `/resultados/relatorios/gerar` | Gera novo relatório |
| GET | `/resultados/projetos` | Progresso dos projetos |

---

### 📱 Canais / Contas Sociais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/channels` | Lista contas conectadas |
| POST | `/channels/conectar` | Conecta conta social |
| DELETE | `/channels/{id}` | Desconecta conta |
| GET | `/channels/plataformas` | Lista plataformas suportadas |

---

## 🔐 Autenticação nas Requisições

Todos os endpoints protegidos exigem o header:

```
Authorization: Bearer SEU_JWT_TOKEN
```

No frontend React (Axios):
```typescript
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
});
```

---

## 🔥 Modo Mock vs. Real (Meta API)

### Modo Mock (`USE_MOCK_META_API=True`)
- Simula o envio para Facebook/Instagram
- Atualiza `status_envio = "publicado"` no banco
- Gera um `post_id_externo` fictício
- **Use para desenvolvimento e testes**

### Modo Real (`USE_MOCK_META_API=False`)
- Requer `access_token` válido da Meta (via OAuth)
- Facebook: `POST https://graph.facebook.com/v18.0/{page_id}/feed`
- Instagram: cria container de mídia → publica
- **Use em produção com credenciais reais da Meta**

---

## ⏰ Agendamento Automático

O `APScheduler` roda a cada **60 segundos** em background e:

1. Busca todos os agendamentos com `status_envio = "agendado"` e `data_agendada <= agora`
2. Chama `executar_publicacao()` para cada um
3. Atualiza `status_envio`, `data_publicacao_real`, `post_id_externo`
4. Em caso de erro, registra `erro_mensagem` e mantém histórico de `tentativas`

---

## 🗄️ Tabelas do Banco (Supabase)

O backend conecta diretamente nas tabelas existentes — **sem recriar estrutura**:

| Tabela | Uso |
|--------|-----|
| `usuarios` | Autenticação e perfil |
| `contas_sociais` | Tokens e IDs das redes sociais |
| `plataformas` | Facebook, Instagram, etc. |
| `projetos` | Organização dos projetos de marketing |
| `postagens` | Conteúdo das postagens |
| `agendamentos` | Fila de publicação + status |
| `midias` | Imagens e vídeos das postagens |
| `metricas` | Curtidas, alcance, comentários |
| `relatorios` | Relatórios consolidados |
| `sugestoes_ia` | Legendas e ideias geradas pela IA |
| `tags` | Etiquetas para classificar postagens |
| `postagem_tags` | Relação N:N postagem ↔ tag |
| `planos` | Planos de assinatura |
| `assinaturas` | Assinaturas dos usuários |
| `automacoes` | Regras de automação |
| `interacoes` | Comentários e mensagens recebidos |
| `configuracoes_usuario` | Preferências do usuário |

---

---

# 📄 DOCUMENTAÇÃO ACADÊMICA

---

## 20. Arquitetura do Sistema

A arquitetura do HypeCerto segue o modelo de três camadas separadas por responsabilidade:

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                      │
│        Vite + TypeScript + Tailwind + Wouter            │
│   Login │ Dashboard │ Create │ Publish │ Results        │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP REST (JSON) / Axios
                       │ Authorization: Bearer JWT
┌──────────────────────▼──────────────────────────────────┐
│                  BACKEND (FastAPI)                       │
│                                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │   Auth   │ │  Posts   │ │ Agendas  │ │   Meta   │   │
│  │  Router  │ │  Router  │ │  Router  │ │  Router  │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                 │
│  │    IA    │ │Channels  │ │Resultados│                 │
│  │  Router  │ │  Router  │ │  Router  │                 │
│  └──────────┘ └──────────┘ └──────────┘                 │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │              Serviços Internos                   │    │
│  │  auth_service │ ia_service │ scheduler           │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │           APScheduler (60s interval)             │    │
│  │   Busca agendados → Publica → Atualiza banco    │    │
│  └─────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────┘
                       │ SQLAlchemy ORM
┌──────────────────────▼──────────────────────────────────┐
│              SUPABASE (PostgreSQL)                       │
│  usuarios │ postagens │ agendamentos │ contas_sociais    │
│  midias │ metricas │ sugestoes_ia │ relatorios │ ...    │
└──────────────────────┬──────────────────────────────────┘
                       │ httpx (Graph API)
┌──────────────────────▼──────────────────────────────────┐
│             META PLATFORMS API                           │
│  Facebook: POST /v18.0/{page_id}/feed                   │
│  Instagram: POST /v18.0/{ig_user_id}/media              │
│             POST /v18.0/{ig_user_id}/media_publish      │
└─────────────────────────────────────────────────────────┘
```

O frontend comunica-se exclusivamente com o backend via API REST no padrão JSON, utilizando o cabeçalho `Authorization: Bearer <token>` para autenticação. O backend, por sua vez, é o único componente que acessa diretamente o banco de dados e as APIs externas, garantindo isolamento de responsabilidades e segurança das credenciais.

---

## 22.2 Implementação do Backend

### Tecnologias Utilizadas

O backend do HypeCerto foi implementado com **Python 3.10+** e o framework **FastAPI**, escolhido por sua alta performance, suporte nativo a operações assíncronas e geração automática de documentação OpenAPI. A camada de acesso a dados utiliza **SQLAlchemy 2.0** como ORM, conectado ao banco **PostgreSQL** hospedado no **Supabase**.

A autenticação é implementada com **JWT (JSON Web Tokens)** através da biblioteca `python-jose`, e as senhas são armazenadas com hash seguro usando `bcrypt` via `passlib`. Tokens JWT são gerados no login com validade configurável (padrão: 7 dias) e validados em cada requisição por meio de uma FastAPI Dependency (`get_current_user`), que extrai o token do cabeçalho `Authorization: Bearer`.

### Organização dos Módulos

O projeto segue arquitetura em camadas:

- **`routers/`**: Definem os endpoints REST, recebem as requisições e delegam às camadas de serviço.
- **`services/`**: Contêm a lógica de negócio (autenticação, agendamento, IA).
- **`models/`**: Modelos SQLAlchemy mapeados às tabelas existentes no Supabase — sem recriar estrutura.
- **`schemas/`**: Modelos Pydantic para validação de entrada e serialização de saída.
- **`integrations/`**: Integração com APIs externas (Meta Graph API).
- **`database/`**: Configuração da conexão com PostgreSQL.

### Endpoints Implementados

O sistema expõe os seguintes grupos de endpoints:

**Autenticação (`/auth`):** `POST /login` autentica o usuário verificando o email na tabela `usuarios` e comparando a senha com o hash armazenado via bcrypt; em caso de sucesso, retorna um JWT. `POST /signup` cria novo registro em `usuarios` e retorna token imediatamente. `GET /me` valida o JWT e retorna os dados do usuário autenticado.

**Postagens (`/posts`):** CRUD completo sobre a tabela `postagens`. A criação (`POST /posts`) recebe título e conteúdo, salva com `status = "rascunho"` e retorna o objeto criado. A edição suporta alteração de título, conteúdo, status e projeto vinculado. O endpoint `POST /posts/{id}/midia` aceita upload multipart de imagens e vídeos, salva em disco e registra o caminho na tabela `midias`.

**Agendamentos (`/agendamentos`):** `POST /agendamentos` cria um agendamento vinculando uma postagem a uma conta social com data/hora desejada, inserindo com `status_envio = "agendado"`. O scheduler monitora esses registros automaticamente e os publica no horário correto.

**Meta API (`/meta`):** `POST /meta/publicar` recebe um `agendamento_id` e executa a publicação imediata, seja em modo mock (simulado) ou real (Graph API da Meta). O modo é controlado pela variável `USE_MOCK_META_API` no arquivo `.env`.

**Inteligência Artificial (`/ia`):** `POST /ia/legenda` recebe tema, plataforma e tom, chama a API OpenAI (ou retorna template demonstrativo), salva o resultado em `sugestoes_ia` e retorna o conteúdo gerado. `POST /ia/ideias` opera de forma análoga, gerando listas de ideias para um nicho de mercado.

**Resultados (`/resultados`):** `GET /resultados/dashboard` agrega dados das tabelas `postagens`, `agendamentos` e `metricas` para retornar os indicadores exibidos no painel principal: total de postagens, publicações, agendamentos ativos e atividade semanal.

### Serviço de Agendamento Automático

O componente `APScheduler` é inicializado junto com a aplicação (via `lifespan` do FastAPI) e executa uma verificação a cada 60 segundos. A rotina consulta a tabela `agendamentos` filtrando registros com `status_envio = "agendado"` e `data_agendada <= datetime.now()`, e para cada resultado chama o serviço de publicação Meta, atualizando os campos `status_envio`, `data_publicacao_real` e `post_id_externo` conforme o resultado da operação.

---

## 22.3 Integração Frontend e Backend

### Protocolo de Comunicação

A comunicação entre frontend e backend é realizada exclusivamente via **API REST**, com troca de dados no formato **JSON**. O frontend React utiliza a biblioteca **Axios** (ou `fetch` nativo) para realizar as requisições HTTP às rotas do backend FastAPI. O backend possui **CORS habilitado**, configurado para aceitar requisições das origens definidas na variável `ALLOWED_ORIGINS`, o que permite que o navegador autorize as chamadas cross-origin durante o desenvolvimento e produção.

### Fluxo de Autenticação

Ao submeter o formulário de login (`Login.tsx`), o frontend realiza uma requisição `POST /auth/login` com email e senha. O backend valida as credenciais, gera um JWT e retorna o token junto com os dados do usuário. O frontend armazena o token no `localStorage` e o inclui no cabeçalho `Authorization: Bearer <token>` em todas as requisições subsequentes. Rotas protegidas no backend validam o token antes de processar qualquer operação.

### Fluxo de Criação e Publicação de Postagem

O fluxo completo inicia na tela `Create.tsx`, onde o usuário preenche nome do projeto, área, responsável e descrição. O frontend serializa esses dados e envia `POST /posts` ao backend, que salva a postagem na tabela `postagens` com status `"rascunho"`. Em seguida, o usuário é redirecionado para `Publish.tsx`, onde seleciona os canais desejados e uma imagem opcional. Ao clicar em publicar, o frontend envia `POST /agendamentos` com o `postagem_id`, `conta_social_id` e a data/hora desejada. O backend cria o agendamento com status `"agendado"`, e o scheduler cuida da publicação automática no horário correto. Se o usuário desejar publicação imediata, o frontend pode chamar `POST /meta/publicar`.

### Fluxo do Dashboard

A tela `Dashboard.tsx` exibe o calendário de publicações e listas de postagens. Os dados são obtidos via `GET /agendamentos`, que retorna os agendamentos com data, status e plataforma, permitindo ao frontend renderizar cada item no dia correspondente do calendário. A tela `Results.tsx` consome `GET /resultados/dashboard` para obter os indicadores e `GET /resultados/projetos` para os cards de progresso.

### Formatação das Respostas

Todas as respostas seguem um padrão JSON consistente. Listas retornam arrays de objetos, operações de criação retornam o objeto criado com código HTTP 201, e erros retornam o formato `{"detail": "Mensagem de erro"}` com o código HTTP correspondente. Esse padrão facilita o tratamento de erros no frontend e garante previsibilidade na integração.

---

*Documentação gerada em conformidade com os requisitos acadêmicos do projeto HypeCerto.*
*Backend desenvolvido com FastAPI + SQLAlchemy + Supabase + Meta Graph API.*
