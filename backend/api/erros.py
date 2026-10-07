# FINALIDADE: Apoio — Definir o erro de indisponibilidade compartilhado pelas etapas.
# EXECUÇÃO: Pode ser utilizado em qualquer etapa; não representa uma etapa sequencial.
"""Erros de disponibilidade compartilhados pelas etapas do fluxo."""


class Indisponivel(RuntimeError):
    pass
