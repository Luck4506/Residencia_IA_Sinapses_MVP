# FINALIDADE: Feature 20/24 — URL com domínio da lista fixa de encurtadores da versão 1.
# EXECUÇÃO: Recebe o texto na representação esperada pelo extrator e devolve o atributo correspondente. Não decide se o SMS é golpe.
"""URL com domínio da lista fixa de encurtadores da versão 1."""

from extrator_features.bibliotecas.apoio_02_urls import ENCURTADORES, dominio, extrair_urls


def classificar(sms: str) -> int:
    # Compara o host real completo; tamanho do link não é critério.
    return int(any(dominio(url) in ENCURTADORES for url in extrair_urls(sms)))
