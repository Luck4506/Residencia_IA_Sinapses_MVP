// FINALIDADE: Verifica a navegação e os elementos da interface Flutter; executado apenas pelos testes.
// FLUXO: suporte ao frontend; os modelos de IA pertencem à API Python.
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:protitipo_tela_aplicacao/main.dart';

void main() {
  testWidgets('Tema acompanha mudanças do sistema', (tester) async {
    final dispatcher = tester.binding.platformDispatcher;
    addTearDown(dispatcher.clearPlatformBrightnessTestValue);
    dispatcher.platformBrightnessTestValue = Brightness.dark;
    await tester.pumpWidget(const MyApp());
    await tester.pumpAndSettle();
    expect(
      Theme.of(tester.element(find.byType(Scaffold))).brightness,
      Brightness.dark,
    );
    dispatcher.platformBrightnessTestValue = Brightness.light;
    await tester.pumpAndSettle();
    expect(
      Theme.of(tester.element(find.byType(Scaffold))).brightness,
      Brightness.light,
    );
  });
  testWidgets('Compartilhar, avaliar, dar feedback e recomeçar', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(const MyApp());
    expect(
      Theme.of(tester.element(find.byType(Scaffold))).brightness,
      Brightness.light,
    );
    await tester.tap(find.byTooltip('Ativar tema escuro'));
    await tester.pumpAndSettle();
    expect(
      Theme.of(tester.element(find.byType(Scaffold))).brightness,
      Brightness.dark,
    );
    await tester.ensureVisible(find.text('Começar'));
    await tester.tap(find.text('Começar'));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Usar mensagem de exemplo'));
    await tester.tap(find.text('Usar mensagem de exemplo'));
    await tester.pumpAndSettle();
    expect(find.text('Sua mensagem'), findsOneWidget);
    expect(find.text(example), findsOneWidget);
    await tester.ensureVisible(find.text('Avaliar mensagem'));
    await tester.tap(find.text('Avaliar mensagem'));
    await tester.pumpAndSettle(const Duration(seconds: 1));
    expect(find.text('CHANCE DE SER GOLPE'), findsOneWidget);
    await tester.pumpAndSettle();
    expect(find.text('78%'), findsOneWidget);
    await tester.ensureVisible(find.text('Eu conheço quem enviou?'));
    await tester.tap(find.text('Eu conheço quem enviou?'));
    await tester.pumpAndSettle();
    expect(find.textContaining('Confira o número'), findsOneWidget);
    await tester.ensureVisible(find.byTooltip('Sim, ajudou'));
    await tester.tap(find.byTooltip('Sim, ajudou'));
    await tester.pump();
    expect(find.text('Obrigado pelo feedback!'), findsOneWidget);
    await tester.ensureVisible(find.text('Analisar outra mensagem'));
    await tester.tap(find.text('Analisar outra mensagem'));
    await tester.pumpAndSettle();
    expect(
      tester.widget<TextField>(find.byType(TextField)).controller!.text,
      isEmpty,
    );
    final button = tester.widget<FilledButton>(
      find.widgetWithText(FilledButton, 'Avaliar mensagem'),
    );
    expect(button.onPressed, isNull);
  });
  testWidgets(
    'Texto externo pula introdução e substitui mensagem com app aberto',
    (tester) async {
      debugDefaultTargetPlatformOverride = TargetPlatform.android;
      const channel = MethodChannel('sinal/shared_text');
      tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(
        channel,
        (call) async => example,
      );
      addTearDown(() {
        debugDefaultTargetPlatformOverride = null;
        tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(
          channel,
          null,
        );
      });
      await tester.pumpWidget(const MyApp());
      await tester.pumpAndSettle();
      expect(find.text('BOAS-VINDAS'), findsNothing);
      expect(
        tester.widget<TextField>(find.byType(TextField)).controller!.text,
        example,
      );
      await tester.binding.defaultBinaryMessenger.handlePlatformMessage(
        'sinal/shared_text',
        const StandardMethodCodec().encodeMethodCall(
          const MethodCall('sharedText', 'Outro texto recebido'),
        ),
        (_) {},
      );
      await tester.pumpAndSettle();
      expect(
        tester.widget<TextField>(find.byType(TextField)).controller!.text,
        'Outro texto recebido',
      );
      await tester.ensureVisible(find.byTooltip('Ativar tema escuro'));
      await tester.tap(find.byTooltip('Ativar tema escuro'));
      await tester.pumpAndSettle();
      expect(
        tester.widget<TextField>(find.byType(TextField)).controller!.text,
        'Outro texto recebido',
      );
      debugDefaultTargetPlatformOverride = null;
    },
  );
}
