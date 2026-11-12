"""Acesso ao banco SQLite de produtos da aula 14."""
import sqlite3
from contextlib import closing
from pathlib import Path

from arquivos import ler_catalogo, validar_catalogo


CAMINHO_BANCO = Path(__file__).with_name("produtos.db")
CAMINHO_CATALOGO = Path(__file__).with_name("catalogo.json")


def _conectar(caminho):
    return sqlite3.connect(caminho)


def _validar_codigo(codigo):
    if not isinstance(codigo, str) or not codigo.strip():
        raise ValueError("O código do produto não pode ser vazio.")
    return codigo.strip()


def _validar_nome(nome):
    if not isinstance(nome, str) or not nome.strip():
        raise ValueError("O nome do produto não pode ser vazio.")
    return nome.strip()


def _validar_preco(preco_centavos):
    if type(preco_centavos) is not int or preco_centavos <= 0:
        raise ValueError("O preço deve ser um inteiro positivo em centavos.")
    return preco_centavos


def _salvar_produto(conexao, codigo, nome, preco_centavos):
    conexao.execute(
        """
        INSERT INTO produtos (codigo, nome, preco_centavos)
        VALUES (?, ?, ?)
        """,
        (_validar_codigo(codigo), _validar_nome(nome), _validar_preco(preco_centavos)),
    )


def _atualizar_produto(conexao, codigo, nome, preco_centavos):
    cursor = conexao.execute(
        """
        UPDATE produtos
        SET nome = ?, preco_centavos = ?
        WHERE codigo = ?
        """,
        (
            _validar_nome(nome),
            _validar_preco(preco_centavos),
            _validar_codigo(codigo),
        ),
    )
    return cursor.rowcount > 0


def _remover_produto(conexao, codigo):
    cursor = conexao.execute(
        "DELETE FROM produtos WHERE codigo = ?",
        (_validar_codigo(codigo),),
    )
    return cursor.rowcount > 0


def _importar_catalogo_json(conexao, caminho_catalogo):
    produtos = ler_catalogo(caminho_catalogo)
    if produtos is None:
        return 0

    linhas = [
        (
            _validar_codigo(str(produto["id"])),
            _validar_nome(produto["nome"]),
            _validar_preco(produto["preco_centavos"]),
        )
        for produto in produtos
    ]
    conexao.executemany(
        """
        INSERT INTO produtos (codigo, nome, preco_centavos)
        VALUES (?, ?, ?)
        """,
        linhas,
    )
    return len(linhas)


def criar_banco(caminho=CAMINHO_BANCO, caminho_catalogo=CAMINHO_CATALOGO):
    """Cria a tabela e importa o catálogo JSON se ainda não houver produtos."""
    with closing(_conectar(caminho)) as conexao:
        with conexao:
            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS produtos (
                    codigo TEXT PRIMARY KEY,
                    nome TEXT NOT NULL,
                    preco_centavos INTEGER NOT NULL
                )
                """
            )
            total = conexao.execute(
                "SELECT COUNT(*) FROM produtos"
            ).fetchone()[0]
            if total == 0:
                _importar_catalogo_json(conexao, caminho_catalogo)


def listar_produtos(caminho=CAMINHO_BANCO):
    """Retorna produtos como tuplas (codigo, nome, preco_centavos)."""
    with closing(_conectar(caminho)) as conexao:
        cursor = conexao.execute(
            """
            SELECT codigo, nome, preco_centavos
            FROM produtos
            ORDER BY codigo
            """
        )
        return cursor.fetchall()


def salvar_produto(codigo, nome, preco_centavos, caminho=CAMINHO_BANCO):
    """Insere um produto; códigos repetidos geram sqlite3.IntegrityError."""
    with closing(_conectar(caminho)) as conexao:
        with conexao:
            _salvar_produto(conexao, codigo, nome, preco_centavos)


def atualizar_produto(codigo, nome, preco_centavos, caminho=CAMINHO_BANCO):
    """Atualiza nome e preço; retorna False quando o código não existe."""
    with closing(_conectar(caminho)) as conexao:
        with conexao:
            return _atualizar_produto(conexao, codigo, nome, preco_centavos)


def remover_produto(codigo, caminho=CAMINHO_BANCO):
    """Remove o produto pelo código; retorna False quando não existe."""
    with closing(_conectar(caminho)) as conexao:
        with conexao:
            return _remover_produto(conexao, codigo)


def sincronizar_produtos(produtos, caminho=CAMINHO_BANCO):
    """Sincroniza a lista editada com o banco em uma única transação."""
    validar_catalogo(produtos)
    desejados = {
        _validar_codigo(str(produto["id"])): (
            _validar_nome(produto["nome"]),
            _validar_preco(produto["preco_centavos"]),
        )
        for produto in produtos
    }

    resultado = {"inseridos": 0, "atualizados": 0, "removidos": 0}
    with closing(_conectar(caminho)) as conexao:
        with conexao:
            atuais = {
                codigo: (nome, preco)
                for codigo, nome, preco in conexao.execute(
                    "SELECT codigo, nome, preco_centavos FROM produtos"
                )
            }

            for codigo, (nome, preco) in desejados.items():
                if codigo not in atuais:
                    _salvar_produto(conexao, codigo, nome, preco)
                    resultado["inseridos"] += 1
                elif atuais[codigo] != (nome, preco):
                    _atualizar_produto(conexao, codigo, nome, preco)
                    resultado["atualizados"] += 1

            for codigo in atuais.keys() - desejados.keys():
                _remover_produto(conexao, codigo)
                resultado["removidos"] += 1

    return resultado
