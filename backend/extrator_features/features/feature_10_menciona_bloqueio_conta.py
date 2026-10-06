# FINALIDADE: Feature 10/24 — Estado ou ameaça de bloqueio, suspensão ou cancelamento de conta/serviço.
# EXECUÇÃO: Recebe o texto na representação esperada pelo extrator e devolve o atributo correspondente. Não decide se o SMS é golpe.
"""Estado ou ameaça de bloqueio, suspensão ou cancelamento de conta/serviço."""

from extrator_features.apoio_02_regras import afirmacao

OBJETO = r"conta|cartao|cadastro|servico|acesso"
ESTADO = r"bloquead[oa]s?|bloqueio|suspens[oa]s?|suspensao|cancelad[oa]s?|cancelamento|desativad[oa]s?|desativacao"


def classificar(sms: str) -> int:
    # A proximidade associa a consequência ao objeto, nas duas ordens comuns.
    return afirmacao(sms, rf"(?:{OBJETO})(?:\s+\w+){{0,5}}\s+(?:{ESTADO})|"
                     rf"(?:{ESTADO})(?:\s+\w+){{0,5}}\s+(?:{OBJETO})")
