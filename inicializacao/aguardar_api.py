"""Espera a API local, com progresso e cancelamento legíveis."""
import json
import os
import signal
import sys
import time
import urllib.error
import urllib.request


def cancelar(*_):
    print('\nInicialização cancelada.', flush=True)
    raise SystemExit(130)


def aguardar(porta, pid, timeout=180):
    inicio = time.monotonic()
    proximo_aviso = inicio
    while time.monotonic() - inicio < timeout:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            raise SystemExit('A API encerrou antes de iniciar. Confira o erro exibido acima.') from None
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{porta}/saude', timeout=2) as resposta:
                status = json.load(resposta)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            agora = time.monotonic()
            if agora >= proximo_aviso:
                print(f'Aguardando a API carregar modelos e corretor gramatical… {int(agora - inicio)}s', flush=True)
                proximo_aviso = agora + 10
            time.sleep(1)
            continue
        if not status.get('classificacao_disponivel'):
            pendencias = '; '.join(status.get('pendencias', []))
            raise SystemExit(f'API indisponível: {pendencias or "modelos ainda não disponíveis"}')
        print(f'API pronta em http://127.0.0.1:{porta}. Abrindo o aplicativo…', flush=True)
        return
    raise SystemExit('A API não iniciou em três minutos. Confira os erros exibidos acima.')


if __name__ == '__main__':
    signal.signal(signal.SIGINT, cancelar)
    signal.signal(signal.SIGTERM, cancelar)
    aguardar(int(sys.argv[1]), int(sys.argv[2]))
