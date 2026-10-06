# FINALIDADE: Operações compartilhadas pelas regras textuais da versão inicial.
# EXECUÇÃO: É importado e chamado pelo fluxo da API; não precisa ser iniciado manualmente.
"""Operações compartilhadas pelas regras textuais da versão inicial."""

# BIBLIOTECAS UTILIZADAS (todas fazem parte do próprio Python):
# re reconhece padrões textuais por expressões regulares.
# Usamos \b para limites de palavras, alternativas (a|b) para vocabulários e
# quantificadores para limitar a distância entre uma ação e seu complemento.
# unicodedata decompõe caracteres acentuados; removemos somente as marcas de
# acento e convertemos para minúsculas. Assim, "CÓDIGO" e "codigo" coincidem.
# Essas operações ocorrem localmente; não consultam serviços nem enviam o SMS.
import re
import unicodedata


def normalizar(sms: str) -> str:
    if not isinstance(sms, str):
        raise TypeError("O SMS deve ser uma string.")
    texto = unicodedata.normalize("NFKD", sms.casefold())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto).strip()


def contem(texto: str, padrao: str) -> bool:
    """Procura um padrão em texto já normalizado, respeitando palavras inteiras."""
    return re.search(rf"\b(?:{padrao})\b", texto) is not None


def trechos(sms: str) -> list[str]:
    # Não separa em vírgulas: listas como "CPF, nome e endereço" devem sobreviver.
    normalizar(sms)  # Verifica o tipo antes de usar re.split.
    return [normalizar(p) for p in re.split(r"[!?;\n]+|(?<!\d)\.(?!\d)", sms) if p.strip()]


def negado_antes(texto: str, inicio: int) -> bool:
    """Detecta negação local antes do verbo/afirmação, sem eliminar o SMS todo."""
    antes = texto[:inicio]
    return bool(re.search(
        r"\b(?:nao|nunca|jamais|evite|sem)(?:\s+\w+){0,3}\s*$", antes
    ))


ACOES_DADOS = (
    r"informe|envie|digite|confirme|confirma|atualize|compartilhe|forneca|preencha|redefina|altere|"
    # Imperativos informais também são pedidos: "me manda sua senha".
    r"insira|encaminhe|mande|manda|envia|passe|valide|regularize|complete|revele|cadastre-se"
)
ACOES_GERAIS = (
    ACOES_DADOS + r"|clique|acesse|toque|abra|ligue|telefone|chame|contate|"
    r"responda|pague|transfira|deposite|quite|faca|realize|efetue|baixe|"
    r"instale|resgate|receba|contrate|aproveite|resolva|retorne|compareca|"
    r"entre em contato|entre|solicite|envia|manda|me envie|me informe|"
    r"ative|autorize|verifique|consulte|cadastre|participe|avise|aceite|confira|negocie|"
    r"cancele|bloqueie|desbloqueie|reative|simule|garanta|veja|saiba|peca|economize|"
    r"faz|responde|liga|use|utilize|copie|troque|retome|treine|ouca|desconsidere|apresente-se"
)
# Relaciona cada imperativo à forma aceita após "você precisa", "favor" etc.
INFINITIVOS = {
    "informe": "informar", "envie": "enviar", "digite": "digitar",
    "confirme": "confirmar", "atualize": "atualizar", "compartilhe": "compartilhar",
    "forneca": "fornecer", "preencha": "preencher", "insira": "inserir",
    "encaminhe": "encaminhar", "mande": "mandar", "passe": "passar",
    "valide": "validar", "regularize": "regularizar", "complete": "completar",
    "clique": "clicar", "acesse": "acessar", "toque": "tocar", "abra": "abrir",
    "ligue": "ligar", "telefone": "telefonar", "responda": "responder",
    "pague": "pagar", "transfira": "transferir", "deposite": "depositar",
    "quite": "quitar", "faca": "fazer", "realize": "realizar", "efetue": "efetuar",
    "baixe": "baixar", "instale": "instalar", "resgate": "resgatar",
    "receba": "receber", "contrate": "contratar", "resolva": "resolver",
    "retorne": "retornar", "compareca": "comparecer", "solicite": "solicitar",
    "ative": "ativar", "autorize": "autorizar", "verifique": "verificar",
    "consulte": "consultar", "cadastre": "cadastrar", "participe": "participar",
    "avise": "avisar", "aceite": "aceitar", "entre em contato": "entrar em contato",
    "confira": "conferir", "negocie": "negociar",
}
PEDIDO_INDIRETO = (
    r"(?:voce (?:deve|precisa|pode)|favor|por favor|solicitamos(?: que voce)?|"
    r"pedimos(?: que voce)?|e necessario|e preciso|precisamos que voce)\s+"
)


