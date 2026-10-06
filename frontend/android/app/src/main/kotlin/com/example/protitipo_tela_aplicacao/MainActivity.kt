// FINALIDADE: Inicializa a atividade Android e encaminha texto compartilhado para o Flutter.
// FLUXO: suporte ao frontend; os modelos de IA pertencem à API Python.
package com.example.protitipo_tela_aplicacao

import android.content.Intent
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    private var sharedChannel: MethodChannel? = null

    private fun sharedText(intent: Intent?): String? {
        if (intent?.action != Intent.ACTION_SEND || intent.type != "text/plain") return null
        return intent.getStringExtra(Intent.EXTRA_TEXT)?.takeIf { it.isNotBlank() }
    }

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        sharedChannel = MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "sinal/shared_text")
        sharedChannel?.setMethodCallHandler { call, result ->
            if (call.method == "getInitialText") {
                result.success(sharedText(intent))
                intent?.removeExtra(Intent.EXTRA_TEXT)
            } else result.notImplemented()
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        sharedText(intent)?.let { sharedChannel?.invokeMethod("sharedText", it) }
        intent.removeExtra(Intent.EXTRA_TEXT)
    }
}
