"""Compara a validação de vínculos em memória com as constraints do SQLite."""
from contextlib import closing
import sqlite3


def demonstrar():
    clientes_memoria = {1: "João"}
    vendas_memoria = []
    venda_valida = {"cliente_id": 1}

    if venda_valida["cliente_id"] not in clientes_memoria:
        raise ValueError("O cliente informado não existe.")
    vendas_memoria.append(venda_valida)
    print("Memória: venda com cliente válido aceita.")

    try:
        cliente_id = 999
        if cliente_id not in clientes_memoria:
            raise ValueError("O cliente informado não existe.")
        vendas_memoria.append({"cliente_id": cliente_id})
    except ValueError as erro:
        print(f"Memória: venda recusada: {erro}")

    try:
        if any(
            venda["cliente_id"] == 1
            for venda in vendas_memoria
        ):
            raise ValueError("Cliente possui vendas vinculadas.")
        del clientes_memoria[1]
    except ValueError as erro:
        print(f"Memória: exclusão recusada: {erro}")

    with closing(sqlite3.connect(":memory:")) as conexao:
        conexao.execute("PRAGMA foreign_keys = ON")
        conexao.execute(
            """
            CREATE TABLE clientes (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL
            )
            """
        )
        conexao.execute(
            """
            CREATE TABLE vendas (
                id INTEGER PRIMARY KEY,
                cliente_id INTEGER NOT NULL,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
                    ON DELETE RESTRICT
            )
            """
        )
        with conexao:
            conexao.execute(
                "INSERT INTO clientes (id, nome) VALUES (1, 'João')"
            )
            conexao.execute(
                "INSERT INTO vendas (id, cliente_id) VALUES (1, 1)"
            )
        print("SQLite: venda com cliente válido aceita.")

        try:
            with conexao:
                conexao.execute(
                    "INSERT INTO vendas (id, cliente_id) VALUES (2, 999)"
                )
        except sqlite3.IntegrityError as erro:
            print(f"SQLite: venda recusada: {erro}")

        try:
            with conexao:
                conexao.execute("DELETE FROM clientes WHERE id = 1")
        except sqlite3.IntegrityError as erro:
            print(f"SQLite: exclusão recusada: {erro}")


if __name__ == "__main__":
    demonstrar()
