// FINALIDADE: Suporte nativo de inicialização e janela da plataforma linux. Não executa os modelos Python.
// FLUXO: suporte ao frontend; os modelos de IA pertencem à API Python.
#include "my_application.h"

int main(int argc, char** argv) {
  g_autoptr(MyApplication) app = my_application_new();
  return g_application_run(G_APPLICATION(app), argc, argv);
}
