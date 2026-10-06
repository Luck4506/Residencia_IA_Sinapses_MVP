# FINALIDADE: 01 — Receber requisições HTTP, validar o corpo e devolver JSON ao cliente.
# EXECUÇÃO: Ao iniciar o FastAPI, cria o serviço e carrega os modelos; nas requisições chama as etapas seguintes.
"""Executar dentro de backend: python -m uvicorn api.etapa_01_main:app --reload."""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator






app = criar_app()
