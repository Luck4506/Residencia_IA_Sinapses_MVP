# FINALIDADE: Feature 12/24 — Pressão temporal associada ao pedido, não ao fato narrado em outra oração.
# EXECUÇÃO: Recebe o texto na representação esperada pelo extrator e devolve o atributo correspondente. Não decide se o SMS é golpe.
"""Pressão temporal associada ao pedido, não ao fato narrado em outra oração."""
import re
from extrator_features.apoio_02_regras import afirmacao, acoes, contem, normalizar, trechos


def classificar(sms: str) -> int:
    texto = normalizar(sms)
    if contem(texto, r'nao perca tempo'):
        return 1
    if afirmacao(sms, r'urgente|urgencia|ultima chance'):
        return 1
    if contem(texto, r'sem pressa|nao (?:e |ha )?urgencia'):
        return 0
    if afirmacao(sms, r'(?:hoje|agora)(?:\s+\w+){0,3}\s+prazo final|prazo final(?:\s+\w+){0,3}\s+hoje'):
        return 1
    if not list(acoes(texto)):
        return 0
    # Contagem regressiva explícita pode estar na frase adjacente ao pedido.
    if contem(texto, r'(?:tem so|restam|voce tem somente) (?:[1-9]|[1-5][0-9]|60) minutos?'):
        return 1
    tempo = (r'agora|imediatamente|hoje|hj|ja|em poucos minutos|o quanto antes|'
             r'(?:em|ate|dentro de|prazo de) (?:[1-9]|1[0-9]|2[0-4]|uma|duas|tres|quatro|seis|doze|vinte e quatro) horas?|'
             r'(?:em|ate|dentro de|prazo de) (?:[1-9]|[1-5][0-9]|60) minutos?')
    # Prazo/necessidade explícitos podem preceder o comando em outra frase.
    if afirmacao(sms, rf'(?:vence|expira|vai expirar|ira expirar|valido|valida)(?:\s+\w+){{0,3}}\s+(?:{tempo})|'
                       r'(?:somente ate|para|ainda) hoje|'
                       r'(?:preciso disso|precisamos validar seu acesso) agora|'
                       r'(?:comeca|e) hoje'):
        return 1
    for trecho in trechos(sms):
        for acao in acoes(trecho):
            if acao.group() == 'desconsidere':
                continue
            # Não propaga o prazo de uma ação do remetente ('que faço o depósito hoje').
            depois = re.split(r'\b(?:quando|que (?:eu )?(?:faco|vou))\b', trecho[acao.end():], maxsplit=1)[0]
            # 'Já foi enviado' descreve estado passado; não equivale a 'envie já'.
            depois = re.sub(r'\bja\s+(?:foi|esta|tem|terminou|recebeu)\b', 'estado_anterior', depois)
            if contem(depois, tempo):
                return 1
            if re.search(r'\b(?:hoje|agora|imediatamente)\s*,?\s*$', trecho[:acao.start()]):
                return 1
    return 0
