# FINALIDADE: linkify-it-py encontra links; urllib e ipaddress conferem o host real.
# EXECUÇÃO: É importado e chamado pelo fluxo da API; não precisa ser iniciado manualmente.
"""linkify-it-py encontra links; urllib e ipaddress conferem o host real.

A biblioteca reconhece limites, pontuação e domínios sem esquema. Não abre
URLs. A lista de encurtadores é curada, pois tamanho não identifica um serviço.
"""

from functools import lru_cache
from ipaddress import ip_address
from urllib.parse import urlsplit

from extrator_features.bibliotecas.apoio_01_texto import validar

ENCURTADORES = frozenset({"bit.ly", "tinyurl.com", "t.co", "is.gd", "ow.ly"})


@lru_cache(maxsize=1)
def _extrator():
    from linkify_it import LinkifyIt
    return LinkifyIt().set({"fuzzy_email": False})


def dominio(url: str) -> str:
    """Obtém hostname; usuário@host e caminho não são parte do domínio."""
    try:
        partes = urlsplit(url if "://" in url else "https://" + url.lstrip("/"))
        _ = partes.port  # Também rejeita portas inválidas.
        host = (partes.hostname or "").rstrip(".").lower()
        try:
            ip_address(host)
            return host
        except ValueError:
            pass
        ascii_host = host.encode("idna").decode("ascii")
        partes_host = ascii_host.split(".")
        if len(partes_host) < 2 or len(ascii_host) > 253 or partes_host[-1].isdigit():
            return ""
        if not all(p and len(p) <= 63 and p[0] != "-" and p[-1] != "-"
                   and all(c.isalnum() or c == "-" for c in p) for p in partes_host):
            return ""
        return ascii_host
    except (ValueError, UnicodeError):
        return ""


def ocorrencias(sms: str) -> list[dict]:
    validar(sms)
    if not sms.strip():
        return []
    return [{"texto": m.raw, "url": m.url, "dominio": dominio(m.url),
             "inicio": m.index, "fim": m.last_index}
            for m in (_extrator().match(sms) or [])
            if m.schema in ("", "http:", "https:", "//") and dominio(m.url)]


def extrair_urls(sms: str) -> list[str]:
    return [m["texto"] for m in ocorrencias(sms)]


def mascarar_urls(sms: str) -> str:
    """Substitui URLs por espaços mantendo posições dos demais caracteres."""
    caracteres = list(validar(sms))
    for m in ocorrencias(sms):
        caracteres[m["inicio"]:m["fim"]] = " " * (m["fim"] - m["inicio"])
    return "".join(caracteres)
