import 'api.dart';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

void main() => runApp(const MyApp());

const orange = Color(0xFFEF922E);
const example =
    'Olá! Identificamos uma pendência no seu cadastro. Para evitar o bloqueio da sua conta, confirme seus dados no link enviado em até 30 minutos.';

class MyApp extends StatefulWidget {
  const MyApp({super.key, this.api});
  final SmsApi? api;
  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  ThemeMode themeMode = ThemeMode.system;
  ThemeData makeTheme(Brightness brightness) {
    final isDark = brightness == Brightness.dark;
    final scheme = ColorScheme.fromSeed(
      seedColor: orange,
      brightness: brightness,
      primary: isDark ? orange : const Color(0xFF9B4C00),
      surface: isDark ? const Color(0xFF1B1C20) : Colors.white,
    );
    return ThemeData(
      brightness: brightness,
      colorScheme: scheme,
      fontFamily: 'Arial',
      scaffoldBackgroundColor: isDark
          ? const Color(0xFF101113)
          : const Color(0xFFF7F6F2),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: orange,
          foregroundColor: const Color(0xFF261604),
          minimumSize: const Size(double.infinity, 56),
          textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'Assistente de mensagens',
    debugShowCheckedModeBanner: false,
    theme: makeTheme(Brightness.light),
    darkTheme: makeTheme(Brightness.dark),
    themeMode: themeMode,
    home: Builder(
      builder: (context) => AssistantFlow(
        api: widget.api,
        onToggleTheme: () => setState(() {
          themeMode = Theme.of(context).brightness == Brightness.dark
              ? ThemeMode.light
              : ThemeMode.dark;
        }),
      ),
    ),
  );
}

class AssistantFlow extends StatefulWidget {
  const AssistantFlow({super.key, required this.onToggleTheme, this.api});
  final SmsApi? api;
  final VoidCallback onToggleTheme;
  @override
  State<AssistantFlow> createState() => _AssistantFlowState();
}

class _AssistantFlowState extends State<AssistantFlow> {
  static const channel = MethodChannel('sinal/shared_text');
  final controller = TextEditingController();
  late final SmsApi api;
  Map<String, dynamic>? analysis;
  String? error;
  int requestId = 0;
  static const showDiagnostics = bool.fromEnvironment(
    'SHOW_DIAGNOSTICS',
    defaultValue: true,
  );
  int step = 0;
  bool loading = false;
  bool shared = false;
  int? feedback;
  Color get muted => Theme.of(context).colorScheme.onSurfaceVariant;
  Color get accent => Theme.of(context).colorScheme.primary;
  Color get border => Theme.of(context).colorScheme.outlineVariant;

  @override
  void initState() {
    super.initState();
    api = widget.api ?? SmsApi();
    if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
      channel.setMethodCallHandler((call) async {
        if (call.method == 'sharedText') receive(call.arguments as String?);
      });
      channel
          .invokeMethod<String>('getInitialText')
          .then(receive)
          .catchError((Object _) {});
    }
  }

  void receive(String? text) {
    if (!mounted || text == null || text.trim().isEmpty) return;
    setState(() {
      requestId++;
      analysis = null;
      error = null;
      controller.text = text;
      shared = true;
      loading = false;
      feedback = null;
      step = 1;
    });
  }

  @override
  void dispose() {
    channel.setMethodCallHandler(null);
    if (widget.api == null) api.close();
    controller.dispose();
    super.dispose();
  }

  Future<void> analyze() async {
    if (controller.text.trim().isEmpty || loading) return;
    FocusScope.of(context).unfocus();
    final text = controller.text;
    final currentRequest = ++requestId;
    setState(() {
      loading = true;
      error = null;
      analysis = null;
    });
    try {
      final response = await api.analyze(text);
      if (!mounted || currentRequest != requestId) return;
      setState(() {
        analysis = response;
        step = 2;
        feedback = null;
      });
    } catch (exception) {
      if (!mounted || currentRequest != requestId) return;
      setState(
        () => error = exception.toString().replaceFirst('Exception: ', ''),
      );
    } finally {
      if (mounted && currentRequest == requestId)
        setState(() => loading = false);
    }
  }

