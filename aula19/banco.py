"""Acesso ao banco SQLite de produtos, clientes e vendas."""
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
    """Cria as tabelas e importa produtos se ainda não houver registros."""
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
            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    telefone TEXT
                )
                """
            )
            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS vendas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_hora TEXT NOT NULL,
                    forma_pagamento TEXT NOT NULL,
                    total_centavos INTEGER NOT NULL,
                    cliente_id INTEGER
                )
                """
            )
            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS itens_venda (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venda_id INTEGER NOT NULL,
                    produto_codigo TEXT NOT NULL,
                    quantidade INTEGER NOT NULL,
                    preco_centavos INTEGER NOT NULL
                )
                """
            )
            total = conexao.execute(
                "SELECT COUNT(*) FROM produtos"
            ).fetchone()[0]
            if total == 0:
                _importar_catalogo_json(conexao, caminho_catalogo)


def _validar_itens_venda(itens):
    linhas = []
    for codigo, quantidade, preco_centavos in itens:
        if type(quantidade) is not int or quantidade <= 0:
            raise ValueError("A quantidade do item deve ser um inteiro positivo.")
        linhas.append(
            (
                _validar_codigo(codigo),
                quantidade,
                _validar_preco(preco_centavos),
            )
        )
    return linhas


def _inserir_itens_venda(conexao, venda_id, itens):
    existe = conexao.execute(
        "SELECT 1 FROM vendas WHERE id = ?",
        (venda_id,),
    ).fetchone()
    if existe is None:
        raise ValueError(f"A venda {venda_id} não existe.")

    conexao.executemany(
        """
        INSERT INTO itens_venda (
            venda_id, produto_codigo, quantidade, preco_centavos
        )
        VALUES (?, ?, ?, ?)
        """,
        [
            (venda_id, codigo, quantidade, preco_centavos)
            for codigo, quantidade, preco_centavos in itens
        ],
    )
    return len(itens)


def salvar_itens_venda(venda_id, itens, caminho=CAMINHO_BANCO):
    """Salva vários itens vinculados a uma venda existente e retorna a quantidade."""
    if type(venda_id) is not int or venda_id <= 0:
        raise ValueError("O ID da venda deve ser um inteiro positivo.")
    linhas_itens = _validar_itens_venda(itens)

    with closing(_conectar(caminho)) as conexao:
        with conexao:
            return _inserir_itens_venda(conexao, venda_id, linhas_itens)


def registrar_pedido(
    data_hora,
    forma_pagamento,
    total_centavos,
    cliente_id=None,
    itens=(),
    caminho=CAMINHO_BANCO,
    validar_catalogo=False,
):
    """Registra venda e itens na mesma transação e retorna o ID.

    Cada item deve ser uma tupla (produto_codigo, quantidade, preco_centavos).
    """
    if not isinstance(data_hora, str) or not data_hora.strip():
        raise ValueError("A data e hora da venda não podem ser vazias.")
    if not isinstance(forma_pagamento, str) or not forma_pagamento.strip():
        raise ValueError("A forma de pagamento não pode ser vazia.")
    if type(total_centavos) is not int or total_centavos < 0:
        raise ValueError("O total deve ser um inteiro não negativo em centavos.")
    if cliente_id is not None:
        cliente_id = _validar_id_cliente(cliente_id)
    linhas_itens = _validar_itens_venda(itens)

    with closing(_conectar(caminho)) as conexao:
        with conexao:
            if validar_catalogo:
                for codigo, _, preco_centavos in linhas_itens:
                    produto_atual = conexao.execute(
                        "SELECT preco_centavos FROM produtos WHERE codigo = ?",
                        (codigo,),
                    ).fetchone()
                    if (
                        produto_atual is None
                        or produto_atual[0] != preco_centavos
                    ):
                        raise ValueError(
                            "O catálogo foi alterado durante a confirmação. "
                            f"Revise o produto {codigo} antes de tentar novamente."
                        )

            cursor = conexao.execute(
                """
                INSERT INTO vendas (
                    data_hora, forma_pagamento, total_centavos, cliente_id
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    data_hora.strip(),
                    forma_pagamento.strip(),
                    total_centavos,
                    cliente_id,
                ),
            )
            venda_id = cursor.lastrowid
            _inserir_itens_venda(conexao, venda_id, linhas_itens)
            return venda_id


def salvar_venda(
    data_hora,
    forma_pagamento,
    total_centavos,
    cliente_id=None,
    itens=(),
    caminho=CAMINHO_BANCO,
):
    """Compatibilidade com o nome anterior; registra venda e itens atomicamente."""
    return registrar_pedido(
        data_hora,
        forma_pagamento,
        total_centavos,
        cliente_id,
        itens,
        caminho,
    )


def listar_vendas(caminho=CAMINHO_BANCO):
    """Retorna vendas como tuplas (id, data_hora, forma, total, cliente_id)."""
    with closing(_conectar(caminho)) as conexao:
        cursor = conexao.execute(
            """
            SELECT id, data_hora, forma_pagamento, total_centavos, cliente_id
            FROM vendas
            ORDER BY id
            """
        )
        return cursor.fetchall()


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


def _validar_id_cliente(cliente_id):
    if type(cliente_id) is not int or cliente_id <= 0:
        raise ValueError("O ID do cliente deve ser um inteiro positivo.")
    return cliente_id


def _validar_nome_cliente(nome):
    if not isinstance(nome, str) or not nome.strip():
        raise ValueError("O nome do cliente não pode ser vazio.")
    return nome.strip()


def _validar_telefone(telefone):
    if telefone is None:
        return None
    if not isinstance(telefone, str):
        raise ValueError("O telefone deve ser informado como texto.")
    telefone = telefone.strip()
    return telefone or None


def listar_clientes(caminho=CAMINHO_BANCO):
    """Retorna clientes como tuplas (id, nome, telefone)."""
    with closing(_conectar(caminho)) as conexao:
        cursor = conexao.execute(
            "SELECT id, nome, telefone FROM clientes ORDER BY nome, id"
        )
        return cursor.fetchall()


def salvar_cliente(nome, telefone=None, caminho=CAMINHO_BANCO):
    """Insere cliente e retorna o ID gerado pelo SQLite."""
    valores = (_validar_nome_cliente(nome), _validar_telefone(telefone))
    with closing(_conectar(caminho)) as conexao:
        with conexao:
            cursor = conexao.execute(
                "INSERT INTO clientes (nome, telefone) VALUES (?, ?)",
                valores,
            )
            return cursor.lastrowid


def atualizar_cliente(cliente_id, nome, telefone=None, caminho=CAMINHO_BANCO):
    """Atualiza cliente pelo ID; retorna False se não existir."""
    valores = (
        _validar_nome_cliente(nome),
        _validar_telefone(telefone),
        _validar_id_cliente(cliente_id),
    )
    with closing(_conectar(caminho)) as conexao:
        with conexao:
            cursor = conexao.execute(
                "UPDATE clientes SET nome = ?, telefone = ? WHERE id = ?",
                valores,
            )
            return cursor.rowcount > 0


def remover_cliente(cliente_id, caminho=CAMINHO_BANCO):
    """Remove cliente pelo ID; retorna False se não existir."""
    cliente_id = _validar_id_cliente(cliente_id)
    with closing(_conectar(caminho)) as conexao:
        with conexao:
            cursor = conexao.execute(
                "DELETE FROM clientes WHERE id = ?",
                (cliente_id,),
            )
            return cursor.rowcount > 0
