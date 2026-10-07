"""Regressões do contrato, OR cadastral e inferência real."""
import pytest
from fastapi.testclient import TestClient
from api.main import app
from extrator_features.etapa_01_classificador import analisar_sms, NOMES

@pytest.mark.parametrize('mensagem,esperado', [
    ('Envie seu CPF.', 1), ('Atualize seu cadastro.', 1),
    ('Envie seu CPF e atualize seu cadastro.', 1),
    ('Nossa reunião será amanhã.', 0), ('Não envie seu CPF.', 0),
    ('Ligue para nossa central.', 0),
])
def test_contrato_extrator(mensagem, esperado):
    features = analisar_sms(mensagem, gramatica={'aceitos': [], 'ignorados': []})['features']
    assert len(features) == 22
    assert features['solicita_dados_cadastro'] == esperado
    assert not {'solicita_ligacao', 'solicita_dados_pessoais', 'solicita_atualizacao_cadastro'} & features.keys()

@pytest.fixture(scope='module')
def client():
    with TestClient(app) as c:
        assert c.get('/saude').json()['classificacao_disponivel'], c.get('/saude').json()
        yield c

@pytest.mark.parametrize('texto', ['', '   ', 'x' * 5001])
def test_validacao(client, texto):
    assert client.post('/analisar', json={'mensagem': texto}).status_code == 422

def test_resultado_real(client):
    mensagem = 'Urgente! Sua conta será bloqueada. Envie seu CPF e atualize seu cadastro.'
    response = client.post('/analisar', json={'mensagem': mensagem})
    assert response.status_code == 200, response.text
    d = response.json()
    assert 0 <= d['score_golpe'] <= 1
    assert d['classe'] == int(d['score_golpe'] >= 0.55)
    assert set(d['features']) == set(NOMES)
    assert set(d['features_binarias'].values()) <= {0, 1}
    assert sum(d['features_clusters'].values()) == 1
    assert sum(v for k, v in d['features_binarias'].items() if k.startswith('carga_emocional_')) == 1
    assert all(d['features'][f['feature']] > 0 and f['contribuicao'] > 0 for f in d['features_importantes'])

def test_cors_local(client):
    r = client.options('/analisar', headers={'Origin':'http://localhost:8080', 'Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'content-type'})
    assert r.headers['access-control-allow-origin'] == 'http://localhost:8080'