  Widget label(String text) => Text(
    text,
    style: TextStyle(
      color: accent,
      fontSize: 11,
      letterSpacing: 2,
      fontWeight: FontWeight.w700,
    ),
  );
  Widget heading(String text) => Padding(
    padding: const EdgeInsets.only(top: 14, bottom: 14),
    child: Text(
      text,
      style: TextStyle(
        fontSize: 36,
        height: 1.12,
        letterSpacing: -1.3,
        fontWeight: FontWeight.w700,
      ),
    ),
  );
  Widget description(String text) =>
      Text(text, style: TextStyle(color: muted, fontSize: 15, height: 1.6));
  Widget card(Widget child, {Color? color}) => Container(
    width: double.infinity,
    padding: const EdgeInsets.all(22),
    decoration: BoxDecoration(
      color: color ?? Theme.of(context).colorScheme.surface,
      borderRadius: BorderRadius.circular(22),
      border: Border.all(color: border),
    ),
    child: Material(color: Colors.transparent, child: child),
  );
  Widget action(
    String text,
    VoidCallback? onPressed, {
    IconData icon = Icons.arrow_forward_rounded,
  }) => FilledButton(
    onPressed: onPressed,
    child: Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Flexible(child: Text(text)),
        const SizedBox(width: 12),
        Icon(icon, size: 20),
      ],
    ),
  );

  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 520),
          child: SingleChildScrollView(
            key: ValueKey(step),
            padding: const EdgeInsets.symmetric(horizontal: 26, vertical: 24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Image.asset(
                      'assets/eldorado.png',
                      width: 116,
                      semanticLabel: 'Instituto Eldorado',
                    ),
                    const Spacer(),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 8,
                      ),
                      decoration: BoxDecoration(
                        color: const Color(0xFFE4E6E0),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Image.asset(
                        'assets/tic-em-trilhas.png',
                        width: 90,
                        semanticLabel: 'TIC em trilhas',
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 30),
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: orange,
                        borderRadius: BorderRadius.circular(11),
                      ),
                      child: const Icon(
                        Icons.radar_rounded,
                        color: Color(0xFF17120C),
                        size: 22,
                      ),
                    ),
                    const SizedBox(width: 10),
                    Text(
                      'Sinápses',
                      style: TextStyle(
                        fontSize: 25,
                        fontWeight: FontWeight.bold,
                        letterSpacing: -1,
                      ),
                    ),
                    const Spacer(),
                    IconButton(
                      tooltip: Theme.of(context).brightness == Brightness.light
                          ? 'Ativar tema escuro'
                          : 'Ativar tema claro',
                      onPressed: widget.onToggleTheme,
                      icon: Icon(
                        Theme.of(context).brightness == Brightness.light
                            ? Icons.dark_mode_outlined
                            : Icons.light_mode_outlined,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 28),
                Row(
                  children: List.generate(
                    3,
                    (index) => Expanded(
                      child: Padding(
                        padding: EdgeInsets.only(right: index < 2 ? 6 : 0),
                        child: Container(
                          height: 3,
                          color: index <= step ? orange : border,
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 28),
                if (step == 0) ...intro(),
                if (step == 1) ...message(),
                if (step == 2) ...result(),
                const SizedBox(height: 26),
                Center(
                  child: Text(
                    'Residência Tecnológica em IA  /  2026',
                    style: TextStyle(color: Color(0xFF787984), fontSize: 11),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    ),
  );

  List<Widget> intro() => [
    label('BOAS-VINDAS'),
    heading('Conheça seu\nassistente de mensagens.'),
    description(
      'Um apoio para avaliar mensagens suspeitas e reconhecer possíveis sinais de golpe.',
    ),
    const SizedBox(height: 32),
    card(
      Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Como funciona',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 22),
          introStep(
            '1',
            'Traga uma mensagem',
            'Na próxima tela, você pode inserir o texto que deseja avaliar.',
          ),
          const SizedBox(height: 22),
          introStep(
            '2',
            'Confira a avaliação',
            'Veja o risco indicado e perguntas que ajudam a conferir a mensagem.',
          ),
        ],
      ),
    ),
    const SizedBox(height: 32),
    action('Começar', () => setState(() => step = 1)),
  ];

  Widget introStep(String number, String title, String text) => Row(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(
        number.padLeft(2, '0'),
        style: TextStyle(
          color: muted,
          fontSize: 13,
          fontWeight: FontWeight.w600,
        ),
      ),
      const SizedBox(width: 16),
      Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 6),
            description(text),
          ],
        ),
      ),
    ],
  );

  List<Widget> message() => [
    label('02 / REVISE A MENSAGEM'),
    heading('O que chegou\npara você?'),
    description(
      'Confira o texto abaixo e toque em avaliar. Você também pode escrever ou colar uma mensagem.',
    ),
    const SizedBox(height: 24),
    card(
      Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                shared ? Icons.move_to_inbox_outlined : Icons.message_outlined,
                color: orange,
                size: 18,
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  shared
                      ? 'Texto recebido • pronto para avaliar'
                      : 'Sua mensagem',
                  style: TextStyle(color: muted, fontSize: 12),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          TextField(
            controller: controller,
            enabled: !loading,
            onChanged: (_) => setState(() {}),
            minLines: 6,
            maxLines: 12,
            maxLength: 5000,
            style: TextStyle(fontSize: 17, height: 1.6),
            decoration: InputDecoration(
              border: InputBorder.none,
              hintText: 'A mensagem que você quer analisar aparece aqui…',
              hintStyle: TextStyle(color: Color(0xFF777984)),
              counterStyle: TextStyle(color: muted),
            ),
          ),
        ],
      ),
    ),
    const SizedBox(height: 10),
    TextButton(
      onPressed: loading
          ? null
          : () {
              setState(() {
                controller.text = example;
                shared = false;
              });
            },
      child: Text('Usar mensagem de exemplo'),
    ),
    const SizedBox(height: 16),
    if (error != null) ...[
      Text(
        error!,
        style: TextStyle(color: Theme.of(context).colorScheme.error),
      ),
      const SizedBox(height: 12),
    ],
    action(
      loading ? 'Avaliando…' : 'Avaliar mensagem',
      controller.text.trim().isEmpty || loading ? null : analyze,
      icon: Icons.auto_awesome_outlined,
    ),
    const SizedBox(height: 12),
    Center(
      child: TextButton(
        onPressed: loading ? null : () => setState(() => step = 0),
        child: Text('Voltar ao início', style: TextStyle(color: muted)),
      ),
    ),
  ];

  Widget question(String number, String title, String help) => ExpansionTile(
    tilePadding: EdgeInsets.zero,
    childrenPadding: const EdgeInsets.only(bottom: 16),
    shape: const Border(),
    collapsedShape: const Border(),
    leading: Text(
      number,
      style: TextStyle(color: accent, fontWeight: FontWeight.w700),
    ),
    title: Text(
      title,
      style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
    ),
    children: [description(help)],
  );

  List<Widget> result() => [
    label('03 / RESULTADO DA AVALIAÇÃO'),
    heading('Qual é o risco?'),
    description(
      'Veja a chance de ser golpe e confira os pontos abaixo antes de agir.',
    ),
    const SizedBox(height: 22),
    card(
      Column(
        children: [
          label('CHANCE DE SER GOLPE'),
          const SizedBox(height: 24),
          Semantics(
            label:
                '${((analysis!["score_golpe"] as num) * 100).toStringAsFixed(1)} por cento de chance de golpe.',
            child: ExcludeSemantics(
              child: SizedBox(
                width: 210,
                height: 210,
                child: TweenAnimationBuilder<double>(
                  tween: Tween(
                    begin: 0,
                    end: (analysis!['score_golpe'] as num).toDouble(),
                  ),
                  duration: const Duration(milliseconds: 1000),
                  builder: (context, value, child) => Stack(
                    alignment: Alignment.center,
                    children: [
                      Positioned.fill(
                        child: CircularProgressIndicator(
                          value: value,
                          strokeWidth: 15,
                          strokeCap: StrokeCap.round,
                          backgroundColor: border,
                          color: analysis!['classe'] == 1
                              ? const Color(0xFFC97575)
                              : const Color(0xFF62A889),
                        ),
                      ),
                      Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            '${(value * 100).toStringAsFixed(1)}%',
                            style: const TextStyle(
                              fontSize: 54,
                              fontWeight: FontWeight.w700,
                              letterSpacing: -3,
                            ),
                          ),
                          Text(
                            analysis!['classe'] == 1
                                ? 'possível golpe'
                                : 'menor risco indicado',
                            style: TextStyle(fontSize: 14, color: muted),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(height: 24),
          Text(
            'Avaliação do modelo',
            style: TextStyle(color: accent, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          description(
            'A avaliação pode errar. Confira a mensagem e a identidade do remetente antes de agir.',
          ),
        ],
      ),
    ),
    const SizedBox(height: 22),
    card(
      Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Principais sinais identificados',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 12),
          if ((analysis!['features_importantes'] as List).isEmpty)
            description(
              'Nenhum atributo estruturado detectado aumentou o risco nesta análise. O modelo também considera o texto completo.',
            ),
          for (final item in analysis!['features_importantes'] as List)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Text('• ${featureLabel(item["feature"] as String)}'),
            ),
        ],
      ),
    ),
    if (showDiagnostics) ...[
      const SizedBox(height: 14),
      card(
        ExpansionTile(
          key: const Key('diagnostico'),
          tilePadding: EdgeInsets.zero,
          title: const Text('Diagnóstico: todas as features'),
          subtitle: const Text('Uso interno • toque para expandir'),
          children: [
            description(
              '0 = não detectado; 1 = detectado. Carga emocional exibida por categoria; o modelo recebe 0/1/2.',
            ),
            const SizedBox(height: 12),
            for (final entry in {
              ...analysis!['features_binarias'] as Map<String, dynamic>,
              ...analysis!['features_clusters'] as Map<String, dynamic>,
            }.entries)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 5),
                child: Row(
                  children: [
                    Expanded(
                      child: SelectableText(
                        entry.key,
                        style: const TextStyle(fontSize: 12),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      '${entry.value}',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    ],
    const SizedBox(height: 26),
    Text(
      'Antes de confiar, pergunte:',
      style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w600),
    ),
    const SizedBox(height: 8),
    description('Toque em cada pergunta para ver como conferir.'),
    const SizedBox(height: 14),
    card(
      Column(
        children: [
          question(
            '01',
            'Eu conheço quem enviou?',
            'Confira o número ou endereço completo. Um nome conhecido e uma foto de perfil, sozinhos, não confirmam a identidade.',
          ),
          Divider(color: border),
          question(
            '02',
            'Estão me pressionando a agir agora?',
            'Pare por um momento. Pense se a ameaça, o prazo curto ou a promessa fazem sentido para a situação.',
          ),
          Divider(color: border),
          question(
            '03',
            'Pedem dinheiro, senha ou algum código?',
            'Antes de responder, confirme o pedido por outro canal que você já conhece e usa.',
          ),
          Divider(color: border),
          question(
            '04',
            'Consigo confirmar no canal oficial?',
            'Abra o aplicativo ou site oficial por conta própria e confira a informação, sem usar o link da mensagem.',
          ),
        ],
      ),
    ),
    const SizedBox(height: 14),
    ExpansionTile(
      tilePadding: const EdgeInsets.symmetric(horizontal: 4),
      title: Text(
        'Ver mensagem analisada',
        style: TextStyle(fontSize: 14, color: muted),
      ),
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: SelectableText(controller.text, style: TextStyle(height: 1.6)),
        ),
      ],
    ),
    const SizedBox(height: 18),
    Row(
      children: [
        Expanded(
          child: Text(
            feedback == null
                ? 'Essa resposta ajudou?'
                : 'Obrigado pelo feedback!',
            style: TextStyle(fontSize: 13, color: muted),
          ),
        ),
        IconButton(
          tooltip: 'Sim, ajudou',
          onPressed: () => setState(() => feedback = 1),
          icon: Icon(
            feedback == 1 ? Icons.thumb_up : Icons.thumb_up_outlined,
            color: feedback == 1 ? orange : muted,
          ),
        ),
        IconButton(
          tooltip: 'Não ajudou',
          onPressed: () => setState(() => feedback = 0),
          icon: Icon(
            feedback == 0 ? Icons.thumb_down : Icons.thumb_down_outlined,
            color: feedback == 0 ? orange : muted,
          ),
        ),
      ],
    ),
    const SizedBox(height: 20),
    action(
      'Analisar outra mensagem',
      () => setState(() {
        controller.clear();
        shared = false;
        step = 1;
      }),
    ),
    Center(
      child: TextButton(
        onPressed: () => setState(() {
          controller.clear();
          shared = false;
          step = 0;
        }),
        child: Text('Finalizar', style: TextStyle(color: muted)),
      ),
    ),
  ];
}

String featureLabel(String name) =>
    const {
      'solicita_senha': 'Pedido de senha',
      'solicita_codigo_autenticacao': 'Pedido de código de autenticação',
      'solicita_dados_bancarios': 'Pedido de dados bancários',
      'solicita_dados_cartao': 'Pedido de dados do cartão',
      'solicita_dados_cadastro': 'Pedido de dados ou atualização de cadastro',
      'solicita_pagamento': 'Pedido de pagamento',
      'solicita_clique': 'Pedido para clicar',
      'menciona_bloqueio_conta': 'Menção a bloqueio de conta',
      'carga_emocional': 'Linguagem emocional',
      'possui_urgencia': 'Senso de urgência',
      'possui_ameaca': 'Ameaça',
      'possui_linguagem_alarmista': 'Linguagem alarmista',
      'possui_recompensa': 'Oferta de recompensa',
      'possui_reembolso': 'Menção a reembolso',
      'possui_vantagem_inesperada': 'Vantagem inesperada',
      'possui_oferta_financeira': 'Oferta financeira',
      'possui_url': 'Presença de link',
      'possui_url_encurtada': 'Link encurtado',
      'possui_telefone': 'Presença de telefone',
      'possui_pix': 'Menção a Pix',
      'possui_erros_ortografia_gramatica': 'Erros de escrita',
      'possui_chamada_acao': 'Chamada para agir',
    }[name] ??
    name.replaceAll('_', ' ');
