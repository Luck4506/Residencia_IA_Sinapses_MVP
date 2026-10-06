# Protótipo — análise de SMS

Os códigos estão comentados no topo com sua finalidade e seu papel no programa. Apenas os scripts Python são numerados, incluindo os do extrator de features; as pastas têm nomes simples. A numeração organiza a leitura: a inicialização acontece uma vez; o processamento repete por mensagem. Módulos `apoio_*` podem ser chamados em várias etapas. As features numeradas são atributos, não 24 fases independentes de uma análise.

## Estrutura

```text
PROTÓTIPO_FINAL/
├── Iniciar iPhone.command                  # Atalho opcional do Finder
├── inicializacao/
│   ├── iniciar_iphone.sh                   # Abre simulador e executa Flutter
│   ├── 02_selecionar_iphone.py             # Auxiliar: escolhe o iPhone
│   └── iniciar_api.sh                      # Inicia a API separadamente
├── frontend/
│   ├── lib/main.dart                       # Entrada e telas Flutter
│   ├── ios/                                # Projeto iPhone e ShareExtension
│   └── assets/                             # Recursos visuais
├── backend/
│   ├── api/
│   │   ├── 01_main.py                # Rotas e resposta JSON
│   │   ├── 02_modelos.py             # Carregamento dos modelos
│   │   ├── 03_preparacao.py          # Validação do SMS
│   │   ├── 04_servico.py             # Coordenação do processamento
│   │   ├── 05_extracao.py            # 24 features + corretor local
│   │   ├── 06_agrupamento.py         # TF-IDF → K-means → 6 indicadores
│   │   ├── 07_classificacao.py       # Codificação → XGBoost → decisão
│   │   └── 0_erros.py               # Indisponibilidade das etapas
│   ├── modelos/v1/                         # Arquivos treinados e configuração
│   ├── extrator_features/
│   │   ├── etapa_01_classificador.py       # Motor das 24 regras existentes
│   │   ├── features/                       # feature_01_* até feature_24_*
│   │   ├── bibliotecas/                    # URL, telefone, PIX, texto e Java
│   │   └── apoio_*.py                      # Gramática e regras compartilhadas
│   └── tests/                              # Verificação, fora das requisições
├── README.md
└── MAPA_ARQUIVOS.json                      # Nomes anteriores → novos
```

Os arquivos da API atualmente usam nomes como `01_main.py`. Como esses nomes começam com números, não podem ser usados diretamente em instruções comuns como `from api.04_servico import ...`. É necessário compatibilizar o carregamento dos módulos ou adotar nomes válidos para imports comuns. Nomes convencionais, como `__init__.py` e `lib/main.dart`, foram preservados.

> **Estado encontrado nesta revisão:** `backend/api/01_main.py` contém apenas os comentários de cabeçalho. Os outros módulos ainda têm imports com os nomes anteriores (`api.etapa_*` e `api.apoio_00_erros`), e o lançador ainda aponta para `api.etapa_01_main:app`. Portanto, a API não está executável nessa organização atual. O fluxo e o contrato HTTP abaixo documentam o comportamento esperado com base na implementação lida antes dessas alterações. É preciso restaurar o ponto de entrada e compatibilizar os imports e o lançador antes de executar. Esta atualização altera somente a documentação, preservando as alterações em andamento no código.


## 1. Inicialização

**Aplicativo:** `Iniciar iPhone.command` chama `inicializacao/iniciar_iphone.sh`, que consulta `02_selecionar_iphone.py`, abre o simulador e executa `flutter run`. O Flutter começa em `frontend/lib/main.dart`.

**API, separadamente:** `inicializacao/iniciar_api.sh` executa Uvicorn com `api.01_main:app`. No início, `01_main.py` cria `ServicoSMS`, que chama `02_modelos.py` para carregar e conferir os artefatos de `modelos/v1/` uma vez por processo. Não há treinamento durante as requisições.

O LanguageTool local é inicializado quando necessário na primeira extração. Não é preciso abrir um terminal para cada arquivo Python.

## 2. Fluxo de cada mensagem

