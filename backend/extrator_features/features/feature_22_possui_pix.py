# FINALIDADE: Feature 22/24 — Referência explícita ao PIX, independentemente de haver pedido de pagamento.
# EXECUÇÃO: Recebe o texto na representação esperada pelo extrator e devolve o atributo correspondente. Não decide se o SMS é golpe.
"""Referência explícita ao PIX, independentemente de haver pedido de pagamento."""

from extrator_features.bibliotecas.apoio_05_pix import classificar as detectar_pix


def classificar(sms: str) -> int:
    # Limites de palavra evitam marcar "pixel" ou "pixar".
    return detectar_pix(sms)
