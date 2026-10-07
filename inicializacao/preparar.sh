#!/usr/bin/env bash
set -euo pipefail
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"
"${PYTHON:-python3}" -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
backend/.venv/bin/python inicializacao/preparar_modelos.py
PYTHONPATH=backend backend/.venv/bin/python -c 'from extrator_features.bibliotecas.apoio_03_gramatica import Corretor; c = Corretor(); c.detectar_erros("Teste de inicialização."); c.close()'
cd frontend
flutter pub get
