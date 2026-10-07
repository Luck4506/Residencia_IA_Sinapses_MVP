"""Carrega os artefatos entregues, sem retreinar nem alterar suas entradas."""
import json
import logging
import os
from pathlib import Path
import numpy as np
import torch
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
from xgboost import XGBClassifier
from extrator_features.etapa_01_classificador import NOMES

PASTA_MODELOS = Path(os.getenv("PASTA_MODELOS", str(Path(__file__).resolve().parents[1] / "modelos" / "v1")))

class ModelosSMS:
    def __init__(self, pasta=PASTA_MODELOS):
        self.pasta = Path(pasta)
        self.modelo = self.kmeans = self.embedding = None
        self.config = {}
        self.erro_clusters = self.erro_classificacao = None

    def carregar(self):
        try:
            # Inferência unitária: evita contenção entre os pools do PyTorch e XGBoost.
            torch.set_num_threads(1)
            self.config = json.loads((self.pasta / "xgboost_config.json").read_text())
            c = self.config
            if set(c["nomes_atributos"]) != set(NOMES) or len(c["nomes_atributos"]) != len(NOMES):
                raise ValueError("Features do extrator diferem do treinamento.")
            if c["nomes_features_clusters"] != [f"cluster_{i}" for i in range(6)]:
                raise ValueError("Esperados seis clusters.")
            if not 0 < c["threshold"] < 1:
                raise ValueError("Limiar inválido.")
            vocab = json.loads((self.pasta / "tfidf_vocabulario.json").read_text())
            idf = np.load(self.pasta / "tfidf_idf.npy", allow_pickle=False)
            with np.load(self.pasta / "kmeans_tfidf.npz", allow_pickle=False) as dados:
                centros = dados["centros_clusters"]
            if centros.shape != (6, len(vocab)) or idf.shape != (len(vocab),):
                raise ValueError("Dimensões incompatíveis nos artefatos TF-IDF/K-means.")
            self.kmeans = {"contador": CountVectorizer(vocabulary=vocab), "idf": idf, "centros": centros}
            modelo = XGBClassifier(n_jobs=1)
            modelo.load_model(self.pasta / "xgboost_embeddings_final.json")
            local = self.pasta / "embedding"
            self.embedding = SentenceTransformer(str(local) if local.exists() else c["modelo_embedding"], device="cpu")
            dim = self.embedding.get_embedding_dimension()
            esperado = [f"embedding_{i}" for i in range(dim)] + c["nomes_atributos"] + c["nomes_features_clusters"]
            if c["nomes_features"] != esperado or modelo.n_features_in_ != len(esperado):
                raise ValueError("Ordem ou dimensão das entradas difere do modelo treinado.")
            self.modelo = modelo
        except Exception as exc:
            logging.getLogger(__name__).exception("Falha ao carregar modelos")
            self.erro_classificacao = f"Modelo indisponível: {exc}"
            if self.kmeans is None:
                self.erro_clusters = "Artefatos de agrupamento indisponíveis."
