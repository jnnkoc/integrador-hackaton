# IsyShell — Design Spec
**Data:** 2026-06-02  
**Hackathon:** FMU Tech Hackathon 2026 — IsyShell Challenge

---

## Visão Geral

Sistema que transforma rotinas de terminal em um microserviço seguro, auditável e containerizado para a Isy.One. Expõe scripts Bash via API REST autenticada, com interface web de administração e persistência de auditoria em PostgreSQL.

---

## Arquitetura

Um único container FastAPI expõe a API REST e os arquivos estáticos da UI admin. O PostgreSQL roda em container separado. Um volume Docker mapeia `./scripts/` do host para dentro do container, permitindo adicionar/editar scripts sem rebuild de imagem.

```
Docker Compose
├── isyshell-api  (FastAPI :8000)
│   ├── /api/v1/*        REST endpoints
│   ├── /admin           UI admin (HTML estático)
│   └── /docs            Swagger automático
├── postgres      (:5432)
└── volume: ./scripts/ → /scripts/ no container
```

**Stack:**
- Python 3.11 + FastAPI + SQLAlchemy + Alembic
- PostgreSQL 15
- Bootstrap 5 via CDN (UI admin)
- Docker + Docker Compose + Makefile

---

## Modelo de Dados

### Tabela `scripts`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID PK | |
| name | VARCHAR UNIQUE | identificador do script |
| description | TEXT | descrição legível |
| content | TEXT | código Bash inline |
| parameters | JSONB | lista de params esperados (nomes) |
| is_active | BOOLEAN | habilita/desabilita execução |
| created_at | TIMESTAMP | |

### Tabela `tokens`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID PK | |
| name | VARCHAR | nome do cliente/parceiro |
| token | VARCHAR UNIQUE | gerado com `secrets.token_hex(32)` |
| is_active | BOOLEAN | |
| created_at | TIMESTAMP | |

### Tabela `executions`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID PK | |
| script_id | UUID FK → scripts | |
| token_id | UUID FK → tokens | token usado na chamada |
| parameters | JSONB | valores passados na execução |
| stdout | TEXT | saída capturada |
| stderr | TEXT | erros capturados |
| exit_code | INTEGER | código de retorno do processo |
| status | VARCHAR | `success` \| `error` \| `timeout` |
| executed_at | TIMESTAMP | |

---

## Endpoints da API

### Execução (requer `X-Isy-Token` válido)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/scripts` | Lista scripts ativos |
| POST | `/api/v1/scripts/{name}/execute` | Executa script com parâmetros |
| GET | `/api/v1/logs` | Lista execuções do token autenticado (paginado) |
| GET | `/api/v1/logs/{id}` | Detalhe de uma execução (somente do token autenticado) |

**Body de execução:**
```json
{ "parameters": { "param1": "valor1", "param2": "valor2" } }
```

### Administração (requer `X-Isy-Admin-Token` via env var)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/admin/scripts` | Lista todos os scripts |
| POST | `/api/v1/admin/scripts` | Cadastra novo script |
| PUT | `/api/v1/admin/scripts/{id}` | Edita script |
| DELETE | `/api/v1/admin/scripts/{id}` | Remove script |
| GET | `/api/v1/admin/tokens` | Lista tokens de clientes |
| POST | `/api/v1/admin/tokens` | Cria novo token (gerado automaticamente) |
| PATCH | `/api/v1/admin/tokens/{id}` | Ativa/desativa token |
| DELETE | `/api/v1/admin/tokens/{id}` | Remove token |
| GET | `/api/v1/admin/logs` | Lista todas as execuções (paginado) |

---

## Segurança

**Duas camadas de autenticação:**

1. **Clientes** — header `X-Isy-Token`: validado contra tabela `tokens` (`is_active=true`). Token registrado na execução para auditoria.
2. **Admin** — header `X-Isy-Admin-Token`: valor fixo em variável de ambiente `ADMIN_TOKEN`, nunca armazenado no banco.

**Proteções na execução:**
- `subprocess.run(["bash", "/scripts/{name}.sh", param1, param2], capture_output=True, timeout=30)` — parâmetros como argumentos posicionais, nunca interpolados no shell (previne injeção)
- Timeout de 30s para evitar scripts travados
- Container roda com usuário não-root (`appuser`)
- API não exposta publicamente sem token

---

## Fluxo de Execução

```
POST /api/v1/scripts/{name}/execute
  │
  ├── 1. Valida X-Isy-Token → 401 se ausente/inválido/inativo
  ├── 2. Busca script por name → 404 se não encontrado
  ├── 3. Verifica is_active=true → 403 se inativo
  ├── 4. Escreve content em /scripts/{name}.sh (do volume)
  ├── 5. subprocess.run(timeout=30s, capture_output=True)
  ├── 6. Persiste execution no banco (stdout, stderr, exit_code, status)
  └── 7. Retorna JSON com resultado completo
```

---

## Estrutura do Projeto

```
hackaton/
├── Makefile
├── docker-compose.yml
├── docker-compose.override.yml      # hot-reload para dev
├── scripts/                         # volume mapeado no container
│   └── exemplo.sh
├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                      # FastAPI app + routers + static
│   ├── config.py                    # settings via pydantic-settings
│   ├── database.py                  # SQLAlchemy engine + session
│   ├── models.py                    # ORM models
│   ├── schemas.py                   # Pydantic schemas (request/response)
│   ├── routers/
│   │   ├── scripts.py               # GET /scripts, POST /scripts/{name}/execute
│   │   ├── tokens.py                # admin tokens CRUD
│   │   ├── admin_scripts.py         # admin scripts CRUD
│   │   └── logs.py                  # GET /logs
│   ├── services/
│   │   ├── executor.py              # subprocess + persistência de execução
│   │   └── auth.py                  # validação de token cliente e admin
│   └── static/
│       ├── index.html               # UI admin (Bootstrap 5)
│       ├── app.js                   # fetch calls para a API
│       └── style.css
└── docs/
    └── superpowers/specs/
        └── 2026-06-02-isyshell-design.md
```

---

## Docker & Makefile

**`docker-compose.yml`** — serviços `api` e `postgres` com volume `./scripts:/scripts`.

**`docker-compose.override.yml`** — adiciona hot-reload (`--reload`) e monta código fonte para desenvolvimento.

**Makefile targets:**
```makefile
make up        # sobe api + postgres (detached)
make down      # derruba todos os containers
make logs      # tail dos logs da api
make migrate   # roda alembic upgrade head dentro do container
make shell     # bash interativo dentro do container api
make restart   # down + up
make build     # reconstrói imagens
```

---

## Critérios do Hackathon → Cobertura

| Critério | Peso | Como atendido |
|----------|------|---------------|
| Arquitetura & API | 25% | FastAPI, routers organizados, Swagger em `/docs` |
| Segurança (Token) | 25% | Múltiplos tokens, duas camadas (cliente + admin), container não-root |
| Log Persistence | 20% | Tabela `executions` no PostgreSQL com stdout/stderr/status/timestamp |
| Docker Deploy | 20% | Docker Compose, Makefile, imagem slim, volume para scripts |
| Pitch & Inovação | 10% | UI admin visual, Swagger, arquitetura clara para apresentação |
