"""Integra o extrator automático aos modelos treinados."""
from api.agrupamento import gerar_features_clusters
from api.classificacao import classificar_features
from api.erros import Indisponivel
from api.extracao import ExtratorSMS
from api.modelos import ModelosSMS, PASTA_MODELOS
from api.preparacao import preparar_mensagem


class ServicoSMS:
    def __init__(self, pasta_modelos=PASTA_MODELOS):
        self.modelos = ModelosSMS(pasta_modelos)
        self.extrator = ExtratorSMS()
        self.erro_gramatica = None

    def carregar(self):
        self.modelos.carregar()
        try:
            self.extrator.extrair("Esta mensagem está correta.")
        except Indisponivel as exc:
            self.erro_gramatica = str(exc)

    def status(self):
        m = self.modelos
        return {"api": "ok", "versao": "v1", "kmeans_carregado": m.kmeans is not None,
                "gramatica_verificada": self.extrator.gramatica_verificada,
                "xgboost_carregado": m.modelo is not None,
                "classificacao_disponivel": m.modelo is not None and self.extrator.gramatica_verificada,
                "pendencias": [x for x in [m.erro_clusters, m.erro_classificacao, self.erro_gramatica] if x]}

    def extrair(self, mensagem):
        mensagem = preparar_mensagem(mensagem)
        if self.modelos.kmeans is None:
            raise Indisponivel(self.modelos.erro_clusters or "K-means indisponível.")
        try:
            features = self.extrator.extrair(mensagem)
            self.erro_gramatica = None
        except Indisponivel as exc:
            self.erro_gramatica = str(exc)
            raise
        # O treinamento usa carga emocional ordinal; preservar 0/1/2 na inferência.
        carga = features["carga_emocional"]
        features["carga_emocional"] = {"baixa": 0, "media": 1, "média": 1, "alta": 2}[carga]
        cluster, indicadores = gerar_features_clusters(mensagem, self.modelos.kmeans)
        binarias = {k: v for k, v in features.items() if k != "carga_emocional"}
        binarias.update({f"carga_emocional_{n}": int(carga == n or (n == "media" and carga == "média")) for n in ["baixa", "media", "alta"]})
        return {"versao": "v1", "features": features, "features_binarias": binarias,
                "features_clusters": indicadores, "cluster_identificado": cluster,
                "features_completas": {**features, **indicadores},
                "classificacao_disponivel": self.modelos.modelo is not None}

    def classificar(self, mensagem):
        if self.modelos.modelo is None:
            raise Indisponivel(self.modelos.erro_classificacao or "Modelo indisponível.")
        mensagem = preparar_mensagem(mensagem)
        resultado = self.extrair(mensagem)
        decisao = classificar_features(mensagem, resultado["features_completas"], self.modelos)
        return {**resultado, **decisao,
                "sinais_detectados": [k for k, v in resultado["features"].items() if v > 0]}

    def fechar(self):
        self.extrator.fechar()
