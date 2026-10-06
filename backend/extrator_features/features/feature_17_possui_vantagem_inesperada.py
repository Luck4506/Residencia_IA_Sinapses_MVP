# FINALIDADE: Feature 17/24 — Indícios explícitos de benefício extraordinário ou seleção inesperada.
# EXECUÇÃO: Recebe o texto na representação esperada pelo extrator e devolve o atributo correspondente. Não decide se o SMS é golpe.
"""Indícios explícitos de benefício extraordinário ou seleção inesperada."""

from extrator_features.apoio_02_regras import afirmacao
from extrator_features.features.feature_15_possui_recompensa import classificar as tem_recompensa


def classificar(sms: str) -> int:
    # O SMS não permite saber a expectativa real da pessoa; esta é uma aproximação.
    return tem_recompensa(sms) or afirmacao(sms,
        r"(?:dinheiro|beneficio)(?:\s+[\w$.,]+){0,7}\s+(?:liberado|disponivel)|"
        r"credito inesperado|desconto extraordinario|oportunidade exclusiva|"
        r"(?:valor|reembolso|credito) surpresa|sem (?:voce )?ter solicitado"
    )
