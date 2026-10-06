# FINALIDADE: Feature 03/24 — Solicitação de agência, banco e dados da conta bancária.
# EXECUÇÃO: Recebe o texto na representação esperada pelo extrator e devolve o atributo correspondente. Não decide se o SMS é golpe.
"""Solicitação de agência, banco e dados da conta bancária."""

from extrator_features.apoio_02_regras import solicita, afirmacao


def classificar(sms: str) -> int:
    # "Conta" sem qualificação também pode ser de e-mail; não é suficiente.
    return afirmacao(sms, r"qual (?:e )?(?:o )?seu banco|qual (?:e )?(?:a )?sua agencia") or solicita(sms, r"(?:numero (?:do |da ))?(?:banco|agencia)|"
                    r"numero (?:da |de )conta|conta bancaria|dados bancarios|"
                    r"dados (?:da |de sua |da sua )conta(?: bancaria)?")