```text
Flutter — lib/main.dart
    ↓ POST /analisar (conexão ainda pendente)
01_main.py — recebe o JSON
    ↓
03_preparacao.py — valida texto e tamanho
    ↓
04_servico.py — coordena a análise
    ├─ 05_extracao.py
    │    └─ extrator_features/etapa_01_classificador.py
    │         └─ features/ → 24 atributos
    └─ 06_agrupamento.py
         └─ texto → TF-IDF → normalização L2 → K-means
              └─ one-hot → 6 indicadores de cluster
    ↓
04_servico.py — combina 24 + 6 atributos
    ↓
07_classificacao.py — preprocessador → XGBoost → limiar
    ↓
04_servico.py — monta resultado e sinais detectados
    ↓
01_main.py — devolve JSON pela API
    ↓
Flutter — apresenta o resultado (conexão ainda pendente)
```

São dois caminhos complementares, executados em sequência pela implementação: as 24 regras e o agrupamento textual. O K-means recebe o TF-IDF do texto, não as 24 features. A combinação tem 30 atributos antes da codificação de `carga_emocional`.

`03_preparacao.py` não limpa um dataset. Preserva o texto original para não apagar URLs, números e erros de escrita. As normalizações específicas ficam nas regras. As colunas e os valores do extrator mantêm seus nomes originais apesar da numeração dos arquivos.

**Fluxo implementado antes da alteração dos nomes e do ponto de entrada:** o frontend ainda mostra 78% ilustrativos e não chama a API. `POST /extrair` realiza o fluxo até a combinação dos 30 atributos. `POST /analisar` valida a entrada e retorna **503 antes de extrair**, porque falta o XGBoost compatível. O diagrama completo mostra o caminho preparado para quando esse modelo e a integração estiverem disponíveis.

### 2.1. O que acontece ao iniciar e encerrar a API

1. O Uvicorn importa `api.01_main:app`. Isso cria a aplicação FastAPI e registra as rotas.
2. No fluxo esperado, no início do servidor, o ciclo de vida (`lifespan`) cria uma instância de `ServicoSMS`.
3. O serviço cria `ModelosSMS` e `ExtratorSMS`. O extrator prepara um objeto de acesso ao corretor; o servidor Java do LanguageTool é iniciado sob demanda, quando uma extração precisar dele.
4. `ServicoSMS.carregar()` chama `ModelosSMS.carregar()`, que lê a configuração e os artefatos de `backend/modelos/v1/`.
5. O serviço fica em `app.state.servico` e é reutilizado pelas rotas. Cada mensagem usa os objetos já carregados. Com vários processos, cada processo tem suas próprias instâncias.
6. Ao encerrar a API, `ServicoSMS.fechar()` chama `ExtratorSMS.fechar()`, liberando o corretor local.

Os arquivos numerados são módulos importados entre si. Você inicia apenas o servidor da API e o aplicativo; não executa os sete arquivos da API manualmente. O arquivo de modelos, por exemplo, atua na inicialização e não entre cada recebimento e validação de SMS.

### 2.2. Caminho de POST /extrair após restaurar a inicialização

Esta rota permite verificar a parte já disponível do processamento:

1. O cliente envia um JSON com o campo `mensagem`.
2. `PedidoAnalise`, definido em `01_main.py`, valida o corpo e chama `preparar_mensagem()`.
3. A rota chama `ServicoSMS.extrair()`. O serviço valida novamente o texto para também proteger chamadas diretas feitas por outros códigos Python.
4. O serviço verifica se o conjunto TF-IDF/K-means foi carregado. Sem ele, interrompe com erro de indisponibilidade.
5. `ExtratorSMS.extrair()` obtém os resultados gramaticais locais, filtra os erros e chama o extrator de regras. Retorna as 24 features.
6. `gerar_features_clusters()` recebe o texto original e os componentes treinados. Transforma o texto com TF-IDF, normaliza o vetor, identifica um cluster e gera seus seis indicadores.
7. O serviço combina os dois dicionários e confere se existem 30 atributos.
8. A rota devolve o dicionário como JSON, com HTTP 200 quando o processamento termina com sucesso.

As etapas 5 e 6 são sequenciais no código atual, embora representem dois caminhos complementares no desenho do projeto.

