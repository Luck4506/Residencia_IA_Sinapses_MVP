# Sinápses MVP

Aplicação Flutter integrada à API Python e aos modelos treinados entregues. A análise usa o texto recebido, o extrator automático de 22 atributos, TF-IDF/K-means e XGBoost. Não há porcentagens demonstrativas nem treinamento durante a execução.

## Iniciar neste computador

- **Navegador:** abra `Iniciar Web.command` e acesse http://localhost:8080.
- **iPhone virtual:** abra `Iniciar iPhone.command`.
- Os atalhos iniciam API e interface juntos. Encerre com Ctrl+C no terminal.
- O atalho escolhe uma porta livre entre 8000 e 8010 para a API. Para fixar uma porta, use `API_PORT=8001 bash inicializacao/iniciar.sh web` (ou `iphone`).

## Preparar em outro computador

Pré-requisitos: Python 3.12, Java 17 ou superior e Flutter compatível com Dart 3.13.2. Para iPhone, macOS e Xcode com simulador instalado. No macOS, XGBoost também requer a biblioteca OpenMP (`brew install libomp`, se ainda não estiver instalada).

Na raiz deste projeto:

```sh
bash inicializacao/preparar.sh
bash inicializacao/iniciar.sh web
```

A preparação instala as dependências, baixa o encoder `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` exigido pelo treinamento e prepara o LanguageTool 6.8. Esses componentes ficam dentro de `backend/`; a primeira preparação exige internet. A inferência com os componentes locais não envia mensagens a serviços externos.

O ambiente `.venv`, o encoder (~470 MB), o LanguageTool e caches ficam fora do Git. Os seis artefatos treinados pequenos estão em `backend/modelos/v1/` e devem acompanhar o código. O script de preparação recria as dependências grandes após clonar. A pasta original `modelo treinado/` e o ZIP foram preservados para consulta; a aplicação não depende deles.

## Organização

- `frontend/`: aplicativo Flutter, assets e projetos de plataforma; inclui a extensão de compartilhamento do iPhone.
- `backend/api/main.py`: entrada FastAPI; `/saude`, `/extrair` e `/analisar`.
- `backend/api/servico.py`: integra extração, agrupamento e inferência.
- `backend/extrator_features/`: regras de extração e LanguageTool local.
- `backend/modelos/v1/`: artefatos efetivamente usados na inferência.
- `inicializacao/`: preparação e inicialização.

Os módulos da API têm nomes importáveis normais. Execute a partir de `backend` com `.venv/bin/python -m uvicorn api.main:app`, ou prefira os atalhos.

## Contrato do modelo e alterações

Entrada do XGBoost: **384 dimensões de embedding + 22 atributos + 6 clusters = 412 valores**, na ordem de `xgboost_config.json`. Limiar entregue: **0,55**. A normalização textual, TF-IDF, distância aos centroides e codificação emocional seguem a rotina original de predição. Mensagens sem termos no vocabulário seguem a atribuição ao centro mais próximo do vetor zero, como no código entregue.

- `solicita_ligacao` foi removida da extração e das respostas.
- `solicita_dados_cadastro = solicita_dados_pessoais OU solicita_atualizacao_cadastro`. As duas regras originais são reutilizadas internamente.
- `carga_emocional` continua ordinal: baixa = 0, média = 1, alta = 2. Não foi convertida à força em binária na entrada do modelo.
- A resposta inclui `score_golpe` (0–1), `probabilidade_percentual` (0–100), `classe`, `limiar`, `features_importantes`, `explicacao_sinais`, `sinais_detectados`, `features`, `features_binarias`, `features_clusters` e `features_completas`.
- `features_importantes` contém até cinco atributos detectados que contribuíram positivamente para o risco nesta mensagem, ordenados por TreeSHAP. As contribuições são em margem do modelo, não porcentagens; não representam toda a explicação, pois texto e clusters também influenciam.
- `features` conserva os valores exatos dos 22 atributos. `features_completas` adiciona os seis clusters. `features_binarias` mostra as 21 features binárias e três indicadores para as categorias emocionais.

A interface apresenta o logo PUC-Campinas de 85 anos e um parágrafo curto (`explicacao_sinais`) que descreve os sinais destacados e sua importância. O texto é montado a partir de descrições fixas das features detectadas, sem gerar novos achados.

## Diagnóstico na interface

A caixa **Diagnóstico: todas as features** inicia fechada, pode ser expandida e recolhida, e mostra todos os indicadores 0/1, incluindo os seis clusters. Existe no Flutter e na extensão do iPhone.

Para ocultar completamente a caixa na versão destinada ao usuário final:

```sh
SHOW_DIAGNOSTICS=false bash inicializacao/iniciar.sh web
# ou: SHOW_DIAGNOSTICS=false bash inicializacao/iniciar.sh iphone
```

Ao executar/compilar o Flutter diretamente, use `--dart-define=SHOW_DIAGNOSTICS=false`. A API continua retornando os dados para inspeção. A extensão do iPhone recebe a mesma configuração de compilação do Flutter.

## Rede

O padrão atende navegador e simulador de iPhone em `127.0.0.1:8000`; o emulador Android usa `10.0.2.2:8000` quando o Flutter é iniciado diretamente. Para celular físico, inicie a API com `API_HOST=0.0.0.0` e informe `--dart-define=API_URL=http://IP_DO_COMPUTADOR:8000` ao Flutter. Ambos devem estar na mesma rede. As permissões HTTP local estão habilitadas para este MVP.

CORS permite origens locais de navegador. Para outra origem, configure `CORS_ORIGINS` com a lista separada por vírgulas. `PASTA_MODELOS` permite escolher outra pasta de artefatos compatível.

## Verificação

```sh
cd backend
.venv/bin/python -m pip install -r requirements-dev.txt
PYTHONPATH=. .venv/bin/python -m pytest tests/test_01_fluxo.py -q
cd ../frontend
flutter test
```

Os testes cobrem união cadastral, remoção das features antigas, validação de texto, modelo real, codificação binária, CORS, tratamento de falhas de conexão e expansão/recolhimento do diagnóstico.

No OneDrive, os scripts de iPhone colocam os arquivos de compilação em uma pasta temporária para evitar falhas de assinatura por metadados de sincronização. O código-fonte continua neste diretório.

O feedback de polegar é apenas local na tela; não há armazenamento ou retreinamento automático. A porcentagem é a saída do classificador entregue, não uma garantia de que a mensagem seja ou não golpe.
