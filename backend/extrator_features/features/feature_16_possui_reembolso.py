# FINALIDADE: Feature 16/24 — Afirmação de devolução ou valor disponível para recebimento.
# EXECUÇÃO: Recebe o texto na representação esperada pelo extrator e devolve o atributo correspondente. Não decide se o SMS é golpe.
"""Afirmação de devolução ou valor disponível para recebimento."""

from extrator_features.apoio_02_regras import afirmacao


def classificar(sms: str) -> int:
    # Crédito sem contexto de devolução pode ser empréstimo; não basta.
    beneficio = r"reembolso|restituicao|devolucao de dinheiro|estorno|ressarcimento"
    return afirmacao(sms, rf"(?:{beneficio})(?:\s+[\w$.,]+){{0,12}}\s+(?:disponivel|liberado|aprovado)|"
                     rf"(?:voce tem direito a[o]?|receba|recebera|receber|liberamos|solicite|solicitar)(?:\s+\w+){{0,4}}\s+(?:{beneficio})|"
                     r"(?:o valor|sua compra)(?:\s+\w+){0,4}\s+sera estornad[oa]|"
                     r"(?:voce tem|identificamos|consta)(?:\s+\w+){0,4}\s+valor(?:es)? a receber")
