# FINALIDADE: Feature 02/24 — Pedido de código de autenticação; códigos de produto e cupom não contam.
# EXECUÇÃO: Recebe o texto na representação esperada pelo extrator e devolve o atributo correspondente. Não decide se o SMS é golpe.
"""Pedido de código de autenticação; códigos de produto e cupom não contam."""

from extrator_features.apoio_02_regras import contem, solicita, trechos

# Atualizar um token/dispositivo não é pedir o valor de um código (PDF p. 3).
VERBOS = r"informe|envie|digite|compartilhe|forneca|insira|encaminhe|mande|manda|envia|passe|revele|confirme|confirma|use|utilize|copie"
CONTEXTO = r"autenticacao|verificacao|confirmacao|validacao|sms|whatsapp|acesso|login|2fa|dois fatores|seguranca"


def classificar(sms: str) -> int:
    for trecho in trechos(sms):
        alvo = r"token|otp|codigo (?:de |do |da )?(?:autenticacao|verificacao|confirmacao|validacao|sms|whatsapp|acesso|login|2fa|dois fatores)|codigo (?:recebido|enviado)(?:\s+\w+){0,4}\s+(?:sms|whatsapp)"
        # "Código de segurança" com cartão é dado de cartão, não autenticação.
        if not contem(trecho, r"cartao|cvv|cvc"):
            alvo += r"|codigo de seguranca"
        # Aceita "código de 6 números que recebeu por SMS", como no dicionário.
        alvo += r"|codigo de [46] (?:numeros|digitos)(?:\s+\w+){0,9}\s+(?:sms|whatsapp|celular|autenticacao|verificacao)"
        # Número entre 'código' e sua finalidade; nunca só cupom/produto/rastreio.
        if not contem(trecho, r"cupom|produto|rastreio|rastreamento|cartao|cvv|cvc"):
            alvo += rf"|codigo(?:\s+\w+){{0,8}}\s+(?:{CONTEXTO}|acessar sua conta|acessar o app|confirmar a operacao|cadastrar sua chave)"
            alvo += r"|[0-9]{4,8} para validar seu telefone"
            if contem(sms.lower(), r"autentica[cç][aã]o"):
                alvo += r"|codigo para confirmar a operacao"
        if solicita(trecho, alvo, verbos=VERBOS):
            return 1
    # Elipse explícita e limitada: 'Seu código de acesso ... . Digite na tela de login'.
    partes = trechos(sms)
    for anterior, atual in zip(partes, partes[1:]):
        if contem(anterior, rf"codigo (?:de |do |da )?(?:{CONTEXTO})"):
            if solicita(atual, r"tela de login|campo de verificacao", verbos=r"digite|insira"):
                return 1
    return 0
