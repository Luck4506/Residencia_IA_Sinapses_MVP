"""Embedding + 22 atributos + seis clusters, na ordem exata do treinamento."""
import re
import numpy as np
from xgboost import DMatrix
from api.erros import Indisponivel
from api.explicacao import explicar_sinais


def classificar_features(mensagem, features, modelos):
    texto = re.sub(r"\s+", " ", mensagem.lower()).strip()
    embedding = modelos.embedding.encode([texto], show_progress_bar=False)[0] # embbedding 
    nomes = modelos.config["nomes_atributos"]
    valores = [features[n] for n in nomes]
    clusters = [features[n] for n in modelos.config["nomes_features_clusters"]]
    vetor = np.concatenate([embedding, valores, clusters]).astype(np.float32).reshape(1, -1)
    score = float(modelos.modelo.predict_proba(vetor)[0, 1])
    if not np.isfinite(score) or not 0 <= score <= 1:
        raise Indisponivel("Pontuação inválida retornada pelo modelo.")
    # TreeSHAP local: ordena somente atributos detectados que aumentaram o risco.
    contribuicoes = modelos.modelo.get_booster().predict(DMatrix(vetor), pred_contribs=True)[0]
    importantes = sorted([
        {"feature": nome, "valor": features[nome], "contribuicao": float(contribuicoes[len(embedding) + i])}
        for i, nome in enumerate(nomes)
        if features[nome] > 0 and contribuicoes[len(embedding) + i] > 0
    ], key=lambda item: item["contribuicao"], reverse=True)[:5]
    limiar = modelos.config["threshold"]
    return {"score_golpe": score, "probabilidade_percentual": round(score * 100, 2),
            "limiar": limiar, "classe": int(score >= limiar), "features_importantes": importantes,
            "explicacao_sinais": explicar_sinais(importantes)}
