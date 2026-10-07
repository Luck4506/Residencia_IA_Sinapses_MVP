# FINALIDADE: 03 — Validar tipo, presença de texto e limite de caracteres, preservando URLs e escrita original.
# EXECUÇÃO: Na entrada de cada mensagem; não remove duplicatas de datasets nem altera rótulos.
"""Validação de uma mensagem; a limpeza de datasets pertence à pesquisa."""


def preparar_mensagem(texto: str) -> str:
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("Envie uma mensagem com texto.")
    if len(texto) > 5000:
        raise ValueError("A mensagem deve ter no máximo 5.000 caracteres.")
    # Preserva URLs, números, pontuação, caixa, acentos e erros de escrita.
    # O extrator existente prepara internamente as versões de que precisa.
    return texto
