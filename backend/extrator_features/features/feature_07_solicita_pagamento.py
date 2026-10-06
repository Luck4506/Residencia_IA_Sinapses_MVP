# FINALIDADE: Feature 07/24 — Pedido de pagamento ou movimentação de dinheiro.
# EXECUÇÃO: Recebe o texto na representação esperada pelo extrator e devolve o atributo correspondente. Não decide se o SMS é golpe.
"""Pedido de pagamento ou movimentação de dinheiro."""

from extrator_features.apoio_02_regras import acoes, solicita, trechos


def classificar(sms: str) -> int:
    # Verbos inequivocamente financeiros podem aparecer sem valor expresso.
    if any(list(acoes(t, r"pague|quite|deposite")) for t in trechos(sms)):
        return 1
    return solicita(sms, r"pagamento|pix|deposito|transferencia|dinheiro|valor|"
                    r"quantia|r\$\s*\d+(?:[.,]\d+)*|reais|taxa|boleto|divida|cobranca|fatura", verbos=
                    r"faca|faz|realize|efetue|transfira|envie|mande|pague|quite|deposite")
