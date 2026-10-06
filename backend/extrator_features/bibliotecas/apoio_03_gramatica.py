# FINALIDADE: LanguageTool pt-BR: dicionário e regras gramaticais mantidos pelo projeto.
# EXECUÇÃO: É importado e chamado pelo fluxo da API; não precisa ser iniciado manualmente.
"""LanguageTool pt-BR: dicionário e regras gramaticais mantidos pelo projeto.

O servidor Java é LOCAL. Não usamos a API pública. URLs são mascaradas
preservando offsets. Sugestões estilísticas e de tipografia são excluídas:
contam apenas issue_type 'misspelling' e 'grammar'. Não corrigimos o texto.
"""

from extrator_features.bibliotecas.apoio_01_texto import validar
from extrator_features.bibliotecas.apoio_02_urls import mascarar_urls


class Corretor:
    def __init__(self, versao="6.8"):
        self.versao = versao
        self._tool = None

    def detectar_erros(self, sms: str) -> list[dict]:
        validar(sms)
        if not sms.strip():
            return []
        texto = mascarar_urls(sms)
        if not texto.strip():
            return []
        if self._tool is None:
            try:
                import language_tool_python
                self._tool = language_tool_python.LanguageTool(
                    "pt-BR", language_tool_download_version=self.versao)
            except Exception as exc:
                raise RuntimeError("LanguageTool local indisponível. Instale Java 17+ e as dependências; a primeira execução baixa o servidor. A análise não foi tratada como zero erros.") from exc
        erros = []
        for m in self._tool.check(texto):
            if m.rule_issue_type not in {"misspelling", "grammar"}:
                continue
            erros.append({"trecho": sms[m.offset:m.offset + m.error_length],
                          "inicio": m.offset, "comprimento": m.error_length,
                          "tipo": "ortografia" if m.rule_issue_type == "misspelling" else "gramatica",
                          "regra": m.rule_id, "mensagem": m.message,
                          "sugestoes": list(m.replacements[:5])})
        return erros

    def close(self):
        if self._tool is not None:
            self._tool.close()
            self._tool = None
