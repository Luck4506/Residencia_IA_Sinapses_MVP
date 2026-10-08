import UIKit
import SwiftUI
import UniformTypeIdentifiers

final class ShareViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        let model = SharedMessage()
        let host = UIHostingController(rootView: SharedMessageView(model: model) { [weak self] in
            self?.extensionContext?.completeRequest(returningItems: nil)
        })
        addChild(host)
        view.addSubview(host.view)
        host.view.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            host.view.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            host.view.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            host.view.topAnchor.constraint(equalTo: view.topAnchor),
            host.view.bottomAnchor.constraint(equalTo: view.bottomAnchor)
        ])
        host.didMove(toParent: self)
        Task { @MainActor in
            var texts: [String] = []
            for item in extensionContext?.inputItems as? [NSExtensionItem] ?? [] {
                var attachments: [String] = []
                for provider in item.attachments ?? [] {
                    let type = provider.hasItemConformingToTypeIdentifier(UTType.plainText.identifier)
                        ? UTType.plainText.identifier : UTType.url.identifier
                    guard provider.hasItemConformingToTypeIdentifier(type) else { continue }
                    let text: String? = await withCheckedContinuation { continuation in
                        provider.loadItem(forTypeIdentifier: type, options: nil) { value, _ in
                            if let text = value as? String { continuation.resume(returning: text) }
                            else if let url = value as? URL { continuation.resume(returning: url.absoluteString) }
                            else if let data = value as? Data { continuation.resume(returning: String(data: data, encoding: .utf8)) }
                            else { continuation.resume(returning: nil) }
                        }
                    }
                    if let text, !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty { attachments.append(text) }
                }
                if attachments.isEmpty, let text = item.attributedContentText?.string { attachments.append(text) }
                texts.append(contentsOf: attachments)
            }
            model.text = texts.joined(separator: "\n\n")
            model.loading = false
        }
    }
}

final class SharedMessage: ObservableObject {
    @Published var text = ""
    @Published var loading = true
}

private struct SharedMessageView: View {
    @ObservedObject var model: SharedMessage
    let close: () -> Void
    @Environment(\.colorScheme) private var systemScheme
    @State private var overrideScheme: ColorScheme?
    @State private var result = false
    @State private var progress = 0.0
    @State private var analyzing = false
    @State private var error: String?
    @State private var analysis: Analysis?
    private var settings: [String: String] {
        let encoded = Bundle.main.object(forInfoDictionaryKey: "SinapsesDartDefines") as? String ?? ""
        return encoded.split(separator: ",").reduce(into: [:]) { values, part in
            guard let data = Data(base64Encoded: String(part)), let text = String(data: data, encoding: .utf8),
                  let equal = text.firstIndex(of: "=") else { return }
            values[String(text[..<equal])] = String(text[text.index(after: equal)...])
        }
    }

    private func analyze() async {
        analyzing = true; error = nil
        defer { analyzing = false }
        do {
            let base = settings["API_URL"] ?? "http://127.0.0.1:8000"
            guard let url = URL(string: base.trimmingCharacters(in: CharacterSet(charactersIn: "/")) + "/analisar") else { throw URLError(.badURL) }
            var request = URLRequest(url: url, timeoutInterval: 90)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.httpBody = try JSONSerialization.data(withJSONObject: ["mensagem": model.text])
            let (data, response) = try await URLSession.shared.data(for: request)
            guard (response as? HTTPURLResponse)?.statusCode == 200 else {
                let detail = (try? JSONSerialization.jsonObject(with: data)) as? [String: Any]
                error = detail?["detail"] as? String ?? "Não foi possível analisar. Confira o texto (até 5.000 caracteres)."
                return
            }
            let value = try JSONDecoder().decode(Analysis.self, from: data)
            guard value.score_golpe.isFinite, (0...1).contains(value.score_golpe) else { throw URLError(.cannotParseResponse) }
            analysis = value; result = true
        } catch {
            self.error = "Não foi possível analisar a mensagem. Confira a conexão com a API e tente novamente."
        }
    }
    private var accent: Color { (overrideScheme ?? systemScheme) == .dark ? .orange : Color(red: 0.61, green: 0.30, blue: 0) }
    private let questions = [
        ("Eu conheço quem enviou?", "Confira o número ou endereço completo. Um nome conhecido e uma foto de perfil, sozinhos, não confirmam a identidade."),
        ("Estão me pressionando a agir agora?", "Pare por um momento. Pense se a ameaça, o prazo curto ou a promessa fazem sentido para a situação."),
        ("Pedem dinheiro, senha ou algum código?", "Antes de responder, confirme o pedido por outro canal que você já conhece e usa."),
        ("Consigo confirmar no canal oficial?", "Abra o aplicativo ou site oficial por conta própria e confira a informação, sem usar o link da mensagem.")
    ]

