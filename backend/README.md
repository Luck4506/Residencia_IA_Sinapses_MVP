# Backend — Sinápses

Backend de análise de mensagens implementado em **Python com FastAPI**. A API valida o texto, extrai 22 atributos estruturados, calcula um indicador de agrupamento TF-IDF/K-means e executa um classificador XGBoost com embeddings multilíngues.

Para visão geral e inicialização conjunta do projeto, consulte o [README principal](../README.md).

## Arquitetura

```text
backend/
├── api/
│   ├── main.py          # Aplicação FastAPI, rotas, validação e CORS
│   ├── servico.py       # Coordena extração, agrupamento e classificação
│   ├── extracao.py      # Integra o extrator de atributos e LanguageTool
│   ├── agrupamento.py   # TF-IDF e escolha do cluster mais próximo
│   ├── classificacao.py # Vetor de entrada, XGBoost e contribuições TreeSHAP
│   ├── explicacao.py    # Descrições fixas dos sinais destacados
│   ├── modelos.py       # Carregamento e validação dos artefatos
│   ├── preparacao.py    # Validação do texto de entrada
│   └── erros.py         # Erros de indisponibilidade
├── extrator_features/   # Regras e bibliotecas auxiliares dos 22 atributos
├── modelos/v1/          # Artefatos pequenos usados na inferência
├── tests/               # Testes automatizados
├── requirements.txt
└── requirements-dev.txt
```

Os componentes do modelo são carregados na inicialização da aplicação. O serviço verifica a disponibilidade dos modelos e do LanguageTool local; a rota `/saude` informa o estado e as pendências.

## Requisitos e preparação

- Python 3.12
- Java 17 ou superior, necessário ao LanguageTool local
- Dependências listadas em `requirements.txt`
- Internet na primeira preparação para baixar o encoder de embeddings e preparar o LanguageTool

A partir da raiz do repositório, execute:

```bash
bash inicializacao/preparar.sh
```

O script cria `backend/.venv`, instala as dependências Python, prepara o modelo `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, configura o LanguageTool 6.8 e instala as dependências Flutter. Os arquivos grandes e caches gerados ficam fora do Git.

No macOS, caso o XGBoost precise de OpenMP e a biblioteca não esteja disponível, execute `brew install libomp`.

## Executar a API

### Opção recomendada: inicializador do projeto

Na raiz do repositório:

```bash
bash inicializacao/iniciar.sh web
```

O script inicia a API e o frontend juntos. Para escolher uma porta específica para a API:

```bash
API_PORT=8001 bash inicializacao/iniciar.sh web
```

### Executar somente a API

Após a preparação:

```bash
cd backend
.venv/bin/python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Para permitir acesso de outro dispositivo na rede local, use `--host 0.0.0.0` e configure o frontend com o IP do computador. Isso não deve ser confundido com disponibilizar o serviço publicamente na internet.

A documentação interativa do FastAPI fica em `http://127.0.0.1:8000/docs` enquanto a API estiver ativa.

## Endpoints

### `GET /saude`

Retorna o estado da API e dos componentes, incluindo `kmeans_carregado`, `gramatica_verificada`, `xgboost_carregado`, `classificacao_disponivel` e eventuais `pendencias`.

### `POST /extrair`

Extrai os atributos e indicadores de cluster sem executar a classificação final.

### `POST /analisar`

Executa o pipeline completo e retorna os atributos, os sinais detectados, a pontuação e a classe prevista.

As duas rotas `POST` recebem um corpo JSON neste formato:

```json
{
  "mensagem": "Urgente! Confira sua conta pelo link enviado."
}
```

A mensagem precisa ser uma string não vazia com no máximo 5.000 caracteres. Texto vazio ou maior que o limite resulta em erro de validação HTTP 422. Falhas de componentes necessários à análise podem resultar em HTTP 503.

### Campos principais da resposta de `/analisar`

| Campo | Significado |
|---|---|
| `score_golpe` | Saída numérica do classificador entre 0 e 1. |
| `probabilidade_percentual` | `score_golpe` multiplicado por 100 e arredondado para duas casas. Não é garantia de risco real. |
| `classe` | `1` quando a pontuação atinge o limiar; caso contrário, `0`. |
| `limiar` | Limiar de decisão carregado da configuração do modelo (0,55 na versão entregue). |
| `features` | Valores dos 22 atributos extraídos. |
| `features_binarias` | Representação binária dos atributos e indicadores da categoria emocional. |
| `features_clusters` | Seis indicadores de cluster, com um indicador ativo. |
| `features_completas` | Atributos utilizados no fluxo de classificação, incluindo os indicadores de cluster. |
| `sinais_detectados` | Nomes dos atributos detectados na mensagem. |
| `features_importantes` | Até cinco atributos detectados com contribuição positiva, ordenados pela contribuição calculada com TreeSHAP. |
| `explicacao_sinais` | Texto determinístico montado a partir de descrições fixas dos sinais destacados. |
| `cluster_identificado` | Índice do cluster atribuído pelo agrupamento auxiliar. |

