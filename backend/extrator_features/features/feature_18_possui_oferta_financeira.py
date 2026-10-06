# FINALIDADE: Feature 18/24 — Oferta de crédito, empréstimo, investimento ou ganho financeiro.
# EXECUÇÃO: Recebe o texto na representação esperada pelo extrator e devolve o atributo correspondente. Não decide se o SMS é golpe.
"""Oferta de crédito, empréstimo, investimento ou ganho financeiro."""

from extrator_features.apoio_02_regras import afirmacao


def classificar(sms: str) -> int:
    produto = r"credito|emprestimo|financiamento|investimento"
    return afirmacao(sms, rf"(?:{produto})(?:\s+[\w$.,-]+){{0,9}}\s+pre[ -]?aprovad[oa]|"
                     rf"(?:seu |sua |temos |oferecemos )(?:{produto})(?:\s+[\w$.,-]+){{0,9}}\s+(?:pre-aprovado|aprovado|liberado|disponivel)|"
                     rf"(?:contrate|solicite|oferecemos|oferta de)(?:\s+\w+){{0,4}}\s+(?:{produto})|"
                     r"invista(?:\s+[\w$.,]+){0,8}\s+(?:ganhe|retorno|rendimento|lucro)|"
                     r"ganhe (?:r\$\s*)?\d+(?:[.,]\d+)? (?:reais |por dia|por mes)")
