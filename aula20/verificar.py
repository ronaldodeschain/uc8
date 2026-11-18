"""Testes sem interface para CSV e sessões de perfil."""
import csv
import sqlite3
from contextlib import closing, redirect_stdout
from datetime import datetime
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from banco import (
    _conectar,
    atualizar_produto,
    atualizar_cliente,
    criar_banco,
    listar_clientes,
    listar_produtos,
    listar_vendas,
    remover_cliente,
    remover_produto,
    registrar_pedido,
    salvar_cliente,
    salvar_itens_venda,
    salvar_produto,
    sincronizar_produtos,
)
from modelos import Comprovante, Pedido, Produto
from perfis import SessaoDemo
from memoria import ProdutosMemoria
from controller import ProdutoController
from repositorio import ProdutosSQLite
from relatorios import exportar_csv, registrar_venda_csv
from relacoes_sqlite import demonstrar as demonstrar_relacoes_sqlite
from main import (
    _registrar_pedido_no_banco,
    _remover_produto_se_confirmado,
)
from pagamento import calcular_pagamento, preco_para_centavos
from backup_sqlite import criar_backup
from vinculos import (
    clientes as clientes_vinculo,
    pode_excluir_aluno,
    validar_vinculos,
    vinculo_valido,
)


def produto_existe(codigo, caminho):
    with closing(sqlite3.connect(caminho)) as conexao:
        linha = conexao.execute(
            "SELECT 1 FROM produtos WHERE codigo = ?",
            (codigo,),
        ).fetchone()
    return linha is not None


def verificar_pagamento():
    assert calcular_pagamento("13.00", "PIX") == (1131, 169)
    assert calcular_pagamento("100", "Crédito 1x") == (10000, 0)
    assert preco_para_centavos("12,34") == 1234

    try:
        calcular_pagamento("13.00", "Cartão desconhecido")
    except ValueError:
        pass
    else:
        raise AssertionError("Forma de pagamento desconhecida deveria ser rejeitada.")


def verificar_remocao_item_pedido():
    pedido = Pedido()
    pedido.adicionar(Produto("P01", "Pizza", 5000), "1")
    pedido.adicionar(Produto("P02", "Suco", 800), "2")
    pedido.adicionar(Produto("P03", "Doce", 300), "1")

    pedido.remover("P02")
    assert [
        (item.produto.codigo, item.quantidade)
        for item in pedido.itens
    ] == [("P01", 1), ("P03", 1)]
    assert pedido.total_centavos() == 5300

    pedido.remover("P01")
    assert [
        (item.produto.codigo, item.quantidade)
        for item in pedido.itens
    ] == [("P03", 1)]

    pedido.remover("P03")
    assert pedido.itens == []
    assert pedido.total_centavos() == 0

    pedido_antigo = Pedido()
    pedido_antigo.adicionar(Produto("P10", "Café", 450), "1")
    pedido_antigo.remover("P10")
    assert pedido_antigo.itens == []
    assert pedido_antigo.total_centavos() == 0


def verificar_persistencia_sqlite():
    with TemporaryDirectory() as diretorio:
        caminho_banco = Path(diretorio) / "teste_produtos.db"
        caminho_catalogo = Path(diretorio) / "catalogo_inexistente.json"
        criar_banco(caminho_banco, caminho_catalogo)

        salvar_produto("P99", "Pizza Especial", 5990, caminho_banco)
        assert produto_existe("P99", caminho_banco)
        assert listar_produtos(caminho_banco) == [
            ("P99", "Pizza Especial", 5990)
        ]

        assert atualizar_produto(
            "P99", "Pizza Especial", 6490, caminho_banco
        )
        produto = next(
            item for item in listar_produtos(caminho_banco) if item[0] == "P99"
        )
        assert produto[2] == 6490

        with closing(sqlite3.connect(caminho_banco)) as conexao:
            assert conexao.execute(
                "SELECT preco_centavos FROM produtos WHERE codigo = ?",
                ("P99",),
            ).fetchone() == (6490,)

        # A consulta seguinte abre uma conexão nova, como após reabrir o programa.
        assert produto_existe("P99", caminho_banco)
        assert listar_produtos(caminho_banco) == [
            ("P99", "Pizza Especial", 6490)
        ]

        assert remover_produto("P99", caminho_banco)
        assert not produto_existe("P99", caminho_banco)
        assert listar_produtos(caminho_banco) == []


def verificar_chaves_estrangeiras():
    with TemporaryDirectory() as diretorio:
        caminho_banco = Path(diretorio) / "vinculos.db"
        with closing(_conectar(caminho_banco)) as conexao:
            assert conexao.execute("PRAGMA foreign_keys").fetchone() == (1,)
            conexao.execute(
                "CREATE TABLE alunos (id INTEGER PRIMARY KEY)"
            )
            conexao.execute(
                """
                CREATE TABLE matriculas (
                    id INTEGER PRIMARY KEY,
                    aluno_id INTEGER NOT NULL,
                    FOREIGN KEY (aluno_id) REFERENCES alunos(id)
                        ON DELETE RESTRICT
                )
                """
            )
            with conexao:
                conexao.execute("INSERT INTO alunos (id) VALUES (1)")
                conexao.execute(
                    "INSERT INTO matriculas (id, aluno_id) VALUES (1, 1)"
                )

            try:
                with conexao:
                    conexao.execute(
                        "INSERT INTO matriculas (id, aluno_id) VALUES (2, 99)"
                    )
            except sqlite3.IntegrityError:
                pass
            else:
                raise AssertionError(
                    "Uma matrícula com referência inexistente deveria ser recusada."
                )

            try:
                with conexao:
                    conexao.execute("DELETE FROM alunos WHERE id = 1")
            except sqlite3.IntegrityError:
                pass
            else:
                raise AssertionError(
                    "A exclusão de aluno vinculado deveria ser bloqueada."
                )

            assert conexao.execute(
                "SELECT id FROM alunos"
            ).fetchall() == [(1,)]
            assert conexao.execute(
                "SELECT aluno_id FROM matriculas"
            ).fetchall() == [(1,)]