A resposta contém:

| Campo | Conteúdo |
| --- | --- |
| `versao` | Versão informada pela configuração dos modelos. |
| `etapa` | Valor `extracao_e_agrupamento`. |
| `features` | As 24 features extraídas por regras. |
| `features_clusters` | Os seis indicadores `cluster_0` a `cluster_5`. |
| `cluster_identificado` | Número do cluster atribuído à mensagem. |
| `features_completas` | União das 24 features e dos seis indicadores. |
| `classificacao_disponivel` | Indica se o XGBoost foi carregado. Não é uma decisão sobre a mensagem. |

### 2.3. Caminho de POST /analisar

A rota recebe o mesmo formato de entrada de `/extrair`, mas chama `ServicoSMS.classificar()`.

**Com o ponto de entrada restaurado, mas ainda sem o XGBoost final:** após validar o corpo da requisição, o serviço verifica se existe um XGBoost carregado. Como o classificador final está ausente e a configuração possui `classificacao_habilitada: false`, a resposta é HTTP 503. Nesse caso, não executa a extração nem o agrupamento.

**Com os artefatos compatíveis carregados:** o serviço executa o fluxo de extração descrito acima, passa `features_completas` para `classificar_features()` e monta a resposta final. O classificador ordena as colunas, aplica o preprocessador já ajustado, consulta o XGBoost e compara a pontuação com o limiar configurado.

A resposta de sucesso prevista pelo código contém:

| Campo | Conteúdo |
| --- | --- |
| `versao` | Versão do conjunto de modelos utilizado. |
| `score_golpe` | Saída de `predict_proba` para a classe 1, entre 0 e 1. A calibração dessa pontuação precisa ser avaliada no treinamento. |
| `limiar` | Valor configurado para transformar a pontuação em decisão. |
| `classe` | `1` quando `score_golpe >= limiar`; `0` quando abaixo. Classe 1 representa possível golpe; classe 0 não certifica segurança. |
| `cluster_identificado` | Cluster atribuído durante a extração. |
| `sinais_detectados` | Nomes das features estruturadas cujo valor é 1. |

Os sinais são regras ativadas pelo extrator. Não são uma explicação das contribuições do XGBoost, e a categoria textual `carga_emocional` não entra nessa lista de valores iguais a 1.

**Quem devolve o valor ao frontend?** `07_classificacao.py` calcula a pontuação; `04_servico.py` monta o resultado; a rota de `01_main.py`, por meio do FastAPI, envia a resposta HTTP em JSON. O aplicativo ainda precisa implementar o envio da mensagem, a leitura dessa resposta e a atualização da tela.

### 2.4. Responsabilidade de cada arquivo de backend/api

#### 01_main.py — entrada HTTP e ciclo de vida

Deve ser o ponto de entrada utilizado pelo Uvicorn e definir `PedidoAnalise`, `criar_app()` e a instância `app`. Atualmente contém apenas comentários; as responsabilidades abaixo descrevem o que precisa voltar a implementar.

- `PedidoAnalise` exige `mensagem` como texto de 1 a 5.000 caracteres e aplica a validação de preparação.
- `criar_app()` registra as rotas, configura o ciclo de vida do serviço e permite fornecer uma fábrica de serviço para os testes.
- `GET /saude` consulta `ServicoSMS.status()`.
- `POST /extrair` chama `ServicoSMS.extrair()`.
- `POST /analisar` chama `ServicoSMS.classificar()`.
- A função interna `executar()` converte `Indisponivel` em HTTP 503 e `ValueError` em HTTP 422. Erros de validação do corpo também são tratados pelo FastAPI/Pydantic como 422. Outros erros inesperados não são convertidos por essa função.
- Se `CORS_ORIGINS` estiver definida, configura as origens permitidas para clientes sujeitos às regras de CORS, como navegadores.

**Recebe:** requisições HTTP. **Entrega:** respostas JSON e códigos HTTP. Deve concentrar o contrato de comunicação; os cálculos de features e modelos ficam nos outros módulos.

#### 02_modelos.py — carregamento dos artefatos treinados

