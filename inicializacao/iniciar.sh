#!/usr/bin/env bash
# Inicia API + interface. Fechar com Ctrl+C encerra os dois processos.
set -euo pipefail
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Escolhe uma porta livre; API_PORT explícita deve estar disponível.
PORTA="$("$RAIZ/backend/.venv/bin/python" - "${API_PORT:-}" <<'PYPORT'
import socket, sys
requested = sys.argv[1]
ports = [int(requested)] if requested else range(8000, 8011)
for port in ports:
    with socket.socket() as s:
        try:
            s.bind(('127.0.0.1', port))
        except OSError:
            continue
        print(port)
        break
else:
    raise SystemExit('Nenhuma porta disponível. Informe uma porta livre em API_PORT.')
PYPORT
)"
export API_PORT="$PORTA"
"$RAIZ/inicializacao/iniciar_api.sh" &
API_PID=$!
trap 'kill "$API_PID" 2>/dev/null || true' EXIT
trap 'exit 130' INT TERM
"$RAIZ/backend/.venv/bin/python" - "$PORTA" "$API_PID" <<'PY'
import json, sys, time, urllib.request, os
port, pid = sys.argv[1], int(sys.argv[2])
for _ in range(180):
    os.kill(pid, 0)
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/saude', timeout=2) as r:
            status = json.load(r)
        if not status['classificacao_disponivel']:
            raise SystemExit('API indisponível: ' + '; '.join(status['pendencias']))
        break
    except (OSError, ValueError):
        time.sleep(1)
else:
    raise SystemExit('A API não iniciou em três minutos. Confira o terminal.')
PY
export API_URL="${API_URL:-http://127.0.0.1:$PORTA}"
if [[ "${1:-web}" == iphone ]]; then
  "$RAIZ/inicializacao/iniciar_iphone.sh" "${2:-}"
else
  cd "$RAIZ/frontend"
  echo 'Abra http://localhost:8080 no navegador.'
  flutter run -d web-server --web-hostname 127.0.0.1 --web-port 8080 --dart-define="API_URL=$API_URL" --dart-define="SHOW_DIAGNOSTICS=${SHOW_DIAGNOSTICS:-true}"
fi