def verificar_backup_sqlite():
    with TemporaryDirectory() as diretorio:
        caminho_origem = Path(diretorio) / "pizzaria.db"
        caminho_backup = Path(diretorio) / "backup.db"
        caminho_catalogo = Path(diretorio) / "catalogo_inexistente.json"
        criar_banco(caminho_origem, caminho_catalogo)
        salvar_produto("P99", "Pizza de teste", 5000, caminho_origem)

        assert criar_backup(caminho_origem, caminho_backup) == caminho_backup.resolve()
        assert caminho_backup.is_file()
        assert listar_produtos(caminho_origem) == [
            ("P99", "Pizza de teste", 5000)
        ]
        assert listar_produtos(caminho_backup) == [
            ("P99", "Pizza de teste", 5000)
        ]

        try:
            criar_backup(caminho_origem, caminho_backup)
        except FileExistsError:
            pass
        else:
            raise AssertionError("Backup existente não deveria ser sobrescrito.")

        assert listar_produtos(caminho_origem) == [
            ("P99", "Pizza de teste", 5000)
        ]


def verificar_crud_clientes():
    with TemporaryDirectory() as diretorio:
        caminho_banco = Path(diretorio) / "teste_clientes.db"
        caminho_catalogo = Path(diretorio) / "catalogo_inexistente.json"
        criar_banco(caminho_banco, caminho_catalogo)

        cliente_id = salvar_cliente(
            "João Silva",
            "51999999999",
            caminho_banco,
        )
        assert isinstance(cliente_id, int) and cliente_id > 0
        assert listar_clientes(caminho_banco) == [
            (cliente_id, "João Silva", "51999999999")
        ]

        assert atualizar_cliente(
            cliente_id,
            "João Atualizado",
            "51888888888",
            caminho_banco,
        )
        assert listar_clientes(caminho_banco) == [
            (cliente_id, "João Atualizado", "51888888888")
        ]

        assert remover_cliente(cliente_id, caminho_banco)
        assert listar_clientes(caminho_banco) == []
        assert not remover_cliente(cliente_id, caminho_banco)

        cliente_sem_telefone = salvar_cliente(
            "Maria",
            caminho=caminho_banco,
        )
        assert listar_clientes(caminho_banco) == [
            (cliente_sem_telefone, "Maria", None)
        ]

        for nome in ("", "   "):
            try:
                salvar_cliente(nome, caminho=caminho_banco)
            except ValueError:
                pass
            else:
                raise AssertionError("Nome vazio de cliente deveria ser rejeitado.")


def verificar_cliente_inexistente():
    with TemporaryDirectory() as diretorio:
        caminho_banco = Path(diretorio) / "clientes_legado.db"
        with closing(sqlite3.connect(caminho_banco)) as conexao:
            with conexao:
                conexao.execute(
                    """
                    CREATE TABLE clientes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        telefone TEXT
                    )
                    """
                )
                conexao.execute(
                    """
                    CREATE TABLE vendas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_hora TEXT NOT NULL,
                        forma_pagamento TEXT NOT NULL,
                        total_centavos INTEGER NOT NULL,
                        cliente_id INTEGER
                    )
                    """
                )
                conexao.execute(
                    "INSERT INTO clientes (id, nome) VALUES (1, 'Cliente válido')"
                )
                conexao.execute(
                    """
                    INSERT INTO vendas (
                        id, data_hora, forma_pagamento, total_centavos, cliente_id
                    )
                    VALUES (1, '2026-11-18 10:00:00', 'PIX', 1000, 1)
                    """
                )

        criar_banco(
            caminho_banco,
            Path(diretorio) / "catalogo_inexistente.json",
        )
        with closing(_conectar(caminho_banco)) as conexao:
            assert conexao.execute(
                "PRAGMA foreign_key_list(vendas)"
            ).fetchall()[0][6] == "RESTRICT"
            assert conexao.execute(
                "SELECT id, cliente_id FROM vendas"
            ).fetchall() == [(1, 1)]
        assert atualizar_cliente(
            1,
            "João Silva",
            caminho=caminho_banco,
        ) is True
        with closing(_conectar(caminho_banco)) as conexao:
            assert conexao.execute(
                """
                SELECT vendas.cliente_id, clientes.nome
                FROM vendas JOIN clientes ON clientes.id = vendas.cliente_id
                """
            ).fetchall() == [(1, "João Silva")]
            assert conexao.execute("PRAGMA foreign_key_check").fetchall() == []

        erro_ocorreu = False
        try:
            remover_cliente(1, caminho_banco)
        except ValueError as erro:
            assert str(erro) == "Cliente possui vendas vinculadas."
            erro_ocorreu = True
        else:
            raise AssertionError("Cliente vinculado deveria ter exclusão recusada.")
        assert erro_ocorreu is True
        assert listar_clientes(caminho_banco) == [
            (1, "João Silva", None)
        ]

        try:
            registrar_pedido(
                "2026-11-18 10:01:00",
                "PIX",
                1000,
                cliente_id=999,
                caminho=caminho_banco,
            )
        except sqlite3.IntegrityError as erro:
            assert str(erro) == "O cliente informado não existe."
        else:
            raise AssertionError("Venda com cliente inexistente deveria ser recusada.")

        assert listar_vendas(caminho_banco) == [
            (1, "2026-11-18 10:00:00", "PIX", 1000, 1)
        ]


