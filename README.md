# Lista de Tarefas — API REST com pipeline de CI/CD

Aplicação desenvolvida para o módulo de extensão **DevOps** da PUCPR (2026/2).

Trata-se de uma API REST para gerenciamento de uma lista de tarefas, construída com
FastAPI e persistência em PostgreSQL, integrada a um pipeline completo de integração
contínua (CI) e entrega contínua (CD) via GitHub Actions, com publicação de imagem no
Docker Hub e implantação automatizada no Render.

## Descrição da aplicação

A API permite criar, listar, consultar, concluir e remover tarefas. Cada tarefa possui
título, descrição opcional, situação de conclusão e as datas de criação e de conclusão.

Além das rotas de negócio, a aplicação registra em log todas as operações realizadas
(em arquivo e na saída padrão) e trata requisições a rotas inexistentes.

### Rotas disponíveis

| Método | Rota              | Descrição                                    |
|--------|-------------------|----------------------------------------------|
| GET    | `/`               | Mensagem de boas-vindas                      |
| GET    | `/autor`          | Autor da aplicação                           |
| GET    | `/tarefas`        | Lista todas as tarefas                       |
| POST   | `/tarefas`        | Cria uma tarefa (`titulo`, `descricao`)      |
| GET    | `/tarefas/{id}`   | Consulta uma tarefa específica               |
| PUT    | `/tarefas/{id}`   | Marca a tarefa como concluída                |
| DELETE | `/tarefas/{id}`   | Remove a tarefa                              |

A documentação interativa gerada automaticamente pelo FastAPI fica disponível em
`/docs` (Swagger UI) e `/redoc`.

## Tecnologias utilizadas

| Categoria          | Tecnologia                              |
|--------------------|-----------------------------------------|
| Linguagem          | Python 3.14                             |
| Framework web      | FastAPI + Uvicorn                       |
| ORM / modelagem    | SQLModel + SQLAlchemy                   |
| Banco de dados     | PostgreSQL (driver `psycopg`)           |
| Testes             | pytest + pytest-cov + SQLite            |
| Qualidade de código| pylint + ruff + bandit                  |
| Proxy reverso      | nginx (`default.conf`)                  |
| Conteinerização    | Docker                                  |
| CI/CD              | GitHub Actions                          |
| Registro de imagem | Docker Hub                              |
| Implantação        | Render                                  |

## Execução local

### Pré-requisitos

- Python 3.14
- PostgreSQL em execução (local ou remoto)

### 1. Clonar o repositório

```bash
git clone https://github.com/otavioogo/devops-10-2026.git
cd devops-10-2026
```

### 2. Criar e ativar o ambiente virtual

```bash
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar as variáveis de ambiente

A aplicação exige as quatro variáveis abaixo. Se qualquer uma estiver ausente, a
inicialização é interrompida com uma mensagem de log de nível `CRITICAL`.

| Variável            | Descrição                          | Exemplo        |
|---------------------|------------------------------------|----------------|
| `DATABASE_USERNAME` | Usuário do banco                   | `postgres`     |
| `DATABASE_PASSWORD` | Senha do banco                     | `postgres`     |
| `DATABASE_ADDRESS`  | Endereço e porta do banco          | `localhost:5432` |
| `DATABASE`          | Nome da base de dados              | `tarefas`      |

```bash
# Windows (PowerShell)
$env:DATABASE_USERNAME = "postgres"
$env:DATABASE_PASSWORD = "postgres"
$env:DATABASE_ADDRESS  = "localhost:5432"
$env:DATABASE          = "tarefas"

# Linux / macOS
export DATABASE_USERNAME=postgres
export DATABASE_PASSWORD=postgres
export DATABASE_ADDRESS=localhost:5432
export DATABASE=tarefas
```

### 5. Executar a aplicação

```bash
fastapi dev app/api.py
```

A API responde em `http://localhost:8000` e a documentação fica em
`http://localhost:8000/docs`.

Para executar também o serviço de notificações, em outro terminal:

```bash
fastapi dev app/notificacao.py --port 8002
```

## Testes e qualidade de código

Os testes utilizam SQLite, portanto não exigem um PostgreSQL ativo, mas as variáveis
de ambiente precisam estar definidas (podem receber valores fictícios).

```bash
# Testes unitarios
pytest

# Cobertura de testes
pytest --cov=app

# Analise estatica
pylint app -d W1203
ruff check app

# Analise de seguranca
bandit -r app
```

## Execução com Docker

```bash
# Construir a imagem
docker build -t tarefas:2.0 .

# Executar o contêiner
docker run -p 8000:8000 \
  -e DATABASE_USERNAME=postgres \
  -e DATABASE_PASSWORD=postgres \
  -e DATABASE_ADDRESS=host.docker.internal:5432 \
  -e DATABASE=tarefas \
  tarefas:2.0
```

## Pipeline de CI/CD

O workflow [`.github/workflows/python-app.yml`](.github/workflows/python-app.yml) é
disparado automaticamente a cada `push` ou `pull request` na branch `main`, e também
pode ser acionado manualmente (`workflow_dispatch`). Ele é composto por três estágios
executados em sequência:

### 1. `build` — Integração Contínua

- Instala o Python 3.14 e as dependências do projeto
- Executa a análise estática com `pylint`
- Executa a suíte de testes com `pytest`

### 2. `entrega` — Entrega Contínua

- Autentica no Docker Hub
- Constrói a imagem a partir do `Dockerfile`
- Publica a imagem no Docker Hub com a tag `tarefas:2.0`

### 3. `deploy` — Implantação

- Aciona o *deploy hook* do Render, que publica a nova versão da imagem

### Configuração necessária no repositório

Para que os estágios de entrega e implantação funcionem, é preciso cadastrar no
GitHub, em *Settings → Secrets and variables → Actions*:

| Tipo     | Nome                 | Conteúdo                              |
|----------|----------------------|---------------------------------------|
| Variable | `DOCKERHUB_USER`     | Usuário do Docker Hub                 |
| Secret   | `DOCKERHUB_TOKEN`    | Token de acesso do Docker Hub         |
| Secret   | `RENDER_DEPLOY_HOOK` | URL do *deploy hook* do serviço       |

## Estrutura do projeto

```
.
├── .github/workflows/
│   └── python-app.yml      # Pipeline de CI/CD
├── app/
│   ├── __init__.py
│   ├── api.py              # Rotas da API e configuracao do banco
│   ├── modelo.py           # Modelo Tarefa (SQLModel)
│   └── notificacao.py      # Servico de notificacoes
├── tests/
│   ├── __init__.py
│   ├── test_app.py         # Testes das rotas
│   └── test_modelo.py      # Testes do modelo
├── Dockerfile
├── default.conf            # Configuracao do proxy reverso nginx
├── requirements.txt
└── README.md
```

## Autor

Otavio Ogo
