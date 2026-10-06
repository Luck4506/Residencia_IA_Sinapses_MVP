# FINALIDADE: Confere extração e clusters usando Java/LanguageTool reais.
# EXECUÇÃO: Executar separadamente durante a verificação; não participa do atendimento de cada SMS.
"""Teste manual com Java/LanguageTool reais: python tests/verificar_02_gramatica_real.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from api.etapa_01_main import criar_app
from api.etapa_04_servico import ServicoSMS

servico = ServicoSMS()
with TestClient(criar_app(lambda: servico)) as cliente:
    resposta = cliente.post('/extrair', json={'mensagem': 'Informe sua senha agora.'})
    assert resposta.status_code == 200, resposta.text
    dados = resposta.json()
    assert len(dados['features_completas']) == 30
    assert dados['features']['solicita_senha'] == 1
    assert sum(dados['features_clusters'].values()) == 1
    assert cliente.get('/saude').json()['gramatica_verificada']
    print('LanguageTool real + extrator + K-means: 30 atributos, HTTP 200.')
    assert cliente.post('/analisar', json={'mensagem': 'Informe sua senha agora.'}).status_code == 503
    print('XGBoost ausente: HTTP 503, sem classificação inventada.')
