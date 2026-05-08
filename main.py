"""Entrypoint local para executar o jogo sem instalar o pacote."""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def run() -> None:
    """Importa o módulo principal do jogo e inicia a execução."""
    from game import main

    main()


if __name__ == "__main__":
    run()
