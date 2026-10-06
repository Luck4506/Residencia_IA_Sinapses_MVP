# FINALIDADE: Feature 01/24 — Pedido explícito de senha, incluindo confirmação e atualização.
# EXECUÇÃO: Recebe o texto na representação esperada pelo extrator e devolve o atributo correspondente. Não decide se o SMS é golpe.
"""Pedido explícito de senha, incluindo confirmação e atualização."""

from extrator_features.apoio_02_regras import solicita, ACOES_DADOS, PEDIDO_INDIRETO

# PDF p. 2: inclui atualizar a senha, não apenas revelá-la a alguém.
# Vocabulário local para não mudar o significado das outras features.
ACOES_SENHA = (
    ACOES_DADOS + r"|altere|troque|redefina|recadastre|"
    + PEDIDO_INDIRETO + r"(?:alterar|trocar|redefinir|recadastrar)|"
    r"(?:voce )?(?:poderia|pode|deveria)\s+(?:alterar|trocar|redefinir|recadastrar)"
)


def classificar(sms: str) -> int:
    # A palavra sozinha não basta: exige verbo de pedido e ignora negações locais.
    # Aviso de troca, cancelamento de acesso ou credenciais genéricas não basta.
    # Sem inferir o conteúdo da página de destino ou resolver elipses entre frases.
    return solicita(sms, r"senhas?(?: de acesso)?", verbos=ACOES_SENHA)
