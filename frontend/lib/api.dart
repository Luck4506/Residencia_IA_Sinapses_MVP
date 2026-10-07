import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class SmsApi {
  SmsApi({http.Client? client}) : client = client ?? http.Client();
  final http.Client client;
  static String get baseUrl {
    const configured = String.fromEnvironment('API_URL');
    if (configured.isNotEmpty)
      return configured.replaceFirst(RegExp(r'/$'), '');
    return !kIsWeb && defaultTargetPlatform == TargetPlatform.android
        ? 'http://10.0.2.2:8000'
        : 'http://127.0.0.1:8000';
  }

  Future<Map<String, dynamic>> analyze(String message) async {
    try {
      final response = await client
          .post(
            Uri.parse('$baseUrl/analisar'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'mensagem': message}),
          )
          .timeout(const Duration(seconds: 90));
      final data =
          jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
      if (response.statusCode != 200) {
        final detail = data['detail'];
        throw Exception(
          detail is String
              ? detail
              : 'Confira a mensagem (limite de 5.000 caracteres).',
        );
      }
      final score = data['score_golpe'];
      if (score is! num ||
          !score.isFinite ||
          score < 0 ||
          score > 1 ||
          data['features_binarias'] is! Map ||
          data['features_importantes'] is! List ||
          (data['classe'] != 0 && data['classe'] != 1)) {
        throw const FormatException('Resposta inválida');
      }
      return data;
    } on TimeoutException {
      throw Exception('A análise demorou demais. Tente novamente.');
    } on http.ClientException {
      throw Exception(
        'Não foi possível conectar à API. Confira se o servidor está iniciado e acessível.',
      );
    } on FormatException {
      throw Exception('A API retornou uma resposta inválida.');
    }
  }

  void close() => client.close();
}
