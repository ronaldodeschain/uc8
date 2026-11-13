"""Testes sem interface para CSV e sessões de perfil."""
import csv
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from banco import (
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
)
from modelos import Comprovante, Pedido, Produto
from perfis import SessaoDemo
from memoria import ProdutosMemoria
from controller import ProdutoController
from repositorio import ProdutosSQLite
from relatorios import exportar_csv, registrar_venda_csv
from main import (
    _registrar_pedido_no_banco,
    _remover_produto_se_confirmado,
)
from pagamento import calcular_pagamento, preco_para_centavos
from backup_sqlite import criar_backup


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


def verificar_persistencia_vendas():
    with TemporaryDirectory() as diretorio:
        caminho_banco = Path(diretorio) / "teste_vendas.db"
        caminho_catalogo = Path(diretorio) / "catalogo_inexistente.json"
        criar_banco(caminho_banco, caminho_catalogo)
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
                ("Cliente no comprovante", verificar_cliente_no_comprovante),
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