Define `PASTA_MODELOS`, `ModelosSMS`, `carregar_joblib()` e `conferir_hash()`.

- Localiza o conjunto ativo em `backend/modelos/v1/` e lê `configuracao.json`.
- Confere o SHA-256 de `componentes_kmeans.joblib`, carrega o conjunto e verifica a quantidade de clusters e os nomes dos seis indicadores.
- Trata avisos de incompatibilidade de versão do scikit-learn como falhas de carregamento.
- Quando `classificacao_habilitada` é verdadeira, tenta carregar `preprocessador_xgb.joblib` e `xgboost.ubj`.
- Confere as 30 colunas esperadas, o limiar entre 0 e 1, a classe positiva, os hashes do classificador, a ordem de entrada do preprocessador e as classes do XGBoost.
- Transforma uma linha de exemplo para conferir se a dimensão produzida pelo preprocessador corresponde à entrada do XGBoost.
- Registra falhas no log e guarda mensagens de indisponibilidade que o serviço pode comunicar. Assim, a API pode permanecer acessível para informar pendências.

**Recebe:** diretório de modelos e configuração. **Entrega:** objetos carregados em memória e informações sobre falhas. Não treina nem atualiza os modelos durante uma análise. A verificação estrutural não substitui a avaliação de qualidade do modelo.

#### 03_preparacao.py — validação da mensagem

Contém `preparar_mensagem(texto)`.

- Verifica se o valor é texto.
- Rejeita mensagem vazia ou composta apenas de espaços.
- Rejeita texto com mais de 5.000 caracteres.
- Devolve a mensagem original, preservando espaços, caixa, acentos, pontuação, URLs, números e erros de escrita.

**Recebe:** texto de uma mensagem. **Entrega:** o mesmo texto validado ou `ValueError`. A função usa `strip()` para conferir se há conteúdo, mas não devolve uma versão com espaços removidos. Limpeza de datasets e preparação de treinamento ficam fora deste fluxo de inferência.

#### 04_servico.py — coordenação das etapas

Contém a classe `ServicoSMS`, que conecta os módulos sem depender dos detalhes HTTP.

| Método | Responsabilidade |
| --- | --- |
| `__init__()` | Cria o gerenciador de modelos e o extrator. |
| `carregar()` | Solicita o carregamento dos artefatos. |
| `status()` | Informa versão, componentes carregados, estado da verificação gramatical e pendências. |
| `extrair()` | Valida a mensagem, confere K-means, chama extração e agrupamento, combina os 30 atributos e monta a resposta de extração. |
| `classificar()` | Confere a existência do XGBoost, chama `extrair()`, aciona a classificação e monta a resposta final com os sinais. |
| `fechar()` | Solicita o encerramento do corretor local. |

**Recebe:** mensagem validável. **Entrega:** dicionário de extração, classificação ou estado do serviço. A transformação em clusters ocorre em `06_agrupamento.py`; o serviço apenas chama essa função e combina suas saídas.

#### 05_extracao.py — ligação com o extrator de features

Contém a classe `ExtratorSMS`.

- Prepara o acesso ao corretor local LanguageTool 6.8.
- Usa um bloqueio (`Lock`) para serializar o acesso à extração nessa instância.
- Em `extrair()`, consulta os erros gramaticais e aplica `filtrar_erros()`.
- Atualiza `gramatica_verificada` conforme o sucesso ou a falha dessa consulta. O estado começa como falso e não representa uma checagem antecipada feita por `/saude`.
- Chama `extrator_features/etapa_01_classificador.py`, passando o texto e o resultado gramatical. O motor utiliza os arquivos `feature_01_*` a `feature_24_*` da pasta `features/`.
- Devolve apenas o campo `features` produzido pelo motor. Os detalhes de evidência que o extrator também calcula não são expostos por este adaptador.
- Se a consulta gramatical falhar, lança `Indisponivel`; não transforma a falha em ausência de erros de escrita.
- `fechar()` libera o corretor local.

**Recebe:** texto. **Entrega:** dicionário com 24 atributos, incluindo a categoria `carga_emocional`. A API fornece a gramática diretamente ao motor, evitando o caminho de cache usado pela análise em lote. Apesar do nome `classificador.py` no extrator, esse motor aplica regras de features; a classificação de possível golpe pertence ao XGBoost.

