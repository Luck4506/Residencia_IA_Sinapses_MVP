# FINALIDADE: Feature 15/24 — Alegação de prêmio, seleção ou benefício concedido ao destinatário.
# EXECUÇÃO: Recebe o texto na representação esperada pelo extrator e devolve o atributo correspondente. Não decide se o SMS é golpe.
"""Alegação de prêmio, seleção ou benefício concedido ao destinatário."""

from extrator_features.apoio_02_regras import afirmacao


def classificar(sms: str) -> int:
    return afirmacao(sms, r"(?:voce|vc) (?:ganhou|acaba de ganhar|foi (?:selecionad[oa]|sortead[oa]|premiad[oa]))|"
                     r"(?:voce|vc) recebeu (?:um |uma )?(?:premio|recompensa|brinde|bonus|presente)|"
                     r"(?:tem|ha) (?:um |uma )?(?:premio|recompensa|brinde|bonus|presente) esperando por (?:voce|vc)|"
                     r"seu numero foi sorteado|"
                     r"(?:seu|sua) (?:premio|recompensa|brinde|bonus|presente)(?:\s+\w+){0,4}\s+(?:disponivel|liberad[oa])|"
                     r"(?:ganhou|recebera|ganhe|resgate)(?:\s+\w+){0,4}\s+(?:premio|recompensa|brinde|bonus|presente)")
