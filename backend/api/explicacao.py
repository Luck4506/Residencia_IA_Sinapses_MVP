"""Texto determinístico, baseado somente nos sinais destacados na análise."""
EXPLICACOES = {
    'solicita_senha': 'um pedido de senha, que pode expor sua conta',
    'solicita_codigo_autenticacao': 'um pedido de código de autenticação, que pode permitir acesso à sua conta',
    'solicita_dados_bancarios': 'um pedido de dados bancários, que exige confirmar o destinatário',
    'solicita_dados_cartao': 'um pedido de dados do cartão, que pode permitir compras indevidas',
    'solicita_dados_cadastro': 'um pedido de dados ou atualização cadastral, que exige verificar quem os receberá',
    'solicita_pagamento': 'um pedido de pagamento, que exige conferir o beneficiário',
    'solicita_clique': 'um convite para clicar, que exige verificar o destino',
    'menciona_bloqueio_conta': 'uma menção a bloqueio, que pode pressionar você a agir',
    'carga_emocional': 'expressões emocionais, que podem influenciar sua decisão',
    'possui_urgencia': 'urgência, que pode reduzir seu tempo para conferir o pedido',
    'possui_ameaca': 'uma ameaça, que pode provocar uma reação por medo',
    'possui_linguagem_alarmista': 'linguagem alarmista, que pode dificultar uma avaliação calma',
    'possui_recompensa': 'uma recompensa, que pode incentivar uma ação sem conferência',
    'possui_reembolso': 'uma menção a reembolso, que merece confirmação no canal oficial',
    'possui_vantagem_inesperada': 'uma vantagem inesperada, que pode despertar interesse sem contexto',
    'possui_oferta_financeira': 'uma oferta financeira, cujas condições precisam ser verificadas',
    'possui_url': 'um link, cujo endereço precisa ser conferido',
    'possui_url_encurtada': 'um link encurtado, que dificulta reconhecer o destino',
    'possui_telefone': 'um telefone, cuja presença não confirma a identidade do remetente',
    'possui_pix': 'uma menção a Pix, que merece atenção ao destinatário de eventuais pagamentos',
    'possui_erros_ortografia_gramatica': 'erros de escrita, que merecem atenção ao contexto',
    'possui_chamada_acao': 'uma instrução para agir, que merece ser conferida antes de seguir',
}


def explicar_sinais(sinais):
    trechos = [EXPLICACOES[item['feature']] for item in sinais if item['feature'] in EXPLICACOES][:5]
    if not trechos:
        return ('Não há sinais destacados para explicar nesta análise. '
                'Isso não garante que a mensagem seja segura: o modelo também considera o texto completo.')
    enumeracao = '; '.join(trechos)
    return f'A análise identificou {enumeracao}. Esses sinais pedem atenção, mas não comprovam um golpe por si só.'
