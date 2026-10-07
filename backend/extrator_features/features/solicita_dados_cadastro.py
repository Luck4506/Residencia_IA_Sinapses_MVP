"""Dados pessoais OU atualização cadastral, conforme o contrato treinado."""
from .feature_04_solicita_dados_pessoais import classificar as dados_pessoais
from .feature_06_solicita_atualizacao_cadastro import classificar as atualizacao


def classificar(sms: str) -> int:
    return int(bool(dados_pessoais(sms) or atualizacao(sms)))