    private var riskColor: Color { analysis?.classe == 1
        ? Color(red: 201.0/255, green: 117.0/255, blue: 117.0/255)
        : Color(red: 98.0/255, green: 168.0/255, blue: 137.0/255) }

    private var dark: Bool { (overrideScheme ?? systemScheme) == .dark }
    private var pageColor: Color { dark ? Color(red: 0.063, green: 0.067, blue: 0.075) : Color(red: 0.969, green: 0.965, blue: 0.949) }
    private var panelColor: Color { dark ? Color(red: 0.106, green: 0.110, blue: 0.125) : .white }
    @ScaledMetric(relativeTo: .body) private var editorHeight = 160.0
    @FocusState private var editing: Bool

    // Resolve resources in the extension bundle, never in the sharing host's bundle.
    private func logo(_ name: String, label: String) -> some View {
        Group {
            if let url = Bundle(for: ShareViewController.self).url(forResource: name, withExtension: "png"),
               let image = UIImage(contentsOfFile: url.path) {
                Image(uiImage: image).renderingMode(.original).resizable().scaledToFit()
            } else {
                Text(label).font(.caption.bold()).foregroundColor(.primary)
            }
        }.accessibilityLabel(label)
    }

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Button("Fechar", action: close).frame(minHeight: 44)
                Spacer()
                Text("Projeto Sinapses").font(.headline).foregroundColor(.primary)
                Spacer()
                Button {
                    overrideScheme = dark ? .light : .dark
                } label: {
                    Image(systemName: dark ? "sun.max" : "moon")
                        .font(.system(size: 20)).frame(width: 64, height: 44)
                }.accessibilityLabel("Alternar tema")
            }
            .buttonStyle(.plain).foregroundColor(accent)
            .padding(.horizontal, 24).padding(.top, 8).padding(.bottom, 8)
            Divider().opacity(0.4)
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    HStack {
                        logo("eldorado", label: "Instituto Eldorado").frame(width: 116, height: 36)
                        Spacer(minLength: 20)
                        logo("logo-PUC-85-anos-color", label: "PUC-Campinas — 85 anos")
                            .frame(width: 90, height: 36).padding(8)
                    }.padding(.bottom, 4)
                    VStack(alignment: .leading, spacing: 12) {
                        Text(result ? "RESULTADO DA AVALIAÇÃO" : "TEXTO RECEBIDO")
                            .font(.caption.weight(.bold)).tracking(2).foregroundColor(accent)
                        Text(result ? "Qual é o risco?" : "Pronto para avaliar.")
                            .font(.system(.largeTitle, design: .default).weight(.bold))
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    if result {
                        resultView
                    } else if model.loading {
                        ProgressView("Recebendo texto…")
                    } else {
                        Text(model.text.isEmpty ? "Não foi possível receber um texto. Tente compartilhar uma seleção de texto de outro aplicativo." : "Confira o texto recebido e toque em avaliar.")
                            .font(.body).foregroundColor(.secondary)
                            .fixedSize(horizontal: false, vertical: true)
                        VStack(alignment: .leading, spacing: 10) {
                            Label("Mensagem recebida", systemImage: "tray.and.arrow.down")
                                .font(.caption).foregroundColor(.secondary)
                            messageEditor
                                .frame(height: editorHeight)
                                .focused($editing)
                                .disabled(analyzing)
                                .accessibilityLabel("Mensagem recebida")
                        }.padding(18).background(panelColor).cornerRadius(20)
                            .overlay(RoundedRectangle(cornerRadius: 20).stroke(Color.secondary.opacity(0.22), lineWidth: 1))
                        Button {
                            editing = false
                            Task { await analyze() }
                        } label: {
                            Label(analyzing ? "Avaliando…" : "Avaliar mensagem", systemImage: "sparkles")
                                .font(.body.weight(.semibold)).frame(maxWidth: .infinity).padding(16)
                        }
                        .buttonStyle(.plain)
                        .background(Color(red: 0.937, green: 0.573, blue: 0.180)).foregroundColor(.black).cornerRadius(16)
                        .disabled(analyzing || model.text.count > 5000 || model.text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                        if let error { Text(error).foregroundColor(.red) }
                    }
                }.padding(24).frame(maxWidth: 520).frame(maxWidth: .infinity)
            }
        }
        .background(pageColor.ignoresSafeArea())
        .tint(accent).preferredColorScheme(overrideScheme)
    }

    @ViewBuilder private var messageEditor: some View {
        if #available(iOS 16.0, *) {
            TextEditor(text: $model.text).font(.body).scrollContentBackground(.hidden)
        } else {
            TextEditor(text: $model.text).font(.body)
        }
    }

    private var resultView: some View {
        VStack(alignment: .leading, spacing: 24) {
            VStack(spacing: 24) {
                Text("CHANCE DE SER GOLPE").font(.caption.weight(.bold)).tracking(2).foregroundColor(accent)
                ZStack {
                    Circle().stroke(Color.secondary.opacity(0.2), lineWidth: 15)
                    Circle().trim(from: 0, to: progress).stroke(riskColor, style: StrokeStyle(lineWidth: 15, lineCap: .round)).rotationEffect(.degrees(-90))
                    VStack { Text(String(format: "%.1f%%", (analysis?.score_golpe ?? 0) * 100)).font(.system(size: 54, weight: .bold)); Text(analysis?.classe == 1 ? "possível golpe" : "menor risco indicado").foregroundColor(.secondary) }
                }.frame(width: 200, height: 200)
                    .accessibilityElement(children: .ignore).accessibilityLabel(String(format: "%.1f por cento de chance de golpe", (analysis?.score_golpe ?? 0) * 100))
                    .onAppear { withAnimation(.easeOut(duration: 1)) { progress = analysis?.score_golpe ?? 0 } }
                Text("Avaliação do modelo").fontWeight(.semibold).foregroundColor(accent)
                Text("A avaliação pode errar. Confira a mensagem e a identidade do remetente antes de agir.").font(.subheadline).foregroundColor(.secondary)
            }.padding(24).frame(maxWidth: .infinity).background(panelColor).cornerRadius(22)
            if let analysis {
                Text("Principais sinais identificados").font(.headline)
                ForEach(analysis.features_importantes, id: \.feature) { item in
                    Text("• " + item.feature.replacingOccurrences(of: "_", with: " "))
                }
                Text(analysis.explicacao_sinais ?? "Confira os sinais destacados e confirme o pedido por um canal conhecido.")
                    .font(.subheadline).foregroundColor(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
                if settings["SHOW_DIAGNOSTICS"] != "false" {
                    DisclosureGroup("Diagnóstico: todas as features") {
                        Text("Uso interno. 0 = não detectado; 1 = detectado. Carga emocional exibida por categoria; o modelo recebe 0/1/2.").font(.caption)
                        ForEach(analysis.diagnostic.keys.sorted(), id: \.self) { name in
                            HStack { Text(name).font(.caption); Spacer(); Text("\(analysis.diagnostic[name] ?? 0)").bold() }
                        }
                    }
                }
            }
            Text("Antes de confiar, pergunte:").font(.title2.bold())
            VStack(alignment: .leading, spacing: 18) {
                ForEach(questions.indices, id: \.self) { index in
                    DisclosureGroup(questions[index].0) { Text(questions[index].1).font(.subheadline).foregroundColor(.secondary).padding(.vertical, 10) }
                    if index < questions.count - 1 { Divider() }
                }
            }.padding(20).background(panelColor).cornerRadius(22)
            DisclosureGroup("Ver mensagem analisada") { Text(model.text).padding(.vertical, 12) }
            Button("Voltar à mensagem") { result = false; progress = 0 }
            Button(action: close) { Text("Finalizar").font(.body.weight(.semibold)).frame(maxWidth: .infinity).padding(16) }
                .background(Color.orange).foregroundColor(.black).cornerRadius(16)
        }
    }
}

private struct ImportantFeature: Decodable {
    let feature: String
}
private struct Analysis: Decodable {
    let score_golpe: Double
    let classe: Int
    let features_importantes: [ImportantFeature]
    let explicacao_sinais: String?
    let features_binarias: [String: Int]
    let features_clusters: [String: Int]
    var diagnostic: [String: Int] { features_binarias.merging(features_clusters) { first, _ in first } }
}
