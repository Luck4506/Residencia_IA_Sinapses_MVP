# FINALIDADE: Extração estrutural de URLs, sem abrir os endereços encontrados.
# EXECUÇÃO: É importado e chamado pelo fluxo da API; não precisa ser iniciado manualmente.
"""Extração estrutural de URLs, sem abrir os endereços encontrados."""

# BIBLIOTECAS UTILIZADAS: re, ipaddress e urllib.parse são da biblioteca padrão.
# re encontra candidatos; urlsplit separa esquema, host, porta, caminho e query.
# Ler hostname evita confundir "bit.ly.exemplo.com" ou "bit.ly@outro.com"
# com o serviço bit.ly. ipaddress valida endereços IP quando não há domínio.
# Nada aqui resolve DNS, segue redirecionamentos ou faz chamadas de rede.
import ipaddress
import re
from urllib.parse import urlsplit

from extrator_features.apoio_02_regras import normalizar


# Lista fixa da versão 1; não significa que todos os serviços estejam ativos.
ENCURTADORES = frozenset({"bit.ly", "tinyurl.com", "t.co", "is.gd", "ow.ly"})
_CANDIDATO = re.compile(
    r"(?i)(?<![\w@])(?:https?://|www\.)[^\s<>\"']+|"
    r"(?<![\w@./-])(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+"
    r"(?:com|org|net|edu|gov|br|io|app|dev|ly|co|gd|me|xyz|online|site)"
    r"(?![\w.-])(?:/[^\s<>\"']*)?"
)


def extrair_urls(sms: str) -> list[str]:
    normalizar(sms)  # Valida o tipo sem modificar o endereço original.
    urls = []
    for candidato in _CANDIDATO.finditer(sms):
        url = candidato.group().rstrip(".,;:!?)]}")
        try:
            partes = urlsplit(url if "://" in url else "https://" + url)
            host = partes.hostname or ""
            partes.port  # Rejeita portas malformadas e números fora de faixa.
            try:
                ipaddress.ip_address(host)
                valido = True
            except ValueError:
                valido = bool(re.fullmatch(
                    r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
                    r"(?:[a-z]{2,63}|xn--[a-z0-9-]+)", host, re.I
                ))
            if valido:
                urls.append(url)
        except ValueError:
            continue
    return urls


def dominio(url: str) -> str:
    host = urlsplit(url if "://" in url else "https://" + url).hostname or ""
    return host.lower().removeprefix("www.")
