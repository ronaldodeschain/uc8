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
    remover_cliente,
    remover_produto,
    salvar_cliente,
    salvar_produto,
)
from modelos import Comprovante, Pedido, Produto
from perfis import SessaoDemo
from memoria import ProdutosMemoria
from controller import ProdutoController
from repositorio import ProdutosSQLite
from relatorios import exportar_csv, registrar_venda_csv


def produto_existe(codigo, caminho):
    with closing(sqlite3.connect(caminho)) as conexao:
        linha = conexao.execute(
            "SELECT 1 FROM produtos WHERE codigo = ?",
            (codigo,),
        ).fetchone()
    return linha is not None


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
    verificacoes = (
        ("Persistência SQLite: inserir, atualizar, reabrir e remover",
         verificar_persistencia_sqlite),
        ("CRUD de clientes", verificar_crud_clientes),
        ("Cliente no comprovante", verificar_cliente_no_comprovante),
        ("Contrato do repositório em memória", verificar_repositorio_memoria),
        ("Controller com repositórios memória e SQLite",
         verificar_controller_produtos),
        ("Exportação CSV", verificar_exportacao_csv),
        ("Leitura CSV e caracteres especiais", verificar_leitura_e_registro_csv),
        ("Erro de exportação", verificar_erro_exportacao),
        ("Permissões Caixa", verificar_permissoes_caixa),
        ("Permissões Administração", verificar_permissoes_administracao),
        ("Encerramento da sessão", verificar_encerramento_sessao),
    )

    for descricao, verificar in verificacoes:
        verificar()
        print(f"OK: {descricao}")

    print(f"{len(verificacoes)} verificações concluídas.")


if __name__ == "__main__":
    main()
