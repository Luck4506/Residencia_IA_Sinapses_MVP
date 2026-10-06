# FINALIDADE: Correção local com cache verificável e filtros explícitos de linguagem SMS.
# EXECUÇÃO: É importado e chamado pelo fluxo da API; não precisa ser iniciado manualmente.
"""Correção local com cache verificável e filtros explícitos de linguagem SMS."""
import hashlib, json, re
from pathlib import Path
from importlib.metadata import version
from extrator_features.apoio_02_regras import normalizar
from extrator_features.bibliotecas.apoio_03_gramatica import Corretor
INFORMAIS = frozenset('vc vcs pq q tb tbm blz obg obgd hj msg msgs zap rs kkk ta ne to pra pro oq pfv vlw aff mano bora'.split())
def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def filtrar_erros(erros):
    """Separa alertas aceitos/ignorados sem alterar mensagem nem sugestões.

    Whitelist fixa de linguagem informal; ignora correções exclusivamente de
    acento/caixa. Demais falsos positivos (nomes, marcas) ficam auditáveis.
    Os filtros não foram ajustados para reproduzir os rótulos do CSV.
    """
    aceitos, ignorados = [], []
    for erro in erros:
        palavra = normalizar(erro['trecho'])
        tokens = set(re.findall(r'\b[a-z]+\b', palavra))
        motivo = None
        if tokens & INFORMAIS:
            motivo = 'abreviacao_ou_giria_da_lista_fixa'
        elif erro['tipo'] == 'ortografia' and any(
                normalizar(s) == palavra for s in erro.get('sugestoes', [])):
            motivo = 'apenas_acento_ou_caixa'
        if motivo:
            ignorados.append({**erro, 'motivo': motivo})
        else:
            aceitos.append(erro)
    return {'aceitos': aceitos, 'ignorados': ignorados}

def gramatica_lote(textos, pasta_cache):
    """Executa LanguageTool LOCAL 6.8; cache bruto por texto/versões/código.

    Falha de ferramenta interrompe: nunca equivale a zero erros. Filtros são
    reaplicados sobre os alertas brutos em cada execução do notebook.
    """
    pasta_cache = Path(pasta_cache)
    pasta_cache.mkdir(exist_ok=True, parents=True)
    contexto = json.dumps({'lt': '6.8', 'cliente': version('language-tool-python'),
        'wrapper': sha256(Path(__file__).parent / 'bibliotecas/apoio_03_gramatica.py'),
        'urls': sha256(Path(__file__).parent / 'bibliotecas/apoio_02_urls.py')}, sort_keys=True)
    resultados = []
    corretor = Corretor('6.8')
    try:
        for i, texto in enumerate(textos):
            digest = hashlib.sha256((contexto + '\n' + texto).encode()).hexdigest()
            caminho = pasta_cache / (digest + '.json')
            if caminho.exists():
                dados = json.loads(caminho.read_text())
                if dados['contexto'] != contexto or dados['texto_sha256'] != hashlib.sha256(texto.encode()).hexdigest():
                    raise ValueError('Cache incompatível: ' + str(caminho))
                bruto = dados['erros']
            else:
                bruto = corretor.detectar_erros(texto)
                dados = {'contexto': contexto, 'texto_sha256': hashlib.sha256(texto.encode()).hexdigest(), 'erros': bruto}
                temporario = caminho.with_suffix('.tmp')
                temporario.write_text(json.dumps(dados, ensure_ascii=False, indent=2))
                temporario.replace(caminho)
            resultados.append(filtrar_erros(bruto))
            if (i + 1) % 250 == 0:
                print(f'LanguageTool: {i + 1}/{len(textos)} mensagens processadas.')
    finally:
        corretor.close()
    return resultados