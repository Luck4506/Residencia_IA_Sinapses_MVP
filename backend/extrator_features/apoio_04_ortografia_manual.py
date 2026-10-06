# FINALIDADE: Erros explícitos de um conjunto fixo de regras; não é um corretor completo.
# EXECUÇÃO: É importado e chamado pelo fluxo da API; não precisa ser iniciado manualmente.
"""Erros explícitos de um conjunto fixo de regras; não é um corretor completo."""

# MÉTODO UTILIZADO: lista manual de grafias incorretas e padrões gramaticais.
# re encontra apenas correspondências completas, sem penalizar uma palavra por
# ser desconhecida. Por isso nomes próprios, emojis, "vc", "pq", "blz", gírias,
# falta de acentos e falta de pontuação não são erros automáticos nesta versão.
# Não usamos corretor externo ou modelo. A cobertura é deliberadamente pequena;
# 0 significa nenhum erro das regras cadastrado abaixo, não texto perfeito.
# URLs são retiradas para não interpretar nomes de domínio como erros de escrita.
# detectar_erros expõe ocorrências e sugestões, sem alterar o SMS recebido.
import re

from extrator_features.apoio_02_regras import normalizar
from extrator_features.bibliotecas.apoio_02_urls import extrair_urls

GRAFIAS = {
    "bloquiada": "bloqueada", "bloquiado": "bloqueado",
    "suspetia": "suspeita", "suspetio": "suspeito",
    "suspeitto": "suspeito", "atualise": "atualize",
    "atualisar": "atualizar", "cadasto": "cadastro",
    "cadastrro": "cadastro", "senhha": "senha",
    "imedi-atamente": "imediatamente", "imediatamnete": "imediatamente",
    "comfirme": "confirme", "comfirmar": "confirmar",
    "trasferencia": "transferência", "tranferencia": "transferência",
    "pagameto": "pagamento", "recebimeto": "recebimento",
    "emprestimoos": "empréstimos", "voçe": "você",
}
GRAMATICA = {
    r"\bsua conta foram\b": "sua conta foi",
    r"\bseus dados foi\b": "seus dados foram",
    r"\bvoce (?:ganhamos|ganharam)\b": "você ganhou",
    r"\bos dados esta\b": "os dados estão",
}


def detectar_erros(sms: str) -> list[dict[str, str]]:
    texto = sms
    for url in extrair_urls(sms):
        texto = texto.replace(url, " ")
    # Mantém acentos na busca de grafias: "voçe" não pode virar o correto "voce".
    texto = texto.casefold()
    erros = []
    for grafia, sugestao in GRAFIAS.items():
        for achado in re.finditer(rf"\b{re.escape(grafia)}\b", texto):
            erros.append({"trecho": achado.group(), "sugestao": sugestao, "tipo": "ortografia"})
    for padrao, sugestao in GRAMATICA.items():
        for achado in re.finditer(padrao, normalizar(texto)):
            erros.append({"trecho": achado.group(), "sugestao": sugestao, "tipo": "gramatica"})
    return erros


def classificar(sms: str) -> int:
    return int(bool(detectar_erros(sms)))
