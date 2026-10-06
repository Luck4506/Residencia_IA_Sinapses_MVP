// FINALIDADE: Cria a janela macOS e conecta a interface Flutter ao aplicativo desktop.
// FLUXO: suporte ao frontend; os modelos de IA pertencem à API Python.
import Cocoa
import FlutterMacOS

class MainFlutterWindow: NSWindow {
  override func awakeFromNib() {
    let flutterViewController = FlutterViewController()
    let windowFrame = self.frame
    self.contentViewController = flutterViewController
    self.setFrame(windowFrame, display: true)

    RegisterGeneratedPlugins(registry: flutterViewController)

    super.awakeFromNib()
  }
}
