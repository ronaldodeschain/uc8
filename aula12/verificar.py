"""A12 — verificações de catálogo JSON e navegação sem perder o pedido."""
import json
from pathlib import Path
import tempfile

from arquivos import ler_catalogo, salvar_catalogo, validar_catalogo
from modelos import Pedido, Produto


CATALOGO_VALIDO = [
    {"id": 1, "nome": "Arroz", "preco_centavos": 2590},
    {"id": 2, "nome": "Feijão", "preco_centavos": 890},
    {"id": 3, "nome": "Macarrão", "preco_centavos": 650},
]


def _esperar_value_error(acao, trecho=None):
    try:
        acao()
    except ValueError as erro:
        if trecho is not None:
            assert trecho in str(erro), str(erro)
    else:
        raise AssertionError(f"Era esperado ValueError contendo: {trecho}")


def _estado_pedido(pedido):
    return (
        pedido.versao(),
        [
            (
                item.produto.codigo,
                item.produto.nome,
                item.quantidade,
                item.subtotal(),
            )
            for item in pedido.itens
        ],
        pedido.total_centavos(),
        pedido.aberto,
    )


def verificar_catalogo():
    with tempfile.TemporaryDirectory() as pasta:
        caminho = Path(pasta) / "catalogo.json"

        previsto_ausente = None
        assert ler_catalogo(caminho) == previsto_ausente
        print("[OK] Catálogo ausente")

        previsto_valido = [dict(produto) for produto in CATALOGO_VALIDO]
        salvar_catalogo(caminho, previsto_valido)
        bytes_validos = caminho.read_bytes()
        assert ler_catalogo(caminho) == previsto_valido
        assert caminho.read_bytes() == bytes_validos
        print("[OK] Catálogo válido, round-trip e leitura sem alteração")

        texto_quebrado = '[{"id": 1, "nome": "Arroz" "preco_centavos": 100}]'
        caminho.write_text(texto_quebrado, encoding="utf-8")
        bytes_quebrados = caminho.read_bytes()
        _esperar_value_error(lambda: ler_catalogo(caminho), "JSON inválido")
        assert caminho.read_bytes() == bytes_quebrados
        print("[OK] JSON quebrado rejeitado e preservado")

        estrutura_invalida = {"id": 1, "nome": "Arroz", "preco_centavos": 100}
        caminho.write_text(
            json.dumps(estrutura_invalida),
            encoding="utf-8",
        )
        bytes_estrutura_invalida = caminho.read_bytes()
        _esperar_value_error(lambda: ler_catalogo(caminho), "Catálogo deve ser uma lista")
        assert caminho.read_bytes() == bytes_estrutura_invalida
        print("[OK] JSON válido com estrutura fora das regras rejeitado e preservado")

        salvar_catalogo(caminho, previsto_valido)
        bytes_anteriores = caminho.read_bytes()
        catalogo_repetido = [
            {"id": 7, "nome": "Produto A", "preco_centavos": 100},
            {"id": "7", "nome": "Produto B", "preco_centavos": 200},
        ]
        _esperar_value_error(
            lambda: validar_catalogo(catalogo_repetido),
            "ID repetido",
        )
        _esperar_value_error(
            lambda: salvar_catalogo(caminho, catalogo_repetido),
            "ID repetido",
        )
        assert caminho.read_bytes() == bytes_anteriores
        print("[OK] ID repetido rejeitado antes de alterar o arquivo")

        try:
            assert ler_catalogo(caminho) == [], "previsão deliberadamente falsa"
        except AssertionError as erro:
            assert "previsão deliberadamente falsa" in str(erro)
        else:
            raise AssertionError("A previsão falsa deveria falhar.")

        assert ler_catalogo(caminho) == previsto_valido
        assert caminho.read_bytes() == bytes_anteriores
        print("[OK] Previsão falsa falhou; previsão correta passou sem alterar os dados")

    return True


def verificar_navegacao():
    """Trocar de catálogo ou cancelar não altera o pedido em andamento."""
    arroz = Produto("1", "Arroz", 2590)
    feijao = Produto("2", "Feijão", 890)

    pedido = Pedido()
    pedido.adicionar(arroz, "2")
    estado_inicial = _estado_pedido(pedido)

    catalogo_previsto = [{"id": 10, "nome": "Suco", "preco_centavos": 600}]
    with tempfile.TemporaryDirectory() as pasta:
        caminho = Path(pasta) / "outro_catalogo.json"
        salvar_catalogo(caminho, catalogo_previsto)
        catalogo_carregado = ler_catalogo(caminho)

    assert catalogo_carregado == catalogo_previsto
    assert _estado_pedido(pedido) == estado_inicial
    print("[OK] Troca de catálogo preservou itens, quantidades, total e versão")

    _esperar_value_error(lambda: pedido.adicionar(feijao, "abc"))
    assert _estado_pedido(pedido) == estado_inicial

    _esperar_value_error(
        lambda: pedido.finalizar("PIX", pedido.versao() + 99),
        "Pedido alterado",
    )
    assert _estado_pedido(pedido) == estado_inicial
    print("[OK] Cancelamento e falha de confirmação preservaram o pedido")

    try:
        assert pedido.total_centavos() == 9999, "previsão deliberadamente falsa"
    except AssertionError as erro:
        assert "previsão deliberadamente falsa" in str(erro)
    else:
        raise AssertionError("A previsão falsa do pedido deveria falhar.")

    assert pedido.total_centavos() == 5180
    assert _estado_pedido(pedido) == estado_inicial
    print("[OK] Previsão falsa do total falhou; valor correto passou sem alterar o pedido")
    return True


def verificar():
    casos = [
        ("Catálogo JSON", verificar_catalogo),
        ("Navegação sem perder pedido", verificar_navegacao),
    ]
    for nome, caso in casos:
        assert caso() is True
        print(f"[OK] Caso completo: {nome}")
    return True


if __name__ == "__main__":
    if verificar():
        print("Todos os casos executados passaram.")
