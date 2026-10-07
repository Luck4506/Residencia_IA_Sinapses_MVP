"""Reproduz o TF-IDF e a distância aos centroides da predição entregue."""
import numpy as np
from sklearn.preprocessing import normalize


def gerar_features_clusters(mensagem, componentes):
    contagem = componentes["contador"].transform([mensagem])
    vetor = normalize(contagem.multiply(componentes["idf"]), norm="l2").toarray()[0]
    cluster = int(np.argmin(np.linalg.norm(componentes["centros"] - vetor, axis=1)))
    return cluster, {f"cluster_{i}": int(i == cluster) for i in range(6)}
