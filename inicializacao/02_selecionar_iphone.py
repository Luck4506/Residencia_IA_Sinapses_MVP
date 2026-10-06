# FINALIDADE: Recebe o inventário JSON do Xcode e devolve o UUID do iPhone escolhido.
"""Seleciona um iPhone disponível a partir do JSON de simctl."""
import json
import re
import sys

pedido = sys.argv[1] if len(sys.argv) > 1 else ""
dados = json.load(sys.stdin)
candidatos = []
for runtime, dispositivos in dados["devices"].items():
    if ".iOS-" not in runtime:
        continue
    versao = tuple(map(int, re.findall(r"\d+", runtime.split("iOS-")[1])))
    for d in dispositivos:
        if d.get("isAvailable") and d["name"].startswith("iPhone"):
            if not pedido or pedido in (d["udid"], d["name"]):
                candidatos.append((d["state"] == "Booted", versao, d["name"], d))
if not candidatos:
    sys.exit("Nenhum iPhone compatível encontrado. Instale um simulador no Xcode ou confira o nome/UUID informado.")
d = sorted(candidatos, key=lambda x: x[:3], reverse=True)[0][3]
print(d["udid"])