def acoes(texto: str, verbos: str = ACOES_GERAIS):
    """Encontra imperativos e alguns pedidos indiretos, descartando avisos negativos."""
    permitidos = [INFINITIVOS[v] for v in verbos.split("|") if v in INFINITIVOS]
    indireto = "|".join(permitidos) or r"(?!)"
    padrao = rf"\b(?:{verbos}|{PEDIDO_INDIRETO}(?:{indireto}))\b"
    for acao in re.finditer(padrao, texto):
        if negado_antes(texto, acao.start()):
            continue
        # "O banco pede que informe" e falas relatadas não são resolvidos por NLP.
        # Estes casos frequentes evitam tratar uma recusa como um pedido real.
        prefixo = texto[max(0, acao.start() - 70):acao.start()]
        # Relato ou condição não vira imperativo: "o atendente confirma" e
        # "quando você informe" não são resolvidos como pedidos diretos.
        if re.search(r"\b(?:ele|ela|o atendente|a atendente)\s+$", prefixo):
            continue
        if acao.group() == 'faz':
            if re.search(r"\b(?:voce|vc|que|quem)\s+$", prefixo):
                continue
            if not re.match(r"\s+(?:(?:o|um)\s+)?(?:pix|pagamento|deposito|cadastro|isso)\b", texto[acao.end():]):
                continue  # 'Faz tempo' e 'faz bolos' não são comandos.
        if re.search(r"\b(?:nao solicitamos|nao pedimos|nunca pedimos)\b[^,;.!?]*$", prefixo):
            continue
        if acao.group() == "telefone":
            if re.search(r"\b(?:seu|meu|nosso|o|um|este|pelo|do)\s+$", prefixo):
                continue  # Objeto em "informe seu telefone para retorno".
            # O substantivo "telefone" só vale como verbo em "telefone para...".
            if not re.match(r"\s+(?:para|agora|imediatamente)\b", texto[acao.end():]):
                continue
        yield acao


def solicita(sms: str, alvo: str, verbos: str = ACOES_DADOS) -> int:
    """Exige ação afirmativa e complemento próximo, antes de outra ação."""
    for trecho in trechos(sms):
        for acao in acoes(trecho, verbos):
            depois = trecho[acao.end():]
            # Impede "informe seu CPF e nunca compartilhe sua senha" de pedir senha.
            # Usa ações efetivas: o substantivo telefone não encerra a busca
            # em "informe seu telefone". Negação do alvo continua abaixo.
            proxima = next(acoes(depois), None)
            if proxima:
                depois = depois[:proxima.start()]
            # Oito palavras de ligação aceitam artigos, possessivos e listas curtas.
            achado = re.match(rf"(?:\W+\w+){{0,8}}?\W+(?P<alvo>{alvo})\b", depois)
            if achado and not negado_antes(depois, achado.start("alvo")):
                return 1
    return 0


def afirmacao(sms: str, padrao: str) -> int:
    """Busca uma afirmação local que não esteja explicitamente negada."""
    for trecho in trechos(sms):
        for achado in re.finditer(rf"\b(?:{padrao})\b", trecho):
            if not negado_antes(trecho, achado.start()):
                # A negação também pode ocorrer dentro do padrão completo.
                if not contem(achado.group(), r"nao|nunca|jamais|sem"):
                    return 1
    return 0