def verificar_migracao_orfa_preservada():
    with TemporaryDirectory() as diretorio:
        caminho_banco = Path(diretorio) / "vendas_orfas.db"
        with closing(sqlite3.connect(caminho_banco)) as conexao:
            with conexao:
                conexao.execute(
                    """
                    CREATE TABLE clientes (
                        id INTEGER PRIMARY KEY,
                        nome TEXT NOT NULL,
                        telefone TEXT
                    )
                    """
                )
                conexao.execute(
                    """
                    CREATE TABLE vendas (
                        id INTEGER PRIMARY KEY,
                        data_hora TEXT NOT NULL,
                        forma_pagamento TEXT NOT NULL,
                        total_centavos INTEGER NOT NULL,
                        cliente_id INTEGER
                    )
                    """
                )
                conexao.execute(
                    """
                    INSERT INTO vendas
                    VALUES (1, '2026-11-18 10:00:00', 'PIX', 1000, 999)
                    """
                )

        try:
            criar_banco(
                caminho_banco,
                Path(diretorio) / "catalogo_inexistente.json",
            )
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("A migração deveria recusar venda órfã existente.")

        with closing(sqlite3.connect(caminho_banco)) as conexao:
            tabelas = {
                linha[0]
                for linha in conexao.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            assert "vendas_com_fk" not in tabelas
            assert conexao.execute(
                "SELECT id, cliente_id FROM vendas"
            ).fetchall() == [(1, 999)]
            assert conexao.execute(
                "PRAGMA foreign_key_list(vendas)"
            ).fetchall() == []


def verificar_produto_inexistente():
    with TemporaryDirectory() as diretorio:
        caminho_banco = Path(diretorio) / "itens_legado.db"
        with closing(sqlite3.connect(caminho_banco)) as conexao:
            with conexao:
                conexao.execute(
                    """
                    CREATE TABLE produtos (
                        codigo TEXT PRIMARY KEY,
                        nome TEXT NOT NULL,
                        preco_centavos INTEGER NOT NULL
                    )
                    """
                )
                conexao.execute(
                    """
                    CREATE TABLE clientes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        telefone TEXT
                    )
                    """
                )
                conexao.execute(
                    """
                    CREATE TABLE vendas (
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
                    CREATE TABLE itens_venda (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        venda_id INTEGER NOT NULL,
                        produto_codigo TEXT NOT NULL,
                        quantidade INTEGER NOT NULL,
                        preco_centavos INTEGER NOT NULL
                    )
                    """
                )
                conexao.execute(
                    "INSERT INTO produtos VALUES ('P01', 'Produto válido', 100)"
                )
                conexao.execute(
                    """
                    INSERT INTO vendas (
                        id, data_hora, forma_pagamento, total_centavos
                    )
                    VALUES (1, '2026-11-18 10:00:00', 'PIX', 100)
                    """
                )
                conexao.execute(
                    """
                    INSERT INTO itens_venda (
                        id, venda_id, produto_codigo, quantidade, preco_centavos
                    )
                    VALUES (1, 1, 'P01', 1, 100)
                    """
                )

        criar_banco(
            caminho_banco,
            Path(diretorio) / "catalogo_inexistente.json",
        )
        with closing(_conectar(caminho_banco)) as conexao:
            chave_estrangeira = conexao.execute(
                "PRAGMA foreign_key_list(itens_venda)"
            ).fetchall()[0]
            assert chave_estrangeira[2:5] == (
                "produtos",
                "produto_codigo",
                "codigo",
            )
            assert chave_estrangeira[6] == "RESTRICT"
            assert conexao.execute(
                "SELECT id, venda_id, produto_codigo FROM itens_venda"
            ).fetchall() == [(1, 1, "P01")]
        assert atualizar_produto(
            "P01",
            "Produto renomeado",
            100,
            caminho_banco,
        ) is True
        with closing(_conectar(caminho_banco)) as conexao:
            assert conexao.execute(
                """
                SELECT itens_venda.produto_codigo, produtos.nome
                FROM itens_venda
                JOIN produtos ON produtos.codigo = itens_venda.produto_codigo
                """
            ).fetchall() == [("P01", "Produto renomeado")]
            assert conexao.execute("PRAGMA foreign_key_check").fetchall() == []

        for remover in (
            lambda: remover_produto("P01", caminho_banco),
            lambda: sincronizar_produtos(
                [{"id": "P02", "nome": "Produto substituto", "preco_centavos": 100}],
                caminho_banco,
            ),
        ):
            erro_ocorreu = False
            try:
                remover()
            except ValueError as erro:
                assert str(erro) == "Produto possui itens de venda vinculados."
                erro_ocorreu = True
            else:
                raise AssertionError("Produto vinculado deveria ter exclusão recusada.")
            assert erro_ocorreu is True

        assert listar_produtos(caminho_banco) == [
            ("P01", "Produto renomeado", 100)
        ]

        try:
            salvar_itens_venda(1, [("P999", 1, 100)], caminho_banco)
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("Item com produto inexistente deveria ser recusado.")

        try:
            registrar_pedido(
                "2026-11-18 10:01:00",
                "PIX",
                100,
                itens=[("P999", 1, 100)],
                caminho=caminho_banco,
            )
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError(
                "Venda com produto inexistente deveria ser recusada."
            )

        assert listar_vendas(caminho_banco) == [
            (1, "2026-11-18 10:00:00", "PIX", 100, None)
        ]
        with closing(_conectar(caminho_banco)) as conexao:
            assert conexao.execute(
                "SELECT id, produto_codigo FROM itens_venda"
            ).fetchall() == [(1, "P01")]


def verificar_migracao_item_orfa_preservada():
    with TemporaryDirectory() as diretorio:
        caminho_banco = Path(diretorio) / "produto_orfao.db"
        with closing(sqlite3.connect(caminho_banco)) as conexao:
            with conexao:
                conexao.execute(
                    """
                    CREATE TABLE produtos (
                        codigo TEXT PRIMARY KEY,
                        nome TEXT NOT NULL,
                        preco_centavos INTEGER NOT NULL
                    )
                    """
                )
                conexao.execute(
                    """
                    CREATE TABLE clientes (
                        id INTEGER PRIMARY KEY,
                        nome TEXT NOT NULL,
                        telefone TEXT
                    )
                    """
                )
                conexao.execute(
                    """
                    CREATE TABLE vendas (
                        id INTEGER PRIMARY KEY,
                        data_hora TEXT NOT NULL,
                        forma_pagamento TEXT NOT NULL,
                        total_centavos INTEGER NOT NULL,
                        cliente_id INTEGER
                    )
                    """
                )
                conexao.execute(
                    """
                    CREATE TABLE itens_venda (
                        id INTEGER PRIMARY KEY,
                        venda_id INTEGER NOT NULL,
                        produto_codigo TEXT NOT NULL,
                        quantidade INTEGER NOT NULL,
                        preco_centavos INTEGER NOT NULL
                    )
                    """
                )
                conexao.execute(
                    """
                    INSERT INTO vendas
                    VALUES (1, '2026-11-18 10:00:00', 'PIX', 100, NULL)
                    """
                )
                conexao.execute(
                    """
                    INSERT INTO itens_venda
                    VALUES (1, 1, 'P999', 1, 100)
                    """
                )

        try:
            criar_banco(
                caminho_banco,
                Path(diretorio) / "catalogo_inexistente.json",
            )
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("A migração deveria recusar item sem produto.")

        with closing(sqlite3.connect(caminho_banco)) as conexao:
            tabelas = {
                linha[0]
                for linha in conexao.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            assert "itens_venda_com_fk" not in tabelas
            assert conexao.execute(
                "SELECT id, produto_codigo FROM itens_venda"
            ).fetchall() == [(1, "P999")]
            assert conexao.execute(
                "PRAGMA foreign_key_list(itens_venda)"
            ).fetchall() == []


def verificar_persistencia_vendas():
    with TemporaryDirectory() as diretorio:
        caminho_banco = Path(diretorio) / "teste_vendas.db"
        caminho_catalogo = Path(diretorio) / "catalogo_inexistente.json"
        criar_banco(caminho_banco, caminho_catalogo)
        for codigo, nome, preco in (
            ("P01", "Produto 1", 650),
            ("P02", "Produto 2", 500),
            ("P03", "Produto 3", 300),
            ("P04", "Produto 4", 500),
            ("ERRO", "Produto de teste", 500),
        ):
            salvar_produto(codigo, nome, preco, caminho_banco)
        cliente_id = salvar_cliente("Maria", caminho=caminho_banco)

        venda_id = registrar_pedido(
            "2026-11-13 14:20:00",
            "PIX",
            2100,
            cliente_id,
            [("P01", 2, 650), ("P02", 1, 500)],
            caminho_banco,
        )

        assert isinstance(venda_id, int) and venda_id > 0
        assert listar_vendas(caminho_banco) == [
            (venda_id, "2026-11-13 14:20:00", "PIX", 2100, cliente_id)
        ]
        assert salvar_itens_venda(
            venda_id,
            [("P03", 1, 300)],
            caminho_banco,
        ) == 1
        with closing(sqlite3.connect(caminho_banco)) as conexao:
            assert conexao.execute(
                """
                SELECT venda_id, produto_codigo, quantidade, preco_centavos
                FROM itens_venda
                WHERE venda_id = ?
                ORDER BY id
                """,
                (venda_id,),
            ).fetchall() == [
                (venda_id, "P01", 2, 650),
                (venda_id, "P02", 1, 500),
                (venda_id, "P03", 1, 300),
            ]

        with closing(sqlite3.connect(caminho_banco)) as conexao:
            conexao.execute(
                """
                CREATE TRIGGER falhar_item_teste
                BEFORE INSERT ON itens_venda
                WHEN NEW.produto_codigo = 'ERRO'
                BEGIN
                    SELECT RAISE(ABORT, 'falha de teste ao inserir item');
                END
                """
            )

        with closing(sqlite3.connect(caminho_banco)) as conexao:
            totais_antes = (
                conexao.execute("SELECT COUNT(*) FROM vendas").fetchone()[0],
                conexao.execute("SELECT COUNT(*) FROM itens_venda").fetchone()[0],
            )

        try:
            registrar_pedido(
                "2026-11-13 14:21:00",
                "Dinheiro",
                1000,
                itens=[("P04", 1, 500), ("ERRO", 1, 500)],
                caminho=caminho_banco,
            )
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("Falha na inserção de item deveria abortar o pedido.")

        with closing(sqlite3.connect(caminho_banco)) as conexao:
            totais_depois = (
                conexao.execute("SELECT COUNT(*) FROM vendas").fetchone()[0],
                conexao.execute("SELECT COUNT(*) FROM itens_venda").fetchone()[0],
            )
        assert totais_depois == totais_antes


def verificar_venda_simples():
    with TemporaryDirectory() as diretorio:
        caminho_banco = Path(diretorio) / "venda_simples.db"
        criar_banco(caminho_banco, Path(diretorio) / "catalogo_inexistente.json")
        salvar_produto("P01", "Produto 1", 1000, caminho_banco)

        venda_id = registrar_pedido(
            "2026-11-13 14:45:00",
            "PIX",
            1000,
            itens=[("P01", 1, 1000)],
            caminho=caminho_banco,
        )

        vendas = listar_vendas(caminho_banco)
        assert any(venda[0] == venda_id for venda in vendas)


def verificar_venda_com_itens():
    with TemporaryDirectory() as diretorio:
        caminho_banco = Path(diretorio) / "venda_com_itens.db"
        criar_banco(caminho_banco, Path(diretorio) / "catalogo_inexistente.json")
        salvar_produto("P01", "Produto 1", 1000, caminho_banco)
        salvar_produto("P02", "Produto 2", 400, caminho_banco)

        venda_id = registrar_pedido(
            "2026-11-13 14:45:00",
            "Crédito 1x",
            1800,
            itens=[
                ("P01", 1, 1000),
                ("P02", 2, 400),
            ],
            caminho=caminho_banco,
        )

        with closing(sqlite3.connect(caminho_banco)) as conexao:
            quantidade_itens = conexao.execute(
                "SELECT COUNT(*) FROM itens_venda WHERE venda_id = ?",
                (venda_id,),
            ).fetchone()[0]
        assert quantidade_itens == 2


def verificar_rollback_sem_venda():
    with TemporaryDirectory() as diretorio:
        caminho_banco = Path(diretorio) / "rollback.db"
        criar_banco(caminho_banco, Path(diretorio) / "catalogo_inexistente.json")
        salvar_produto("P01", "Produto 1", 1000, caminho_banco)

        with closing(sqlite3.connect(caminho_banco)) as conexao:
            conexao.execute(
                """
                CREATE TRIGGER forcar_erro_item
                BEFORE INSERT ON itens_venda
                BEGIN
                    SELECT RAISE(ABORT, 'erro de teste');
                END
                """
            )

        try:
            registrar_pedido(
                "2026-11-13 14:45:00",
                "PIX",
                1000,
                itens=[("P01", 1, 1000)],
                caminho=caminho_banco,
            )
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("A falha forçada deveria abortar a venda.")

        with closing(sqlite3.connect(caminho_banco)) as conexao:
            quantidade_vendas = conexao.execute(
                "SELECT COUNT(*) FROM vendas"
            ).fetchone()[0]
            quantidade_itens = conexao.execute(
                "SELECT COUNT(*) FROM itens_venda"
            ).fetchone()[0]
        assert quantidade_vendas == 0
        assert quantidade_itens == 0


def verificar_alteracao_catalogo_recusada():
    with TemporaryDirectory() as diretorio:
        caminho_banco = Path(diretorio) / "catalogo_alterado.db"
        criar_banco(caminho_banco, Path(diretorio) / "catalogo_inexistente.json")
        salvar_produto("P01", "Pizza", 5000, caminho_banco)

        pedido = Pedido()
        pedido.adicionar(Produto("P01", "Pizza", 5000), "1")
        versao = pedido.versao()
        assert atualizar_produto("P01", "Pizza", 6000, caminho_banco)

        try:
            _registrar_pedido_no_banco(
                pedido,
                "PIX",
                versao,
                caminho_banco,
            )
        except ValueError as erro:
            assert "preço mudou de R$ 50,00 para R$ 60,00" in str(erro)
        else:
            raise AssertionError("O preço alterado deveria impedir a gravação.")

        assert pedido.aberto
        assert listar_vendas(caminho_banco) == []


def verificar_confirmacao_integrada_sqlite():
    with TemporaryDirectory() as diretorio:
        caminho_banco = Path(diretorio) / "confirmacao.db"
        criar_banco(caminho_banco, Path(diretorio) / "catalogo_inexistente.json")
        salvar_produto("P01", "Pizza", 650, caminho_banco)
        salvar_produto("ERRO", "Produto", 100, caminho_banco)
        pedido = Pedido()
        pedido.adicionar(Produto("P01", "Pizza", 650), "2")
        versao = pedido.versao()

        venda_id = _registrar_pedido_no_banco(
            pedido,
            "PIX",
            versao,
            caminho_banco,
        )
        comprovante = pedido.finalizar("PIX", versao)

        assert venda_id > 0
        assert comprovante.total_centavos == 1131
        venda = listar_vendas(caminho_banco)[0]
        assert venda[0] == venda_id
        datetime.strptime(venda[1], "%Y-%m-%d %H:%M:%S")
        assert venda[2:] == ("PIX", 1131, None)
        with closing(sqlite3.connect(caminho_banco)) as conexao:
            assert conexao.execute(
                """
                SELECT venda_id, produto_codigo, quantidade, preco_centavos
                FROM itens_venda
                WHERE venda_id = ?
                """,
                (venda_id,),
            ).fetchall() == [(venda_id, "P01", 2, 650)]

        pedido_com_preco_antigo = Pedido()
        pedido_com_preco_antigo.adicionar(Produto("P01", "Pizza", 650), "1")
        versao_preco_antigo = pedido_com_preco_antigo.versao()
        atualizar_produto("P01", "Pizza", 700, caminho_banco)
        total_vendas_antes_alteracao = len(listar_vendas(caminho_banco))
        try:
            _registrar_pedido_no_banco(
                pedido_com_preco_antigo,
                "PIX",
                versao_preco_antigo,
                caminho_banco,
            )
        except ValueError as erro:
            assert "preço mudou de R$ 6,50 para R$ 7,00" in str(erro)
        else:
            raise AssertionError("Preço de catálogo alterado deveria ser detectado.")
        assert pedido_com_preco_antigo.aberto
        assert len(listar_vendas(caminho_banco)) == total_vendas_antes_alteracao

        pedido_com_falha = Pedido()
        pedido_com_falha.adicionar(Produto("ERRO", "Produto", 100), "1")
        versao_falha = pedido_com_falha.versao()
        itens_antes_falha = [
            (item.produto.codigo, item.quantidade)
            for item in pedido_com_falha.itens
        ]
        with closing(sqlite3.connect(caminho_banco)) as conexao:
            conexao.execute(
                """
                CREATE TRIGGER falhar_produto_teste
                BEFORE INSERT ON itens_venda
                WHEN NEW.produto_codigo = 'ERRO'
                BEGIN
                    SELECT RAISE(ABORT, 'falha de teste');
                END
                """
            )
        total_vendas_antes = len(listar_vendas(caminho_banco))
        try:
            _registrar_pedido_no_banco(
                pedido_com_falha,
                "PIX",
                pedido_com_falha.versao(),
                caminho_banco,
            )
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("Falha no SQLite deveria impedir confirmação.")
        assert pedido_com_falha.aberto
        assert pedido_com_falha.versao() == versao_falha
        assert [
            (item.produto.codigo, item.quantidade)
            for item in pedido_com_falha.itens
        ] == itens_antes_falha
        assert len(listar_vendas(caminho_banco)) == total_vendas_antes

        with closing(sqlite3.connect(caminho_banco)) as conexao:
            conexao.execute("DROP TRIGGER falhar_produto_teste")
        venda_retentada = _registrar_pedido_no_banco(
            pedido_com_falha,
            "PIX",
            versao_falha,
            caminho_banco,
        )
        comprovante_retentado = pedido_com_falha.finalizar("PIX", versao_falha)
        assert venda_retentada > 0
        assert not pedido_com_falha.aberto
        assert comprovante_retentado.linhas[0].startswith("ERRO Produto x1")
        assert len(listar_vendas(caminho_banco)) == total_vendas_antes + 1


def verificar_cliente_no_comprovante():
    pedido = Pedido()
    cliente = (1, "João Silva", "51999999999")
    pedido.definir_cliente(cliente)
    pedido.adicionar(Produto("P01", "Mussarela", 4990), "1")

    comprovante = pedido.finalizar("PIX", pedido.versao())
    assert comprovante.cliente == cliente

    pedido.novo()
    assert pedido.cliente is None


def teste_vinculo_valido():
    assert vinculo_valido({"cliente_id": 1}) is True


def teste_vinculo_inexistente():
    assert vinculo_valido({"cliente_id": 99}) is False


def teste_nome_nao_quebra_vinculo():
    nome_original = clientes_vinculo[1]
    try:
        clientes_vinculo[1] = "João Silva"
        resultado = vinculo_valido({"cliente_id": 1})
        assert resultado is True
    finally:
        clientes_vinculo[1] = nome_original


def verificar_validar_vinculos():
    alunos = {1: "Ana", 2: "Beto"}
    planos = {10: "Plano A"}
    matriculas = [{"aluno_id": 1, "plano_id": 10}]
    estado_original = (
        alunos.copy(),
        planos.copy(),
        [matricula.copy() for matricula in matriculas],
    )

    assert validar_vinculos(alunos, planos, matriculas)
    assert not pode_excluir_aluno(1, matriculas)
    assert pode_excluir_aluno(2, matriculas)

    casos_invalidos = (
        (
            lambda: validar_vinculos({}, planos, matriculas),
            "Aluno 1 não existe.",
        ),
        (
            lambda: validar_vinculos(alunos, {}, matriculas),
            "Plano 10 não existe.",
        ),
        (
            lambda: validar_vinculos(
                alunos,
                planos,
                matriculas * 2,
            ),
            "Matrícula duplicada para aluno 1 e plano 10.",
        ),
        (
            lambda: validar_vinculos({True: "Ana"}, planos, []),
            "ID de aluno deve ser um inteiro positivo.",
        ),
        (
            lambda: validar_vinculos({-1: "Ana"}, planos, []),
            "ID de aluno deve ser um inteiro positivo.",
        ),
        (
            lambda: validar_vinculos(
                alunos,
                planos,
                [{"aluno_id": True, "plano_id": 10}],
            ),
            "ID de aluno deve ser um inteiro positivo.",
        ),
        (
            lambda: validar_vinculos(
                alunos,
                planos,
                [{"aluno_id": 1, "plano_id": 0}],
            ),
            "ID de plano deve ser um inteiro positivo.",
        ),
    )
    for validar, mensagem_esperada in casos_invalidos:
        try:
            validar()
        except ValueError as erro:
            assert str(erro) == mensagem_esperada
        else:
            raise AssertionError(
                f"Vínculo inválido deveria ser recusado: {mensagem_esperada}"
            )

    try:
        pode_excluir_aluno(True, matriculas)
    except ValueError as erro:
        assert str(erro) == "ID de aluno deve ser um inteiro positivo."
    else:
        raise AssertionError("ID booleano deveria ser recusado.")

    assert (
        alunos,
        planos,
        matriculas,
    ) == estado_original


def verificar_comparacao_memoria_sqlite():
    saida = StringIO()
    with redirect_stdout(saida):
        demonstrar_relacoes_sqlite()

    assert saida.getvalue().splitlines() == [
        "Memória: venda com cliente válido aceita.",
        "Memória: venda recusada: O cliente informado não existe.",
        "Memória: exclusão recusada: Cliente possui vendas vinculadas.",
        "SQLite: venda com cliente válido aceita.",
        "SQLite: venda recusada: FOREIGN KEY constraint failed",
        "SQLite: exclusão recusada: FOREIGN KEY constraint failed",
    ]


def verificar_repositorio_memoria():
    repositorio = ProdutosMemoria()
    assert repositorio.listar() == []

    repositorio.salvar("P01", "Mussarela", 4990)
    assert repositorio.listar() == [("P01", "Mussarela", 4990)]

    lista = repositorio.listar()
    lista.clear()
    assert repositorio.listar() == [("P01", "Mussarela", 4990)]

    assert repositorio.atualizar("P01", "Calabresa", 5490)
    assert repositorio.listar() == [("P01", "Calabresa", 5490)]
    assert not repositorio.atualizar("P99", "Inexistente", 100)

    assert repositorio.remover("P01")
    assert repositorio.listar() == []
    assert not repositorio.remover("P01")

    novo_repositorio = ProdutosMemoria()
    assert novo_repositorio.listar() == []


def verificar_controller_produtos():
    with TemporaryDirectory() as diretorio:
        repositorios = (
            ProdutosMemoria(),
            ProdutosSQLite(Path(diretorio) / "controller.db"),
        )
        for indice, repositorio in enumerate(repositorios):
            iniciar = getattr(repositorio, "iniciar", None)
            if iniciar is not None:
                iniciar()
            controller = ProdutoController(repositorio)
            lista_inicial = controller.listar_produtos()
            codigo = f"CTRL16-{indice}"

            controller.salvar_produto(codigo, "  Pizza teste  ", 3210)
            assert (codigo, "Pizza teste", 3210) in controller.listar_produtos()

            assert controller.atualizar_produto(
                codigo, "Pizza atualizada", 6540
            )
            assert (codigo, "Pizza atualizada", 6540) in controller.listar_produtos()
            assert not controller.atualizar_produto(
                "AUSENTE", "Produto ausente", 100
            )

            assert controller.remover_produto(codigo)
            assert controller.listar_produtos() == lista_inicial
            assert not controller.remover_produto(codigo)

            for argumentos in (
                ("", "Nome", 100),
                ("P1", "   ", 100),
                ("P1", "Nome", 0),
            ):
                try:
                    controller.salvar_produto(*argumentos)
                except ValueError:
                    pass
                else:
                    raise AssertionError(
                        f"Controller deveria rejeitar dados inválidos: {argumentos}"
                    )


def verificar_recusas_e_cancelamento():
    with TemporaryDirectory() as diretorio:
        caminho_banco = Path(diretorio) / "recusas.db"
        criar_banco(caminho_banco, Path(diretorio) / "catalogo_inexistente.json")
        repositorio = ProdutosSQLite(caminho_banco)
        controller = ProdutoController(repositorio)
        controller.salvar_produto("P01", "Pizza", 5000)
        produtos_esperados = [("P01", "Pizza", 5000)]

        assert not controller.atualizar_produto("AUSENTE", "Produto", 100)
        assert not controller.remover_produto("AUSENTE")
        assert controller.listar_produtos() == produtos_esperados

        pedido = Pedido()
        try:
            pedido.remover("AUSENTE")
        except ValueError as erro:
            assert "nao esta no pedido" in str(erro)
        else:
            raise AssertionError("Remover produto inexistente deveria ser recusado.")

        try:
            controller.salvar_produto("P01", "Duplicado", 9000)
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("Código duplicado deveria ser recusado pelo SQLite.")
        assert controller.listar_produtos() == produtos_esperados

        for argumentos in (
            ("", "Produto", 100),
            ("P02", "   ", 100),
            ("P02", "Produto", 0),
        ):
            try:
                controller.salvar_produto(*argumentos)
            except ValueError:
                pass
            else:
                raise AssertionError(
                    f"Dados inválidos deveriam ser recusados: {argumentos}"
                )
        assert controller.listar_produtos() == produtos_esperados

        removido = _remover_produto_se_confirmado(
            controller,
            "P01",
            confirmado=False,
        )
        assert not removido
        assert controller.listar_produtos() == produtos_esperados

        pedido_venda = Pedido()
        pedido_venda.adicionar(Produto("P01", "Pizza", 5000), "1")
        versao = pedido_venda.versao()
        assert controller.atualizar_produto("P01", "Pizza", 6000)
        itens_esperados = [("P01", 1)]
        try:
            _registrar_pedido_no_banco(
                pedido_venda,
                "PIX",
                versao,
                caminho_banco,
            )
        except ValueError as erro:
            assert "O catálogo foi alterado" in str(erro)
            assert "R$ 50,00" in str(erro)
            assert "R$ 60,00" in str(erro)
        else:
            raise AssertionError("Venda com catálogo alterado deveria ser recusada.")
        assert pedido_venda.aberto
        assert [
            (item.produto.codigo, item.quantidade)
            for item in pedido_venda.itens
        ] == itens_esperados
        assert listar_vendas(caminho_banco) == []


def verificar_exportacao_csv():
    forma = 'Pagamento: João; Débito "especial"'
    comprovante = Comprovante([], 12345, forma)

    with TemporaryDirectory() as diretorio:
        caminho = Path(diretorio) / "relatorio.csv"
        exportar_csv(caminho, comprovante)

        with caminho.open(newline="", encoding="utf-8") as arquivo:
            leitor = csv.DictReader(arquivo, delimiter=";")
            linhas = list(leitor)

    assert leitor.fieldnames == [
        "data_hora",
        "forma_pagamento",
        "total_centavos",
        "total_reais",
    ]
    assert len(linhas) == 1
    assert linhas[0]["forma_pagamento"] == forma
    assert linhas[0]["total_centavos"] == "12345"
    assert linhas[0]["total_reais"] == "123.45"
    datetime.strptime(linhas[0]["data_hora"], "%Y-%m-%d %H:%M:%S")


def verificar_leitura_e_registro_csv():
    formas = [
        "Crédito com acento: débito",
        "Pagamento; com separador",
        'Pagamento com "aspas"',
    ]

    with TemporaryDirectory() as diretorio:
        caminho = Path(diretorio) / "vendas.csv"
        for forma in formas:
            registrar_venda_csv(Comprovante([], 2500, forma), caminho)

        with caminho.open(newline="", encoding="utf-8") as arquivo:
            leitor = csv.DictReader(arquivo, delimiter=";")
            linhas = list(leitor)
            cabecalho = leitor.fieldnames

    assert cabecalho == [
        "data_hora",
        "forma_pagamento",
        "total_centavos",
        "total_reais",
    ]
    assert [linha["forma_pagamento"] for linha in linhas] == formas
    assert all(linha["total_centavos"] == "2500" for linha in linhas)


def verificar_erro_exportacao():
    comprovante = Comprovante([], 1000, "Dinheiro")

    with TemporaryDirectory() as diretorio:
        caminho_invalido = Path(diretorio) / "pasta_inexistente" / "relatorio.csv"
        try:
            exportar_csv(caminho_invalido, comprovante)
        except OSError:
            pass
        else:
            raise AssertionError("A exportação deveria propagar o erro de gravação.")


def verificar_permissoes_caixa():
    sessao = SessaoDemo()
    sessao.entrar("João", "Caixa")

    assert sessao.nome == "João"
    assert sessao.perfil == "Caixa"
    assert sessao.pode_operar_vendas()
    assert not sessao.pode_configurar()


def verificar_permissoes_administracao():
    sessao = SessaoDemo()
    sessao.entrar("Ana", "Administracao")

    assert sessao.nome == "Ana"
    assert sessao.perfil == "Administracao"
    assert sessao.pode_configurar()
    assert not sessao.pode_operar_vendas()


def verificar_encerramento_sessao():
    sessao = SessaoDemo()
    sessao.entrar("João", "Caixa")
    sessao.sair()

    assert sessao.nome is None
    assert sessao.perfil is None
    assert not sessao.pode_configurar()
    assert not sessao.pode_operar_vendas()


def main():
    grupos = (
        (
            "Pagamento",
            (("Cálculos e validação", verificar_pagamento),),
        ),
        (
            "Pedido",
            (("Remover item, preservar restante e esvaziar pedido",
              verificar_remocao_item_pedido),),
        ),
        (
            "Perfis",
            (
                ("Permissões de Caixa", verificar_permissoes_caixa),
                ("Permissões de Administração", verificar_permissoes_administracao),
                ("Encerramento da sessão", verificar_encerramento_sessao),
            ),
        ),
        (
            "Produtos",
            (
                ("Backup SQLite criado sem sobrescrever arquivos", verificar_backup_sqlite),
                (
                    "Persistência SQLite: inserir, atualizar, reabrir e remover",
                    verificar_persistencia_sqlite,
                ),
                (
                    "Chaves estrangeiras habilitadas e exclusão RESTRICT",
                    verificar_chaves_estrangeiras,
                ),
                (
                    "Recusa produto inexistente e migra itens antigos",
                    verificar_produto_inexistente,
                ),
                (
                    "Contrato do repositório em memória",
                    verificar_repositorio_memoria,
                ),
                (
                    "Controller com repositórios memória e SQLite",
                    verificar_controller_produtos,
                ),
                ("Recusas de produto e dados inválidos", verificar_recusas_e_cancelamento),
            ),
        ),
        (
            "Clientes",
            (
                ("CRUD de clientes", verificar_crud_clientes),
                ("Recusa cliente inexistente e migra vendas antigas",
                 verificar_cliente_inexistente),
                ("Rollback de migração com venda órfã",
                 verificar_migracao_orfa_preservada),
                ("Rollback de migração com item órfão",
                 verificar_migracao_item_orfa_preservada),
                ("Cliente no comprovante", verificar_cliente_no_comprovante),
            ),
        ),
        (
            "Vínculos",
            (
                ("Vínculo válido", teste_vinculo_valido),
                ("Vínculo inexistente", teste_vinculo_inexistente),
                ("Nome não quebra vínculo por ID", teste_nome_nao_quebra_vinculo),
                ("Validação de matrícula e exclusão de aluno",
                 verificar_validar_vinculos),
            ),
        ),
        (
            "Relações SQLite",
            (
                ("Comparação de vínculos entre memória e SQLite",
                 verificar_comparacao_memoria_sqlite),
            ),
        ),
        (
            "Vendas",
            (
                ("Persistência de vendas e itens", verificar_persistencia_vendas),
                ("Venda simples gravada", verificar_venda_simples),
                ("Venda com quantidade esperada de itens", verificar_venda_com_itens),
                ("Rollback sem venda ou itens", verificar_rollback_sem_venda),
                (
                    "Alteração de catálogo detectada",
                    verificar_alteracao_catalogo_recusada,
                ),
                (
                    "Confirmação integrada ao SQLite",
                    verificar_confirmacao_integrada_sqlite,
                ),
            ),
        ),
        (
            "Relatórios CSV",
            (
                ("Exportação CSV", verificar_exportacao_csv),
                ("Leitura CSV e caracteres especiais", verificar_leitura_e_registro_csv),
                ("Erro de exportação", verificar_erro_exportacao),
            ),
        ),
    )

    total = 0
    for categoria, verificacoes in grupos:
        print(f"[{categoria}]")
        for descricao, verificar in verificacoes:
            verificar()
            print(f"OK: {descricao}")
            total += 1

    print(f"{total} verificações concluídas.")


if __name__ == "__main__":
    main()
