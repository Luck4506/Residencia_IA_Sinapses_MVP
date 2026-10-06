# FINALIDADE: Feature 09/24 — Pedido de ligação, mesmo quando não informa um número.
# EXECUÇÃO: Recebe o texto na representação esperada pelo extrator e devolve o atributo correspondente. Não decide se o SMS é golpe.
"""Pedido de ligação, mesmo quando não informa um número."""

from extrator_features.apoio_02_regras import acoes, solicita, trechos, contem, afirmacao


def classificar(sms: str) -> int:
    if afirmacao(sms, r"evite(?:\s+\w+){0,5}\s+ligando para"):
        return 1
    for trecho in trechos(sms):
        for acao in acoes(trecho, r"ligue|liga|telefone|ligando"):
            if acao.group() == 'ligando' and not contem(trecho[:acao.start()], r"evite"):
                continue  # 'Estou ligando' relata uma ação, não pede ligação.
            # "Ligue o aparelho" não é uma ligação telefônica.
            resto = trecho[acao.end():].strip()
            if resto.startswith(("o aparelho", "a tv", "o computador", "a luz", "o celular")):
                continue
            if acao.group() == "telefone" and (not resto or resto[0] in ":0123456789(+"):
                continue  # Rótulo "Telefone: (19)..." não é imperativo.
            return 1
    return solicita(sms, r"telefone|ligacao|0800|0300|0303|0900",
                    verbos=r"entre em contato|chame|faca|realize|retorne")
