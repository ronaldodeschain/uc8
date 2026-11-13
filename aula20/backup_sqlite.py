"""Cria uma cópia consistente do banco SQLite da aula 19."""
import argparse
import sqlite3
from contextlib import closing
from pathlib import Path


def criar_backup(origem, destino):
    """Copia um banco SQLite existente sem sobrescrever arquivos."""
    caminho_origem = Path(origem).expanduser().resolve(strict=True)
    if not caminho_origem.is_file():
        raise ValueError(f"A origem não é um arquivo: {caminho_origem}")

    caminho_destino = Path(destino).expanduser().resolve()
    if caminho_origem == caminho_destino:
        raise ValueError("Origem e destino devem ser arquivos diferentes.")
    if caminho_destino.exists():
        raise FileExistsError(f"O destino já existe: {caminho_destino}")

    with caminho_destino.open("xb"):
        pass

    try:
        with closing(sqlite3.connect(caminho_origem)) as conexao_origem:
            with closing(sqlite3.connect(caminho_destino)) as conexao_destino:
                conexao_origem.backup(conexao_destino)
    except (OSError, sqlite3.Error):
        caminho_destino.unlink()
        raise

    return caminho_destino


def main():
    parser = argparse.ArgumentParser(
        description="Copia um banco SQLite sem sobrescrever o destino."
    )
    parser.add_argument(
        "origem",
        nargs="?",
        type=Path,
        default=Path(__file__).with_name("produtos.db"),
        help="banco de origem (padrão: produtos.db ao lado do script)",
    )
    parser.add_argument(
        "destino",
        nargs="?",
        type=Path,
        default=Path(__file__).with_name("backup.db"),
        help="novo arquivo de backup (padrão: backup.db ao lado do script)",
    )
    argumentos = parser.parse_args()

    try:
        caminho_backup = criar_backup(argumentos.origem, argumentos.destino)
    except (OSError, sqlite3.Error, ValueError) as erro:
        parser.error(str(erro))

    print(f"Backup criado: {caminho_backup}")


if __name__ == "__main__":
    main()
