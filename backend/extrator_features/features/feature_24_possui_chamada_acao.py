# FINALIDADE: Feature 24/24 — Comando afirmativo dirigido ao destinatário, qualquer que seja a ação.
# EXECUÇÃO: Recebe o texto na representação esperada pelo extrator e devolve o atributo correspondente. Não decide se o SMS é golpe.
"""Comando afirmativo dirigido ao destinatário, qualquer que seja a ação."""

from extrator_features.apoio_02_regras import acoes, trechos


def classificar(sms: str) -> int:
    # Infinitivos soltos e relatos no passado não são considerados comandos.
    return int(any(list(acoes(trecho)) for trecho in trechos(sms)))
