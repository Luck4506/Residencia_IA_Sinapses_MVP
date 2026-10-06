# FINALIDADE: Validar texto e preservar links, e-mails e marcadores nas substituições.
# EXECUÇÃO: Apoio compartilhado pela normalização e anonimização.
import re

# Preserva URLs explícitas, e-mails e marcadores, como <NOME>.
# Domínios sem protocolo/www não são reconhecidos por esta proteção simples.
TRECHOS_PROTEGIDOS = re.compile(
    r"(?:https?://|www\.)[^\s<>]+|[\w.+-]+@[\w.-]+\.[\w-]+|<[^<>\n]+>",
    re.IGNORECASE,
)


def validar_texto(texto):
    if not isinstance(texto, str):
        raise TypeError("A mensagem precisa ser texto.")
    return texto


def transformar_trechos(texto, transformar):
    validar_texto(texto)
    partes = []
    inicio = 0
    for trecho in TRECHOS_PROTEGIDOS.finditer(texto):
        partes.extend((transformar(texto[inicio:trecho.start()]), trecho.group()))
        inicio = trecho.end()
    partes.append(transformar(texto[inicio:]))
    return "".join(partes)
