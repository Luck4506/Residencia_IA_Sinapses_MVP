# FINALIDADE: Feature 08/24 — Comando para abrir link, endereço ou botão mencionado no SMS.
# EXECUÇÃO: Recebe o texto na representação esperada pelo extrator e devolve o atributo correspondente. Não decide se o SMS é golpe.
"""Comando para abrir link, endereço ou botão mencionado no SMS."""

from extrator_features.apoio_02_regras import solicita
from extrator_features.apoio_03_urls import extrair_urls


def classificar(sms: str) -> int:
    texto = sms
    # Substitui cada URL por uma marca para pontos do domínio não quebrarem frases.
    for url in extrair_urls(sms):
        texto = texto.replace(url, " endereco_url ")
    # 'Veja/Saiba mais' só conta acompanhado do destino, nunca URL isolada.
    if solicita(texto, r"endereco_url|link|site", verbos=r"veja|saiba|confirme|confirma"):
        return 1
    return solicita(texto, r"aqui|link|botao|endereco|endereco_url|site|"
                    r"para (?:confirmar|continuar|atualizar|resgatar|receber)",
                    verbos=r"clique|acesse|toque|abra")
