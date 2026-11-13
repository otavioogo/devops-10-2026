"""Aplicação para o módulo de extensão DevOps"""

from datetime import datetime, timezone
from typing import Annotated, List
import os
import sys
import logging

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel, Session, create_engine, select

from .modelo import Tarefa

LOGGER = logging.getLogger("aplicacao")
LOGGER.setLevel(logging.INFO)

arquivo = logging.FileHandler("aplicacao.log", encoding='utf-8')
saida_padrao = logging.StreamHandler()

formatador = logging.Formatter(
    "%(name)s | %(levelname)s | %(asctime)s | %(filename)s:%(lineno)s | %(message)s"
)

arquivo.setFormatter(formatador)
saida_padrao.setFormatter(formatador)

LOGGER.addHandler(arquivo)
LOGGER.addHandler(saida_padrao)

DATABASE_USERNAME = os.environ.get("DATABASE_USERNAME")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
DATABASE_ADDRESS = os.environ.get("DATABASE_ADDRESS")
DATABASE = os.environ.get("DATABASE")

if DATABASE_USERNAME is None:
    LOGGER.critical("DATABASE_USERNAME está faltando")
    sys.exit(1)

if DATABASE_PASSWORD is None:
    LOGGER.critical("DATABASE_PASSWORD está faltando")
    sys.exit(1)

if DATABASE_ADDRESS is None:
    LOGGER.critical("DATABASE_ADDRESS está faltando")
    sys.exit(1)

if DATABASE is None:
    LOGGER.critical("DATABASE está faltando")
    sys.exit(1)

ENGINE = create_engine(
    f"postgresql+psycopg://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_ADDRESS}/{DATABASE}"
)


def criar_sessao():
    """Função utilitária para criar sessão no banco de dados"""
    with Session(ENGINE) as s:
        yield s


SESSAO = Annotated[Session, Depends(criar_sessao)]


async def inicializacao(_: FastAPI):
    """Função para incialização da API e do banco de dados"""
    SQLModel.metadata.create_all(ENGINE)
    yield


APP = FastAPI(lifespan=inicializacao)
TAREFAS = []

@APP.exception_handler(404)
async def trata_404(_, __):
    """ Rota para erros. """
    LOGGER.error("Página inexistente")
    return JSONResponse({"mensagem": "Página inexistente"})

# GET /tarefas: Lista todas as tarefas (somente id e titulo)
@APP.get("/tarefas")
async def tarefas(sessao: SESSAO) -> List[Tarefa]:
    """Rota para listar as tarefas."""

    LOGGER.info("Usuário listou as tarefas")

    lista_tarefas = sessao.exec(select(Tarefa).offset(0)).all()

    return lista_tarefas


# POST /tarefas: Cria tarefa
@APP.post("/tarefas", status_code=201)
async def post_tarefa(sessao: SESSAO, titulo: str, descricao: str = None):
    """Rota para criar uma tarefa."""
    data = datetime.now().astimezone(timezone.utc).replace(microsecond=0)
    tarefa_nova = Tarefa(
        titulo=titulo,
        descricao=descricao,
        data_criacao=data,
    )

    LOGGER.info("Usuário criou uma tarefa")
    LOGGER.debug(f"Tarefa criada: {tarefa_nova}")

    sessao.add(tarefa_nova)
    sessao.commit()
    sessao.refresh(tarefa_nova)

    return {"mensagem": "OK"}


# GET /tarefas/{id_tarefa}: Visualizar tarefa específica
@APP.get("/tarefas/{id_tarefa}")
async def tarefa_especifica(sessao: SESSAO, id_tarefa: int) -> Tarefa:
    """Rota para visualizar uma tarefa específica"""
    # select * from tarefas where id == id_tarefa
    regra = select(Tarefa).where(Tarefa.id == id_tarefa)
    resultado = sessao.exec(regra).all()

    if resultado:
        LOGGER.info(f"Usuário listou a tafefa {resultado[0].get_id()}")
        return resultado[0]

    LOGGER.info("Usuário tentou acessar uma tarefa inexistente")
    return {"mensagem": "Tarefa não existe"}


# PUT /tarefas/{id}: Atualiza tarefa específica
@APP.put("/tarefas/{id_tarefa}")
async def concluir_tarefa(sessao: SESSAO, id_tarefa: int):
    """Rota para concluir uma tarefa."""

    # Atualizar a rota para suportar o SQLModel/Conexão com BD
    # Usar select para filtrar as tarefas com base no ID e se estiver concluída
    # Atualizar usando sessao.add, sessao.commit, sessao.refresh

    regra = select(Tarefa).where(Tarefa.id == id_tarefa)
    resultado = sessao.exec(regra).all()

    if not resultado:
        LOGGER.info("Usuário tentou finalizar uma tarefa inexistente")
        return {"mensagem": "Tarefa não existe"}

    if resultado[0].concluida is True:
        LOGGER.info(
            "Usuário tentou finalizar a tarefa " 
            f"{resultado[0].get_id()} que já está finalizada"
        )
        return {"mensagem": "Tarefa já finalizada"}

    resultado[0].finalizar()

    sessao.add(resultado[0])
    sessao.commit()
    sessao.refresh(resultado[0])

    LOGGER.info(f"Usuário finalizou a tafefa {resultado[0].get_id()}")
    return {"mensagem": "Tarefa atualizada"}


# DELETE /tarefas/{id_tarefa}: Exclui tarefa
@APP.delete("/tarefas/{id_tarefa}")
async def apagar_tarefa(sessao: SESSAO, id_tarefa: int):
    """Rota para apagar tarefa."""

    regra = select(Tarefa).where(Tarefa.id == id_tarefa)
    resultado = sessao.exec(regra).all()

    if not resultado:
        LOGGER.info("Usuário tentou apagar uma tarefa inexistente")
        return {"mensagem": "Tarefa não existe"}

    tarefa = resultado[0]

    sessao.delete(tarefa)
    sessao.commit()

    LOGGER.info(f"Usuário removeu a tarefa {tarefa.get_id()}")
    return {"mensagem": "Tarefa removida"}


@APP.get("/")
async def index():
    """Rota raíz."""

    LOGGER.info("Usuário acessou a raíz")
    return {"mensagem": "Olá, mundo!"}


# 1. Implementar uma rota chamada "/autor" que retorna
# um dicionário no formato {"mensagem": SEU NOME COMPLETO}
@APP.get("/autor")
async def autor():
    """Rota para retornar o autor da aplicação"""
    LOGGER.info("Usuário consultou o autor")
    return {"mensagem": "Otavio Ogo"}


# 2. Criar um teste unitário para verificar se a rota
# está produzindo o resultado esperado

# 3. Verificar se o código está no padrão do PyLint

# 4. Enviar o código para o repositório (git push)