#### 06_agrupamento.py — texto para cluster e indicadores

Contém `gerar_features_clusters(mensagem, componentes)`.

1. Usa `vetorizador_tfidf.transform([mensagem])` com o vocabulário já aprendido.
2. Se o vetor não contiver nenhum termo reconhecido, lança `ValueError`, que a rota converte em 422.
3. Aplica normalização L2 ao vetor.
4. Usa `modelo_kmeans.predict()` para atribuir um dos seis clusters.
5. Usa o codificador carregado para transformar esse número em seis indicadores one-hot.
6. Confere se existem seis indicadores e se a soma é 1.
7. Retorna o número do cluster e o dicionário de indicadores.

Exemplo **apenas ilustrativo** de codificação, supondo cluster 2:

```json
{"cluster_0": 0, "cluster_1": 0, "cluster_2": 1, "cluster_3": 0, "cluster_4": 0, "cluster_5": 0}
```

**Recebe:** texto e componentes treinados. **Entrega:** `(cluster, indicadores)`. O K-means usa features textuais do TF-IDF; não recebe as 24 features de regras neste projeto. O cluster representa um agrupamento textual e não determina, sozinho, se existe golpe. São seis indicadores adicionais, sem descarte de uma categoria.

#### 07_classificacao.py — pontuação e decisão

Contém `classificar_features(features, modelos)`.

1. Monta um DataFrame de uma linha, respeitando a ordem de `configuracao.json["colunas_entrada"]`.
2. Aplica `preprocessador.transform()` aos 30 atributos combinados. O preprocessador deve reproduzir a codificação aprendida no treinamento, inclusive da feature categórica.
3. Chama `modelo.predict_proba()` e obtém a pontuação da classe 1.
4. Confere se a pontuação é finita e está entre 0 e 1; caso contrário, lança `Indisponivel`.
5. Aplica o limiar configurado e devolve `score_golpe`, `limiar` e `classe`.

**Recebe:** os 30 atributos e os objetos carregados. **Entrega:** pontuação e decisão. A quantidade de colunas após codificação pode diferir de 30 e deve corresponder ao modelo treinado. Esse módulo não monta a lista de sinais nem envia a resposta HTTP. Atualmente, a rota não chega a esta etapa porque falta o classificador final.

#### 0_erros.py — erro compartilhado

Define `Indisponivel`, uma exceção derivada de `RuntimeError`. Os módulos a utilizam quando um componente necessário não pode realizar o processamento. `01_main.py` converte essa exceção em HTTP 503 com uma mensagem no campo `detail`. O número no nome organiza o arquivo de apoio; ele não representa uma fase anterior ao recebimento da mensagem.

#### __init__.py — identificação do pacote

Identifica `api/` como pacote Python e contém sua descrição. Permite a organização dos imports usados pelo projeto. Não inicia o servidor, não carrega modelos por conta própria e não precisa ser executado manualmente.

### 2.5. Estado dos componentes e interpretação do status

| Parte | Situação |
| --- | --- |
| Interface Flutter e simulador | Executáveis; resultado exibido ainda ilustrativo. |
| Entrada da API e imports | Incompletos após alterações recentes; requerem restauração e compatibilização. A função de validação permanece em `03_preparacao.py`. |
| Extração de 24 features | Implementada, com LanguageTool local. |
| TF-IDF, K-means e seis indicadores | Implementados com componentes exportados. |
| Combinação de 30 atributos | Implementada em `/extrair`. |
| Código para inferência XGBoost | Implementado, aguardando os artefatos finais compatíveis. |
| Flutter enviando e exibindo a resposta real | Integração pendente. |

`GET /saude` informa o estado conhecido pelo serviço. `api: "ok"` significa que a API respondeu, e não que toda a análise está pronta. `classificacao_disponivel` reflete o carregamento do XGBoost; ainda pode haver falha em uma extração posterior, por exemplo no LanguageTool. Consulte também os demais campos e trate os erros das próprias requisições.

## 3. Executar com flutter run

