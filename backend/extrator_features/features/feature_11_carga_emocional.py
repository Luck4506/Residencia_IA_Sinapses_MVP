# FINALIDADE: Feature 11/24 — Proporção lexical preservada, agora com faixas baixa/média/alta congeladas.
# EXECUÇÃO: Recebe o texto na representação esperada pelo extrator e devolve o atributo correspondente. Não decide se o SMS é golpe.
"""Proporção lexical preservada, agora com faixas baixa/média/alta congeladas.

Os limites são os tercis das proporções POSITIVAS da referência textual;
zeros ficam na faixa baixa. Nenhum rótulo Baixo/Médio/Alto treina as faixas.
Os limites são carregados de configuracao_emocao.json e nunca recalculados
por mensagem ou por lote. São relativos ao corpus, não escalas psicológicas.
"""
import json
import re
from pathlib import Path
from functools import lru_cache
from extrator_features.apoio_02_regras import normalizar
from extrator_features.bibliotecas.apoio_02_urls import mascarar_urls

LEXICO_EMOCIONAL = frozenset('medo perigo perigoso perigosa panico terror ameaca preocupacao preocupado preocupada ansiedade ansioso ansiosa triste tristeza raiva odio desespero desesperado desesperada alegria alegre feliz felicidade amor carinho esperanca surpresa surpreso vergonha culpa confianca parabens urgente urgencia alerta grave risco perder perda'.split())

@lru_cache(maxsize=1)
def configuracao():
    dados = json.loads((Path(__file__).parents[1]/'configuracao_emocao.json').read_text())
    if not 0 < dados['limite_baixa'] < dados['limite_media'] <= 1:
        raise ValueError('Limites emocionais inválidos.')
    return dados

def medir(sms):
    limpo = re.sub(r'\S+@\S+', ' ', mascarar_urls(sms))
    palavras = re.findall(r'\b[a-z]+\b', normalizar(limpo))
    emocionais = [p for p in palavras if p in LEXICO_EMOCIONAL]
    return {'palavras_analisaveis': len(palavras), 'palavras_emocionais': emocionais,
            'ocorrencias_emocionais': len(emocionais),
            'proporcao': len(emocionais)/len(palavras) if palavras else 0.0}

def categorizar(proporcao):
    if not 0 <= proporcao <= 1: raise ValueError('Proporção fora de 0 a 1.')
    c = configuracao()
    # Empates nos limites pertencem à faixa inferior, inclusive zero.
    return 'baixa' if proporcao <= c['limite_baixa'] else 'média' if proporcao <= c['limite_media'] else 'alta'

def classificar(sms):
    return categorizar(medir(sms)['proporcao'])
