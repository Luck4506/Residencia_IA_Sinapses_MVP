import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:protitipo_tela_aplicacao/api.dart';

void main() {
  test('Falha HTTP preserva a explicação da API', () async {
    final api = SmsApi(client: MockClient((_) async => http.Response('{"detail":"Modelo indisponível"}', 503, headers: {'content-type': 'application/json; charset=utf-8'})));
    await expectLater(api.analyze('Olá'), throwsA(predicate((e) => e.toString().contains('Modelo indisponível'))));
  });
  test('Falha de rede não produz resultado fictício', () async {
    final api = SmsApi(client: MockClient((_) async => throw http.ClientException('offline')));
    await expectLater(api.analyze('Olá'), throwsA(predicate((e) => e.toString().contains('conectar'))));
  });
  test('Resposta malformada é rejeitada', () async {
    final api = SmsApi(client: MockClient((_) async => http.Response('{}', 200)));
    await expectLater(api.analyze('Olá'), throwsA(predicate((e) => e.toString().contains('inválida'))));
  });
}