Abra um simulador de iPhone pelo Xcode/DeviceHub. Com o terminal na pasta principal:

```bash
cd frontend
flutter pub get
flutter run
```

Escolha o iPhone se aparecer uma lista. Para indicar o simulador usado nas verificações deste Mac:

```bash
flutter run -d FAE62F0A-431A-4AA0-B1F3-6C522BAC1736
```

Requisitos: Flutter no PATH, Xcode configurado e simulador iOS instalado. O frontend demonstrativo não exige iniciar a API. O terminal fica aberto; `r` faz hot reload, `d` desconecta mantendo o aplicativo aberto e `q` encerra a execução.

O projeto está no OneDrive. O lançador prepara um link para os artefatos iOS numa pasta temporária fora da sincronização, evitando problemas de assinatura. Se essa pasta tiver sido apagada ou após `flutter clean`, use uma vez o comando abaixo para recriá-la.

## 4. Atalho opcional

Dê dois cliques em **Iniciar iPhone.command**, ou, na pasta principal:

```bash
bash inicializacao/iniciar_iphone.sh "iPhone 16e"
```

Esse script inicia o aplicativo, não a API. Ele reconhece o Simulator tradicional e o DeviceHub desta instalação do Xcode. O seletor aceita nome ou UUID; prefere um aparelho já ligado e depois a versão mais recente disponível.

## 5. Executar o backend

**Antes de executar:** resolva as pendências do ponto de entrada, imports e lançador descritas no início deste README. Os comandos abaixo representam o destino esperado após esse ajuste; não estão funcionais no estado atual.

Python 3.12 e Java 17+ são necessários. A primeira utilização do LanguageTool pode baixar seus componentes. Com dependências instaladas, o processamento no Mac pode funcionar sem internet.

Primeira instalação, a partir da pasta principal:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn api.01_main:app --reload
```

Nas próximas vezes, na pasta principal:

```bash
bash inicializacao/iniciar_api.sh --reload
```

Se já existia um ambiente virtual na antiga pasta `02_backend`, recrie-o em `backend/.venv`.

Abra [a documentação interativa](http://127.0.0.1:8000/docs). Teste `POST /extrair` com:

```json
{"mensagem": "Informe sua senha agora."}
```

- `GET /saude`: informa modelos carregados e pendências.
- `POST /extrair`: devolve 24 features, seis indicadores e cluster identificado.
- `POST /analisar`: responde 503 até existir um XGBoost compatível habilitado.
- 422: entrada inválida ou mensagem sem termos reconhecidos pelo TF-IDF.
- 503: componente indisponível; nunca significa que a mensagem é segura.

O simulador de iPhone neste Mac poderá acessar a API em `http://127.0.0.1:8000` quando a integração for implementada. A ShareExtension iOS possui interface própria e também precisa dessa integração.

## 6. Atualizar modelos

Altere `PASTA_MODELOS` em `backend/api/02_modelos.py` para apontar à nova pasta e reinicie a API. Os artefatos são carregados na inicialização, não em cada mensagem.

O conjunto deve ter TF-IDF/K-means/codificador, preprocessador do XGBoost e XGBoost treinados de forma compatível. O contrato está em `configuracao.json`: ordem das colunas, limiar validado, classe positiva e hashes. O K-means recebido usa scikit-learn 1.9.0. Não foi exportado um XGBoost definitivo com 30 atributos nesta organização.

## 7. Testes e verificação

Os resultados registrados ao final desta seção pertencem à organização anterior às alterações recentes. Não confirmam o funcionamento dos nomes atuais. Reexecute os testes após restaurar o ponto de entrada e os imports.

Dentro de `backend`, com o ambiente ativo:

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python tests/verificar_02_gramatica_real.py
```

O último comando utiliza Java/LanguageTool reais. O modelo sintético dos testes é temporário e nunca é instalado como classificador final. O dataset de estudo e os notebooks continuam fora desta pasta, em `../arquivo_prototipo_2026-10-05/` e nas pastas originais da residência.

Verificação em 05/10/2026 após a numeração: nove testes automatizados aprovados; features e clusters equivalentes para cinco mensagens de referência; compilação iOS concluída no iPhone 16e.
