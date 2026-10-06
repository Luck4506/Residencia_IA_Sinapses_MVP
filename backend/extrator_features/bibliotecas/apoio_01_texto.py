# FINALIDADE: Validação compartilhada sem carregar bibliotecas ou modelos pesados.
# EXECUÇÃO: É importado e chamado pelo fluxo da API; não precisa ser iniciado manualmente.
"""Validação compartilhada sem carregar bibliotecas ou modelos pesados."""


def validar(sms: str) -> str:
    if not isinstance(sms, str):
        raise TypeError("O SMS deve ser uma string.")
    return sms
