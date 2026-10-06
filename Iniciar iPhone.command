#!/bin/bash
# FINALIDADE: Atalho opcional do Finder: chama o lançador Flutter e exibe falhas.
cd "$(dirname "$0")"
bash inicializacao/iniciar_iphone.sh "$@"
resultado=$?
if [[ $resultado -ne 0 ]]; then
  echo "Não foi possível iniciar. Confira o erro acima."
  read -r -p "Pressione Enter para fechar."
fi
exit "$resultado"