A contribuição TreeSHAP de cada atributo está expressa na escala interna do modelo, não em porcentagem. Os atributos exibidos não constituem a explicação completa: o embedding do texto e os indicadores de cluster também participam da classificação.

## Pipeline de inferência

1. **Validação:** preserva o texto original e rejeita mensagens vazias ou com mais de 5.000 caracteres.
2. **Extração de atributos:** aplica regras para 22 sinais estruturados e verifica aspectos gramaticais com LanguageTool local.
3. **Representação textual:** calcula um embedding de 384 dimensões usando `paraphrase-multilingual-MiniLM-L12-v2`.
4. **Agrupamento auxiliar:** calcula TF-IDF e escolhe o centroide K-means mais próximo, produzindo seis indicadores de cluster.
5. **Classificação:** concatena 384 dimensões de embedding, 22 atributos e seis indicadores, totalizando 412 valores, na ordem registrada em `modelos/v1/xgboost_config.json`.
6. **Resposta:** aplica o limiar 0,55 e constrói os campos de sinais e explicação.

A versão entregue não treina nem atualiza o classificador durante a execução. O modelo e as configurações são carregados a partir dos artefatos existentes.

### Ajustes de atributos na versão integrada

- `solicita_ligacao` não faz parte do contrato ativo.
- `solicita_dados_cadastro` combina `solicita_dados_pessoais` e `solicita_atualizacao_cadastro` por uma regra lógica OU.
- `carga_emocional` é ordinal: baixa = 0, média = 1 e alta = 2. A representação binária inclui indicadores para essas categorias.

## Artefatos e preparação do encoder

`modelos/v1/` contém os artefatos pequenos necessários à inferência, incluindo o modelo XGBoost, configuração, vocabulário/IDF e centroides de K-means. O encoder de embeddings é preparado localmente pelo script `inicializacao/preparar_modelos.py` e não é armazenado no Git devido ao tamanho.

A variável `PASTA_MODELOS` permite indicar outra pasta de artefatos compatíveis. Os artefatos devem manter as dimensões, os nomes e a ordem esperados pelo arquivo `xgboost_config.json`.

## Configuração de rede

- `API_HOST`: host usado pelo script que inicia a API; o padrão é local.
- `API_PORT`: porta da API; o inicializador escolhe uma porta livre entre 8000 e 8010 se nenhuma for informada.
- `CORS_ORIGINS`: origens adicionais separadas por vírgula. As origens locais `localhost` e `127.0.0.1` são permitidas pelo padrão de desenvolvimento.
- `PASTA_MODELOS`: diretório alternativo de artefatos compatíveis.

A versão web e os simuladores podem usar `127.0.0.1`; o emulador Android geralmente precisa do endereço especial `10.0.2.2` no frontend. Para um aparelho físico, use o IP local do computador e mantenha ambos na mesma rede.

## Testes

Instale as dependências de desenvolvimento e execute:

```bash
cd backend
.venv/bin/python -m pip install -r requirements-dev.txt
PYTHONPATH=. .venv/bin/python -m pytest tests/test_01_fluxo.py -q
```

Os testes verificam o contrato do extrator, a regra de união cadastral, a remoção de atributos antigos, a validação do texto, a inferência com os modelos, a codificação binária e o CORS local.

## Desempenho e limitações

A avaliação apresentada para o conjunto de teste de 219 mensagens registra uma matriz de confusão com 124 verdadeiros negativos, 2 falsos positivos, 10 falsos negativos e 83 verdadeiros positivos. Esses valores correspondem a acurácia de 94,52%, precisão de 97,65%, recall de 89,65% e F1-score de aproximadamente 93,26%.

Os resultados dependem da base de avaliação e não garantem o mesmo desempenho em mensagens novas. Há falsos positivos e falsos negativos possíveis. A pontuação não comprova que uma mensagem seja fraudulenta nem garante que seja segura. A explicação textual é baseada em descrições fixas, e o feedback da interface não é armazenado nem usado para retreinamento.

## Privacidade

A análise usa componentes locais e não envia o texto da mensagem a serviços externos durante a inferência. A primeira preparação, entretanto, baixa dependências e o modelo de embeddings. Não inclua mensagens pessoais em logs públicos, issues ou exemplos de documentação sem autorização.
