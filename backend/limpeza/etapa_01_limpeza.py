# FINALIDADE: Limpar espaços externos e, opcionalmente, emojis de uma mensagem.
# EXECUÇÃO: Primeira transformação opcional; adaptada do notebook de limpeza simplificada.
import re

from .apoio_02_texto import validar_texto, transformar_trechos

PADRAO_EMOJI = re.compile('[🌀-🗿😀-🙏🚀-\U0001f6ff🜀-🝿🞀-\U0001f7ff🠀-\U0001f8ff🤀-🧿🨀-\U0001faff☀-⛿✀-➿🇦-🇿]+')


def limpar_mensagem(texto, *, remover_emojis=True):
    """Preserva caixa, acentos, números e pontuação; não corrige ortografia.

    As faixas de emoji reproduzem o notebook e não cobrem todo o Unicode.
    URLs, e-mails e marcadores são preservados durante as substituições.
    """
    validar_texto(texto)

    def limpar(trecho):
        if remover_emojis:
            trecho = PADRAO_EMOJI.sub("", trecho)
            trecho = trecho.replace("\ufe0f", "").replace("\u200d", "")
        return re.sub(r"[ \t]{2,}", " ", trecho)

    return transformar_trechos(texto, limpar).strip()
