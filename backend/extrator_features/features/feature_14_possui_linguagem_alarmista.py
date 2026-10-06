# FINALIDADE: Feature 14/24 — Vocabulário explícito de perigo, preocupação ou gravidade.
# EXECUÇÃO: Recebe o texto na representação esperada pelo extrator e devolve o atributo correspondente. Não decide se o SMS é golpe.
"""Vocabulário explícito de perigo, preocupação ou gravidade."""

import re
from extrator_features.apoio_02_regras import afirmacao, trechos


def classificar(sms: str) -> int:
    # Caixa alta e exclamações isoladas não bastam, nem apenas "imediatamente".
    # 'Capitalismo da atenção' não é um chamado de alerta.
    if any(re.match(r"^atencao\b", t) for t in trechos(sms)):
        return 1
    return afirmacao(sms, r"alerta(?: maximo)?|risco (?:imediato|iminente)|"
                     r"situacao (?:grave|critica)|(?:voce esta em |sua conta esta em )?perigo|"
                     r"atividade suspeita|fraude detectada|emergencia|movimentacao estranha|"
                     r"falha de seguranca|problema grave|acesso (?:foi |esta )?comprometido")
