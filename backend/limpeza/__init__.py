# FINALIDADE: Expor as funções de limpeza, abreviações e anonimização do pacote.
# EXECUÇÃO: Importe as funções; não inicia a API nem transforma mensagens sozinho.
from .etapa_01_limpeza import limpar_mensagem
from .etapa_02_abreviacoes import normalizar_abreviacoes
from .etapa_03_anonimizacao import anonimizar_mensagem

__all__ = ["limpar_mensagem", "normalizar_abreviacoes", "anonimizar_mensagem"]
