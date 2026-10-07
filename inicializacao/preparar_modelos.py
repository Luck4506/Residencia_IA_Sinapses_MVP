"""Baixa apenas o encoder exigido pelo XGBoost; nenhum modelo é retreinado."""
import json
import os
from pathlib import Path

PASTA = Path(__file__).resolve().parents[1] / 'backend' / 'modelos' / 'v1'
os.environ.setdefault('HF_HOME', str(PASTA.parent / '.cache_huggingface'))
from sentence_transformers import SentenceTransformer

if __name__ == '__main__':
    config = json.loads((PASTA / 'xgboost_config.json').read_text())
    destino = PASTA / 'embedding'
    if not (destino / 'modules.json').exists():
        modelo = SentenceTransformer(config['modelo_embedding'], device='cpu')
        modelo.save(str(destino))
    print(f'Encoder disponível em {destino}')
