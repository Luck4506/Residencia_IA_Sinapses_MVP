# FINALIDADE: Feature 06/24 — Pedido explícito de atualização, confirmação ou regularização cadastral.
# EXECUÇÃO: Recebe o texto na representação esperada pelo extrator e devolve o atributo correspondente. Não decide se o SMS é golpe.
"""Pedido explícito de atualização, confirmação ou regularização cadastral."""

from extrator_features.apoio_02_regras import solicita


def classificar(sms: str) -> int:
    return solicita(sms, r"cadastro|dados(?: cadastrais)?", verbos=
                    r"atualize|confirme|confirma|regularize|complete|valide") or solicita(
        # "Acesse ... para confirmar seus dados" explicita a finalidade do comando.
        sms, r"(?:atualizar|confirmar|regularizar|completar|validar) (?:seu |seus |o |os )?(?:cadastro|dados)",
        verbos=r"acesse|clique|entre"
    )
