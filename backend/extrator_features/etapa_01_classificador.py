# FINALIDADE: Motor revisado: extrai conforme o PDF, sem aprender rótulos questionados.
# EXECUÇÃO: É importado e chamado pelo fluxo da API; não precisa ser iniciado manualmente.
"""Motor revisado: extrai conforme o PDF, sem aprender rótulos questionados.

Cada saída expõe método e evidência; 0 significa não detectado pelo método,
nunca certificação de que a condição está ausente. Não prevê possivel_golpe.
"""
import re,json
from pathlib import Path
from importlib import import_module
from extrator_features.apoio_02_regras import normalizar, INFINITIVOS
from extrator_features.bibliotecas.apoio_02_urls import ocorrencias, ENCURTADORES
from extrator_features.features import feature_11_carga_emocional as carga_emocional, feature_21_possui_telefone as possui_telefone, feature_23_possui_erros_ortografia_gramatica as possui_erros_ortografia_gramatica
from extrator_features.apoio_01_gramatica import gramatica_lote

PASTA=Path(__file__).parent
DEFINICOES=json.loads((PASTA/'definicoes.json').read_text())
NOMES=[d['nome'] for d in DEFINICOES]
BINARIAS=[n for n in NOMES if n!='carga_emocional']
MODULOS={n:import_module(f'{__package__}.features.feature_{i:02d}_{n}') for i,n in enumerate(NOMES, 1)}
ESTRUTURAIS={'possui_url','possui_url_encurtada','possui_telefone','possui_pix','possui_erros_ortografia_gramatica','carga_emocional'}


def preparar(sms):
    # Não deixa domínio/caminho de URL virar intenção; preserva um alvo de clique.
    texto=sms
    for item in reversed(ocorrencias(sms)):
        texto=texto[:item['inicio']]+' endereco_url '+texto[item['fim']:]
    texto=normalizar(texto)
    for imperativo, infinitivo in INFINITIVOS.items():
        texto=re.sub(rf'\b(?:(?:voce )?(?:poderia|pode|deveria)|pedimos para|solicitamos para)\s+{infinitivo}\b',imperativo,texto)
    return re.sub(r'\b(?:solicitamos|pedimos) (?:o )?envio (?:de|do|da)\b','envie',texto)


def analisar_sms(sms, gramatica=None):
    if not isinstance(sms,str): raise TypeError('A mensagem precisa ser texto.')
    if gramatica is None: gramatica=gramatica_lote([sms],PASTA/'cache_languagetool')[0]
    texto=preparar(sms)
    valores={}
    detalhes={}
    urls=ocorrencias(sms)
    gr=possui_erros_ortografia_gramatica.analisar(sms,gramatica)
    for nome,mod in MODULOS.items():
        if nome=='possui_erros_ortografia_gramatica':
            valor=int(bool(gr['aceitos']))
            evidencia=json.dumps(gr,ensure_ascii=False)
            metodo='LanguageTool pt-BR 6.8 filtrado + lista manual fixa'
        elif nome=='carga_emocional':
            med=carga_emocional.medir(sms); valor=carga_emocional.categorizar(med['proporcao'])
            evidencia=json.dumps(med,ensure_ascii=False); metodo='léxico fixo + tercis positivos congelados'
        elif nome in ESTRUTURAIS:
            valor=mod.classificar(sms)
            if nome=='possui_url': evidencia=json.dumps(urls,ensure_ascii=False)
            elif nome=='possui_url_encurtada': evidencia=json.dumps([u for u in urls if u['dominio'] in ENCURTADORES],ensure_ascii=False)
            elif nome=='possui_telefone': evidencia=json.dumps(possui_telefone.extrair_telefones(sms),ensure_ascii=False)
            else: evidencia='Menção literal de PIX fora de URLs.' if valor else 'PIX não encontrado como palavra fora de URLs.'
            metodo={'possui_url':'linkify-it-py + validação de host','possui_url_encurtada':'host exato em lista fixa','possui_telefone':'phonenumbers / região BR','possui_pix':'regex Unicode / palavra PIX'}[nome]
        else:
            valor=mod.classificar(texto)
            # Teste de suficiência: mostra frase original que sozinha produz 1.
            # Não é atribuição estatística nem prova de correção semântica.
            partes=[p.strip() for p in re.split(r'(?<=[!?;])\s+|(?<=\.)\s+',sms) if p.strip()]
            suficientes=[p for p in partes if valor and mod.classificar(preparar(p))]
            evidencia='Trecho suficiente para a regra: '+min(suficientes,key=len) if suficientes else ('Contexto completo ativou a regra: '+sms if valor else 'Nenhum padrão afirmativo previsto foi detectado; conferir cobertura e contexto.')
            metodo='regra contextual explícita / '+nome+'.py'
        valores[nome]=valor
        detalhes[nome]={'metodo':metodo,'evidencia':evidencia}
    return {'features':valores,'detalhes':detalhes,'medida_emocional':carga_emocional.medir(sms)}


def analisar_lote(textos):
    gram=gramatica_lote(textos,PASTA/'cache_languagetool')
    return [analisar_sms(t,g) for t,g in zip(textos,gram)]
