# IsyShell — Guia Completo

---

## O que é o IsyShell?

O **IsyShell** transforma rotinas de terminal em um microserviço seguro, auditável e containerizado.

A Isy.One gerencia sistemas de ponto de venda para centenas de restaurantes parceiros. Hoje, quando um parceiro precisa executar um diagnóstico no servidor, checar conectividade ou rodar uma manutenção, alguém precisa abrir um terminal e digitar comandos manualmente — sem rastreabilidade, sem controle de acesso, sem registro de quem fez o quê.

O IsyShell resolve isso: qualquer script Bash vira um endpoint REST autenticado, com log completo de cada execução gravado em banco de dados.

---

## O que o sistema faz

| Funcionalidade | Detalhe |
|---|---|
| **Execução de scripts via API** | POST em `/api/v1/scripts/{nome}/execute` roda o script com parâmetros e devolve stdout/stderr |
| **Login para admin e clientes** | Rotas `POST /auth/admin/login` e `POST /auth/login` com usuário e senha — retornam o token de acesso |
| **Autenticação por token** | Após login, o token é enviado no header `X-Isy-Token`. Sem token válido, sem execução |
| **Múltiplos tokens** | Cada restaurante parceiro tem suas credenciais próprias, podendo ser ativado ou desativado individualmente |
| **Auditoria completa** | Toda execução é gravada no PostgreSQL: quem rodou, quando, com quais parâmetros, qual foi o resultado |
| **Painel admin** | Interface web para cadastrar scripts, gerenciar tokens e visualizar logs — sem precisar de curl |
| **Swagger automático** | Documentação interativa da API em `/docs` |
| **Docker Compose** | Um comando sobe tudo: API + banco de dados |

---

## Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e rodando
- `make` disponível no terminal (já vem no macOS/Linux)
- Git (opcional, para clonar o repositório)

---

## Como subir o projeto

### 1. Clone o repositório (ou acesse a pasta do projeto)

```bash
git clone <url-do-repositorio>
cd hackaton
```

### 2. (Opcional) Configure variáveis de ambiente

Copie o `.env.example` e ajuste se necessário:

```bash
cp .env.example .env
```

Por padrão as credenciais são:
- Admin: senha `admin123` (variável `ADMIN_PASSWORD`)
- Admin token interno: `supersecret` (variável `ADMIN_TOKEN`)

Para trocar, edite o `.env`:
```
ADMIN_PASSWORD=minha-senha-segura
ADMIN_TOKEN=meu-token-interno
```

### 3. Suba os containers

```bash
make up
```

Esse comando:
- Builda a imagem Docker da API
- Sobe o container da API na porta `8000`
- Sobe o PostgreSQL na porta `5432`
- Aguarda o banco estar saudável antes de iniciar a API
- Monta a pasta `./scripts/` como volume no container

Aguarde ~15 segundos na primeira execução (download da imagem do PostgreSQL).

### 4. Verifique se está rodando

```bash
curl http://localhost:8000/health
```

Resposta esperada:
```json
{"status": "ok", "service": "isyshell"}
```

### 5. Acesse o painel admin

Abra no navegador: **http://localhost:8000/admin**

- Digite a senha admin no campo superior direito: `admin123`
- Clique em **Conectar**

---

## Comandos disponíveis

```bash
make up        # sobe a API + PostgreSQL (com hot-reload em dev)
make down      # derruba os containers
make logs      # acompanha os logs da API em tempo real
make migrate   # recria as tabelas no banco (se necessário)
make shell     # acessa o bash dentro do container da API
make restart   # make down + make up
make build     # reconstrói a imagem Docker
make test      # roda a suíte de testes (38 testes)
```

> **Atenção:** se o banco já existia de uma versão anterior e você vir erro 500 ao acessar tokens, o schema está desatualizado. Recrie o volume:
> ```bash
> make down && docker volume rm hackaton_postgres_data && make up
> ```

---

## Como usar a API

### Passo 1 — Admin faz login

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/admin/login \
  -H "Content-Type: application/json" \
  -d '{"password": "admin123"}'
```

Resposta:
```json
{"token": "supersecret", "token_type": "bearer"}
```

Use o token retornado no header `X-Isy-Admin-Token` nos próximos passos.

---

### Passo 2 — Criar conta para um cliente

```bash
curl -s -X POST http://localhost:8000/api/v1/admin/tokens \
  -H "Content-Type: application/json" \
  -H "X-Isy-Admin-Token: supersecret" \
  -d '{"name": "Restaurante São Paulo", "username": "rest_sp", "password": "senha123"}'
```

Resposta:
```json
{
  "id": "...",
  "name": "Restaurante São Paulo",
  "username": "rest_sp",
  "token": "a3f8c2d1e4b5...",
  "is_active": true,
  "created_at": "2026-06-02T..."
}
```

---

### Passo 3 — Cliente faz login e obtém seu token

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "rest_sp", "password": "senha123"}'
```

Resposta:
```json
{"token": "a3f8c2d1e4b5...", "token_type": "bearer"}
```

---

### Passo 4 — Admin cadastra um script

```bash
curl -s -X POST http://localhost:8000/api/v1/admin/scripts \
  -H "Content-Type: application/json" \
  -H "X-Isy-Admin-Token: supersecret" \
  -d '{
    "name": "checar-disco",
    "description": "Verifica uso do disco no servidor",
    "content": "#!/bin/bash\ndf -h $1",
    "parameters": ["caminho"],
    "is_active": true
  }'
```

---

### Passo 5 — Cliente executa o script

```bash
curl -s -X POST http://localhost:8000/api/v1/scripts/checar-disco/execute \
  -H "Content-Type: application/json" \
  -H "X-Isy-Token: a3f8c2d1e4b5..." \
  -d '{"parameters": {"caminho": "/"}}'
```

Resposta:
```json
{
  "id": "...",
  "status": "success",
  "exit_code": 0,
  "stdout": "Filesystem      Size  Used Avail Use% Mounted on\n/dev/sda1        50G   12G   38G  24% /\n",
  "stderr": "",
  "executed_at": "2026-06-02T..."
}
```

---

### Passo 6 — Ver os logs de execução

**O cliente vê apenas as próprias execuções:**
```bash
curl http://localhost:8000/api/v1/logs \
  -H "X-Isy-Token: a3f8c2d1e4b5..."
```

**O admin vê tudo:**
```bash
curl http://localhost:8000/api/v1/admin/logs \
  -H "X-Isy-Admin-Token: supersecret"
```

---

## Documentação interativa (Swagger)

Acesse **http://localhost:8000/docs** para explorar e testar todos os endpoints diretamente no navegador.

---

## Estrutura do projeto

```
hackaton/
├── Makefile                      ← comandos do projeto
├── docker-compose.yml            ← definição dos serviços
├── docker-compose.override.yml   ← sobrescritas para desenvolvimento
├── scripts/                      ← scripts Bash (volume mapeado no container)
│   └── exemplo.sh
├── tests/                        ← 38 testes automatizados
└── app/
    ├── Dockerfile                ← imagem python:3.11-slim, usuário não-root
    ├── main.py                   ← FastAPI app
    ├── models.py                 ← Script, Token, Execution (PostgreSQL)
    ├── routers/                  ← endpoints da API
    ├── routers/
    │   ├── auth.py               ← POST /auth/admin/login e /auth/login
    │   └── ...
    ├── services/
    │   ├── auth.py               ← validação de tokens nos headers
    │   └── executor.py           ← subprocess + timeout
    └── static/                   ← UI admin (Bootstrap 5)
```



