# FINALIDADE: 01 — Receber requisições HTTP, validar o corpo e devolver JSON ao cliente.
# EXECUÇÃO: Ao iniciar o FastAPI, cria o serviço e carrega os modelos; nas requisições chama as etapas seguintes.
"""Executar dentro de backend: python -m uvicorn api.main:app --reload."""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from api.preparacao import preparar_mensagem
from api.erros import Indisponivel
from api.servico import ServicoSMS


class PedidoAnalise(BaseModel):
    mensagem: str = Field(min_length=1, max_length=5000)

    @field_validator("mensagem")
    @classmethod
    def validar(cls, mensagem):
        return preparar_mensagem(mensagem)


def criar_app(fabrica_servico=ServicoSMS):
    @asynccontextmanager
    async def lifespan(app):
        servico = fabrica_servico()
        servico.carregar()
        app.state.servico = servico
        try:
            yield
        finally:
            servico.fechar()

    app = FastAPI(title="Protótipo de avaliação de SMS", version="0.1.0", lifespan=lifespan)
    origens = [x.strip() for x in os.getenv("CORS_ORIGINS", "").split(",") if x.strip()]
    app.add_middleware(
        CORSMiddleware, allow_origins=origens,
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_methods=["GET", "POST"], allow_headers=["Content-Type"],
    )

    @app.get("/saude")
    def saude(request: Request):
        return request.app.state.servico.status()

    def executar(acao, mensagem):
        try:
            return acao(mensagem)
        except Indisponivel as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from None
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from None

    @app.post("/extrair")
    def extrair(pedido: PedidoAnalise, request: Request):
        return executar(request.app.state.servico.extrair, pedido.mensagem)

    @app.post("/analisar")
    def analisar(pedido: PedidoAnalise, request: Request):
        return executar(request.app.state.servico.classificar, pedido.mensagem)

    return app


app = criar_app()
