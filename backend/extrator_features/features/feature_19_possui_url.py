# FINALIDADE: Feature 19/24 — Presença estrutural de URL; não avalia se o endereço é malicioso.
# EXECUÇÃO: Recebe o texto na representação esperada pelo extrator e devolve o atributo correspondente. Não decide se o SMS é golpe.
"""Presença estrutural de URL; não avalia se o endereço é malicioso."""

from extrator_features.bibliotecas.apoio_02_urls import extrair_urls


def classificar(sms: str) -> int:
    # A extração e a validação do domínio são explicadas no arquivo urls.py.
    return int(bool(extrair_urls(sms)))
