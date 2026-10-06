# FINALIDADE: Feature 05/24 — Pedido de número, validade, CVV ou outros dados de cartão.
# EXECUÇÃO: Recebe o texto na representação esperada pelo extrator e devolve o atributo correspondente. Não decide se o SMS é golpe.
"""Pedido de número, validade, CVV ou outros dados de cartão."""

from extrator_features.apoio_02_regras import contem, solicita, trechos


def classificar(sms: str) -> int:
    for trecho in trechos(sms):
        alvo = r"cvv|cvc|(?:numero|dados|validade) (?:do |de seu |do seu )cartao|nome impresso no cartao"
        if contem(trecho, r"cartao"):
            alvo += r"|validade|codigo de seguranca|nome impresso"
        if solicita(trecho, alvo):
            return 1
    return 0
