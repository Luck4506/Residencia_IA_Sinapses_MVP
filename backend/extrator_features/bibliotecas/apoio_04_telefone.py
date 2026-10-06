# FINALIDADE: Detecta telefones com phonenumbers, port da libphonenumber do Google.
# EXECUÇÃO: É importado e chamado pelo fluxo da API; não precisa ser iniciado manualmente.
"""Detecta telefones com phonenumbers, port da libphonenumber do Google.

PhoneNumberMatcher usa metadados de planos de numeração, comprimentos e
prefixos. Região padrão BR interpreta números nacionais; + aceita números
internacionais. Leniency.VALID exige validade estrutural, sem confirmar linha
ativa. Mascaramos URLs e identificadores rotulados antes da extração para
reduzir confusão com CPF, valores e protocolos. CPF sem rótulo ainda é ambíguo.

Exemplo positivo: 'Ligue para (19) 99999-1234.'
Contraexemplo: 'CPF: 19999991234'. Presença não implica pedido de ligação.
"""

from extrator_features.bibliotecas.apoio_01_texto import validar
from extrator_features.bibliotecas.apoio_02_urls import mascarar_urls


def extrair_telefones(sms: str) -> list[str]:
    validar(sms)
    if not sms.strip():
        return []
    import phonenumbers
    import regex

    texto = mascarar_urls(sms)
    mascaras = (
        r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b",
        r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b",
        r"\b\d{5}-\d{3}\b",
        r"\b\d{2}[/-]\d{2}[/-]\d{2,4}\b",
        r"(?:R\$|US\$|BRL)\s*[\d.,]+",
        r"\b[\d.,]+\s*(?:reais|centavos)\b",
        r"\b(?:cpf|cnpj|cep|c[oó]digo(?: de (?:autentica[cç][aã]o|verifica[cç][aã]o|acesso|seguran[cç]a))?|token|pedido|protocolo|boleto|conta|ag[eê]ncia)"
        r"\s*(?:n[uú]mero|n[ºo.]|[eé]|:)?\s*[:#-]?\s*\d[\d ./-]*",
    )
    for padrao in mascaras:
        texto = regex.sub(padrao, lambda m: " " * len(m.group()), texto, flags=regex.I)
    return [sms[m.start:m.end] for m in phonenumbers.PhoneNumberMatcher(
        texto, "BR", leniency=phonenumbers.Leniency.VALID)]


def classificar(sms: str) -> int:
    """1 quando há ao menos um número válido segundo os metadados."""
    return int(bool(extrair_telefones(sms)))
