"""Testes sem interface para CSV e sessões de perfil."""
import csv
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from modelos import Comprovante
from perfis import SessaoDemo
from relatorios import exportar_csv, registrar_venda_csv


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
