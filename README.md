# Lista de Tarefas

API para controle de tarefas, feita com FastAPI na disciplina de extensão em DevOps da PUCPR (2026/2).

Dá para criar, listar, consultar, concluir e apagar tarefas. Os dados ficam salvos em um banco PostgreSQL.

Aplicação no ar: https://tarefas-api-x552.onrender.com

Documentação das rotas: https://tarefas-api-x552.onrender.com/docs

O serviço roda no plano gratuito do Render, então ele hiberna quando fica um tempo sem uso. A primeira requisição depois disso pode demorar uns 50 segundos.

## Tecnologias

- Python 3.14
- FastAPI
- SQLModel
- PostgreSQL
- pytest e pylint
- Docker
- GitHub Actions
- Render

## Rotas

- `GET /` - mensagem de boas-vindas
- `GET /autor` - autor do projeto
- `GET /tarefas` - lista as tarefas
- `POST /tarefas` - cria uma tarefa
- `GET /tarefas/{id}` - mostra uma tarefa
- `PUT /tarefas/{id}` - marca a tarefa como concluída
- `DELETE /tarefas/{id}` - apaga a tarefa

## Rodando na sua máquina

Precisa de Python 3.14 e de um PostgreSQL rodando.

Clone o repositório e crie o ambiente virtual:

```
git clone https://github.com/otavioogo/devops-10-2026.git
cd devops-10-2026
python -m venv .venv
.venv\Scripts\activate
```

Instale as dependências:

```
pip install -r requirements.txt
```

A aplicação lê os dados do banco de quatro variáveis de ambiente. Se faltar alguma, ela não sobe:

```
DATABASE_USERNAME - usuário do banco
DATABASE_PASSWORD - senha
DATABASE_ADDRESS  - endereço e porta, por exemplo localhost:5432
DATABASE          - nome do banco
```

No Windows:

```
$env:DATABASE_USERNAME = "postgres"
$env:DATABASE_PASSWORD = "postgres"
$env:DATABASE_ADDRESS = "localhost:5432"
$env:DATABASE = "tarefas"
```

Depois é só rodar:

```
fastapi dev app/api.py
```

A API sobe em http://localhost:8000 e a documentação fica em http://localhost:8000/docs.

As tabelas são criadas sozinhas quando a aplicação inicia.

## Testes

Os testes usam SQLite, então não precisa do PostgreSQL. Mas as variáveis de ambiente precisam estar definidas (pode usar qualquer valor).

```
pytest
pylint app -d W1203
```

## Docker

```
docker build -t tarefas:2.0 .
docker run -p 8000:8000 -e DATABASE_USERNAME=postgres -e DATABASE_PASSWORD=postgres -e DATABASE_ADDRESS=host.docker.internal:5432 -e DATABASE=tarefas tarefas:2.0
```

A imagem também está publicada no Docker Hub: https://hub.docker.com/r/otavioogo/tarefas

## CI/CD

O workflow fica em `.github/workflows/python-app.yml` e roda a cada push ou pull request na branch main. São três etapas:

1. `build` - roda o pylint e os testes
2. `entrega` - monta a imagem Docker e publica no Docker Hub
3. `deploy` - chama o deploy hook do Render para subir a nova versão

As etapas rodam em sequência. Se os testes falharem, a imagem não é publicada.

Para o pipeline funcionar são necessários a variável `DOCKERHUB_USER` e os segredos `DOCKERHUB_TOKEN` e `RENDER_DEPLOY_HOOK`, cadastrados no próprio repositório.

## Estrutura

```
app/        - código da API (api.py, modelo.py, notificacao.py)
tests/      - testes
Dockerfile  - imagem da aplicação
default.conf - configuração do nginx
```

## Autor

Otavio Ogo
