# FINALIDADE: Substituir nomes da lista revisada por <NOME>, como no notebook.
# EXECUÇÃO: Terceira transformação opcional; não garante anonimização completa.
import re

from .apoio_01_vocabulario import NOMES_PESSOAIS
from .apoio_02_texto import transformar_trechos, validar_texto


def anonimizar_mensagem(texto, nomes=None):
    """Mascara nomes conhecidos; preserva URLs, e-mails e marcadores existentes.

    CPF, telefone, endereço e nomes fora da lista não são anonimizados.
    Palavras como Jardim e Lima podem ser nomes ou outros termos: revise a saída.
    """
    validar_texto(texto)
    nomes = NOMES_PESSOAIS if nomes is None else tuple(nomes)
    if not nomes:
        return texto
    if any(not isinstance(n, str) or not n for n in nomes):
        raise ValueError("Os nomes devem ser textos não vazios.")
    alternativas = "|".join(re.escape(n) for n in sorted(nomes, key=len, reverse=True))
    padrao = re.compile(rf"(?<!\w)(?:{alternativas})(?!\w)", re.IGNORECASE)
    return transformar_trechos(texto, lambda trecho: padrao.sub("<NOME>", trecho))
