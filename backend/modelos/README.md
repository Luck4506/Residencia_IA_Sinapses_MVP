# Modelos ativos

`v1/` contém os artefatos entregues em `modelo treinado/models`, copiados sem alteração: XGBoost, configurações, vocabulário/IDF e centroides K-means. O encoder exigido pelo XGBoost fica em `v1/embedding/` e é preparado por `inicializacao/preparar_modelos.py`.

A entrada tem 412 valores: 384 do texto, 22 atributos e seis clusters. Não é necessário treinar novamente. Consulte o README da raiz para instalação, execução e contrato da API.
