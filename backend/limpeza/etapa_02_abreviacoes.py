# FINALIDADE: Expandir abreviações isoladas sem diferenciar maiúsculas de minúsculas.
# EXECUÇÃO: Segunda transformação opcional, usando vocabulário padrão ou personalizado.
import re

from .apoio_01_vocabulario import VOCABULARIO_PADRAO
from .apoio_02_texto import transformar_trechos, validar_texto


def normalizar_abreviacoes(texto, vocabulario=None):
    """Substitui em uma passagem, sem reprocessar as palavras inseridas.

    Limites por caracteres de palavra também aceitam d+, ate+ e p/.
    A correspondência mais longa tem prioridade sobre abreviações menores.
    """
    validar_texto(texto)
    vocabulario = VOCABULARIO_PADRAO if vocabulario is None else vocabulario
    if not vocabulario:
        return texto
    if any(not isinstance(k, str) or not k or not isinstance(v, str)
           for k, v in vocabulario.items()):
        raise ValueError("Use abreviações não vazias e substituições em texto.")
    palavras = {k.lower(): v for k, v in vocabulario.items()}
    alternativas = "|".join(re.escape(k) for k in sorted(palavras, key=len, reverse=True))
    padrao = re.compile(rf"(?<!\w)(?:{alternativas})(?!\w)", re.IGNORECASE)
    return transformar_trechos(
        texto, lambda trecho: padrao.sub(lambda m: palavras[m.group().lower()], trecho)
    )
