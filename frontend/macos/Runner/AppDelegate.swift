// FINALIDADE: Inicializa o aplicativo nativo e registra a integração com Flutter nesta plataforma.
// FLUXO: suporte ao frontend; os modelos de IA pertencem à API Python.
import Cocoa
import FlutterMacOS

@main
class AppDelegate: FlutterAppDelegate {
  override func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
    return true
  }

  override func applicationSupportsSecureRestorableState(_ app: NSApplication) -> Bool {
    return true
  }
}
