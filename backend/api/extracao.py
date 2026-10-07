# FINALIDADE: 05 — Acionar o LanguageTool local e as regras das 22 features estruturadas.
# EXECUÇÃO: Reutiliza o corretor por processo; retorna atributos ao serviço, sem decidir fraude.
"""Adaptador do extrator existente e do corretor gramatical local."""
import logging
import threading

from extrator_features.etapa_01_classificador import analisar_sms
from extrator_features.bibliotecas.apoio_03_gramatica import Corretor
from extrator_features.apoio_01_gramatica import filtrar_erros
from api.erros import Indisponivel

LOGGER = logging.getLogger(__name__)


class ExtratorSMS:
    def __init__(self):
        self.corretor = Corretor("6.8")
        self.gramatica_verificada = False
        self.lock = threading.Lock()

    def extrair(self, mensagem):
        # Reutiliza Java por processo e não grava mensagens no cache do notebook.
        with self.lock:
            try:
                gramatica = filtrar_erros(self.corretor.detectar_erros(mensagem))
                self.gramatica_verificada = True
            except Exception:
                self.gramatica_verificada = False
                LOGGER.exception("LanguageTool local indisponível.")
                raise Indisponivel("LanguageTool indisponível. Configure Java 17+ e o LanguageTool 6.8 local.") from None
            return analisar_sms(mensagem, gramatica=gramatica)["features"]

    def fechar(self):
        with self.lock:
            self.corretor.close()
