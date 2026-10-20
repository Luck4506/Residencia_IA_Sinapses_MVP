# Frontend — Sinápses

Aplicativo multiplataforma desenvolvido com **Flutter e Dart**. A interface permite inserir uma mensagem, solicitar análise à API, consultar a pontuação e os sinais destacados e responder ao feedback local da tela.

O frontend depende do backend Python estar em execução. Para visão geral do projeto e instruções de preparação conjunta, consulte o [README principal](../README.md).

## Estrutura relevante

```text
frontend/
├── lib/
│   ├── main.dart       # Interface e fluxo principal da aplicação
│   └── api.dart        # Cliente HTTP e validação da resposta da API
├── test/
│   ├── api_test.dart
│   └── widget_test.dart
├── assets/             # Imagens utilizadas pela interface
├── ios/                # Projeto iOS e extensão de compartilhamento
├── web/                # Arquivos da versão web
├── android/            # Projeto Android
├── macos/              # Projeto macOS
├── linux/              # Projeto Linux
├── windows/            # Projeto Windows
├── pubspec.yaml
└── pubspec.lock
```

A maior parte do fluxo de tela está em `lib/main.dart`. `lib/api.dart` contém a classe `SmsApi`, responsável por enviar o texto para `POST /analisar`, tratar falhas de conexão e validar campos essenciais da resposta.

## Requisitos

- Flutter compatível com a versão de Dart declarada em `pubspec.yaml` (`^3.13.2`).
- API Sinápses iniciada e acessível pela URL configurada.
- Para iOS: macOS, Xcode e simulador ou dispositivo configurado.

## Executar com o script do projeto

A partir da raiz do repositório:

```bash
bash inicializacao/preparar.sh
bash inicializacao/iniciar.sh web
```

Acesse [http://localhost:8080](http://localhost:8080). O script inicia a API e o Flutter Web em conjunto. Para iPhone Simulator, use:

```bash
bash inicializacao/iniciar.sh iphone
```

## Executar o Flutter diretamente

Primeiro, inicie a API seguindo o [README do backend](../backend/README.md). Em outro terminal:

```bash
cd frontend
flutter pub get
flutter run
```

Para rodar especificamente no navegador:

```bash
flutter run -d web-server --web-hostname 127.0.0.1 --web-port 8080 \
  --dart-define=API_URL=http://127.0.0.1:8000
```

Se necessário, o diagnóstico detalhado pode ser ocultado na compilação:

```bash
flutter run -d web-server \
  --dart-define=API_URL=http://127.0.0.1:8000 \
  --dart-define=SHOW_DIAGNOSTICS=false
```

## Configuração da API

A URL pode ser configurada durante a compilação/execução usando `--dart-define=API_URL=...`. Se a variável não for fornecida, `lib/api.dart` usa os padrões abaixo:

| Ambiente | URL padrão |
|---|---|
| Web, iOS Simulator e demais plataformas não Android | `http://127.0.0.1:8000` |
| Emulador Android | `http://10.0.2.2:8000` |

Para um celular físico, o endereço `127.0.0.1` aponta para o próprio aparelho, não para o computador. Inicie a API escutando na rede local e passe o endereço IP do computador, por exemplo:

```bash
API_HOST=0.0.0.0 API_PORT=8000 bash inicializacao/iniciar_api.sh
```

Em outro terminal, execute o Flutter usando o IP real do computador na mesma rede:

```bash
cd frontend
flutter run --dart-define=API_URL=http://IP_DO_COMPUTADOR:8000
```

Substitua `IP_DO_COMPUTADOR` pelo endereço de rede local correto. Não exponha a API à internet pública sem controles de segurança apropriados.

## Fluxo de comunicação

1. O usuário informa uma mensagem.
2. `SmsApi.analyze()` envia `{"mensagem": "..."}` para `POST /analisar`.
3. O cliente espera a resposta (timeout de 90 segundos) e verifica campos como `score_golpe`, `features_binarias`, `features_importantes` e `classe`.
4. Erros HTTP, tempo limite, falhas de conexão ou respostas inválidas são convertidos em mensagens de erro para a interface.

A resposta completa e os campos estão documentados no [README do backend](../backend/README.md).

## Diagnóstico e feedback

A opção `SHOW_DIAGNOSTICS` controla a exibição da caixa com os indicadores extraídos. O padrão dos scripts de inicialização é `true`; para ocultá-la, defina `SHOW_DIAGNOSTICS=false` ou use `--dart-define=SHOW_DIAGNOSTICS=false`.

O feedback de polegar mostrado na interface é local. O projeto não persiste esse feedback nem o utiliza para retreinar o classificador.

## Testes

```bash
cd frontend
flutter test
```

Os testes automatizados ficam em `test/api_test.dart` e `test/widget_test.dart`.
