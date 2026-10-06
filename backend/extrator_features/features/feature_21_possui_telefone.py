# FINALIDADE: Feature 21/24 — Telefone brasileiro: máscaras + phonenumbers + exigência de região BR.
# EXECUÇÃO: Recebe o texto na representação esperada pelo extrator e devolve o atributo correspondente. Não decide se o SMS é golpe.
"""Telefone brasileiro: máscaras + phonenumbers + exigência de região BR."""
import phonenumbers
from extrator_features.bibliotecas.apoio_04_telefone import extrair_telefones as candidatos

def extrair_telefones(sms):
    return [trecho for trecho in candidatos(sms)
            if phonenumbers.is_valid_number_for_region(phonenumbers.parse(trecho, 'BR'), 'BR')]

def classificar(sms):
    return int(bool(extrair_telefones(sms)))
