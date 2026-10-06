# FINALIDADE: Feature 04/24 — Pedido de identificadores ou dados cadastrais do destinatário.
# EXECUÇÃO: Recebe o texto na representação esperada pelo extrator e devolve o atributo correspondente. Não decide se o SMS é golpe.
"""Pedido de identificadores ou dados cadastrais do destinatário."""

from extrator_features.apoio_02_regras import solicita


def classificar(sms: str) -> int:
    # Lista editável; confirmações e atualizações explícitas também são pedidos.
    return solicita(sms, r"seu cpf|cpf|rg|seu rg|nome completo|data de nascimento|endereco|"
                    r"telefone|celular|e-?mail|dados pessoais|dados cadastrais|seu cadastro")
