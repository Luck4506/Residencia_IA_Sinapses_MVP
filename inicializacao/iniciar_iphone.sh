#!/bin/bash
# FINALIDADE: Abre o iPhone virtual, prepara a compilação fora do OneDrive e executa flutter run. Não inicia a API.
set -euo pipefail
PROTOTIPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
for ferramenta in flutter xcrun python3; do
  command -v "$ferramenta" >/dev/null || { echo "Instale/configure $ferramenta antes de continuar."; exit 1; }
done
SIMULADOR_ID="$(xcrun simctl list devices available -j | python3 "$PROTOTIPO_DIR/inicializacao/02_selecionar_iphone.py" "${1:-}")"
if ! xcrun simctl list devices booted -j | python3 -c 'import json,sys; ds=json.load(sys.stdin)["devices"]; sys.exit(not any(d["udid"]==sys.argv[1] for lista in ds.values() for d in lista))' "$SIMULADOR_ID"; then
  xcrun simctl boot "$SIMULADOR_ID"
fi
XCODE_DEVELOPER="$(xcode-select -p)"
if [[ -d "$XCODE_DEVELOPER/Applications/Simulator.app" ]]; then
  open "$XCODE_DEVELOPER/Applications/Simulator.app" --args -CurrentDeviceUDID "$SIMULADOR_ID"
elif [[ -d "$XCODE_DEVELOPER/../Applications/Simulator.app" ]]; then
  open "$XCODE_DEVELOPER/../Applications/Simulator.app" --args -CurrentDeviceUDID "$SIMULADOR_ID"
elif [[ -d "$XCODE_DEVELOPER/../Applications/DeviceHub.app" ]]; then
  open "$XCODE_DEVELOPER/../Applications/DeviceHub.app"
else
  open -a Simulator --args -CurrentDeviceUDID "$SIMULADOR_ID"
fi
xcrun simctl bootstatus "$SIMULADOR_ID" -b
cd "$PROTOTIPO_DIR/frontend"
# Frameworks assinados ficam fora do OneDrive para evitar metadados de sincronização.
mkdir -p build
if [[ ! -L build/ios || ! -d build/ios ]]; then
  IOS_TEMP="$(mktemp -d /private/tmp/prototipo-final-ios-XXXXXXXX)"
  if [[ -L build/ios ]]; then
    unlink build/ios
  elif [[ -d build/ios ]]; then
    mv build/ios "$IOS_TEMP/ios"
  fi
  mkdir -p "$IOS_TEMP/ios"
  ln -s "$IOS_TEMP/ios" build/ios
fi
flutter pub get
exec flutter run -d "$SIMULADOR_ID" --dart-define="API_URL=${API_URL:-http://127.0.0.1:8000}" --dart-define="SHOW_DIAGNOSTICS=${SHOW_DIAGNOSTICS:-true}"
