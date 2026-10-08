#!/usr/bin/env bash
# FINALIDADE: Inicia o servidor FastAPI; os demais módulos Python são carregados por ele.
set -euo pipefail
PROTOTIPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_API="${PYTHON_API:-$PROTOTIPO_DIR/backend/.venv/bin/python}"
if [[ ! -x "$PYTHON_API" ]]; then
  echo 'Crie o ambiente backend/.venv e instale backend/requirements.txt, conforme o README.'
  exit 1
fi
cd "$PROTOTIPO_DIR/backend"
echo "Carregando dependências da API…"
exec "$PYTHON_API" -u -m uvicorn api.main:app --host "${API_HOST:-127.0.0.1}" --port "${API_PORT:-8000}" "$@"
