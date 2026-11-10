"""A12 — verificação de catálogo JSON e navegação sem perder o pedido."""
import json
from pathlib import Path
import tempfile
from arquivos import ler_catalogo, salvar_catalogo, validar_catalogo
from modelos import Produto, Pedido


CATALOGO_VALIDO = [
    {"id": 1, "nome": "Arroz", "preco_centavos": 2590},
    {"id": 2, "nome": "Feijão", "preco_centavos": 890},
    {"id": 3, "nome": "Macarrão", "preco_centavos": 650},
]


def verificar_catalogo():
    with tempfile.TemporaryDirectory() as pasta:
        caminho = Path(pasta) / "catalogo.json"

        # arquivo ausente
        assert ler_catalogo(caminho) is None

        # catálogo válido com acento
        salvar_catalogo(caminho, CATALOGO_VALIDO)
        lido = ler_catalogo(caminho)
        assert lido is not None
        assert len(lido) == 3
        assert lido[1]["nome"] == "Feijão"

        # bytes preservados: ler não altera o arquivo
        bytes_antes = caminho.read_bytes()
        ler_catalogo(caminho)
        assert caminho.read_bytes() == bytes_antes

        # JSON quebrado: levanta ValueError, arquivo não é alterado
        caminho.write_text(
            "[{\"id\": 1, \"nome\": \"Arroz\" \"preco_centavos\": 100}]",
            encoding="utf-8",
        )
        bytes_quebrado = caminho.read_bytes()
        try:
            ler_catalogo(caminho)
            assert False, "deveria ter levantado ValueError"
        except ValueError:
            pass
        assert caminho.read_bytes() == bytes_quebrado

        # ID repetido: validar_catalogo levanta ValueError
        try:
            validar_catalogo([
                {"id": 1, "nome": "A", "preco_centavos": 100},
                {"id": 1, "nome": "B", "preco_centavos": 200},
            ])
            assert False, "deveria ter levantado ValueError"
        except ValueError as e:
            assert "repetido" in str(e)

        # salvar com ID repetido: arquivo anterior preservado
        salvar_catalogo(caminho, CATALOGO_VALIDO)
        bytes_valido = caminho.read_bytes()
        try:
            salvar_catalogo(caminho, [
                {"id": 5, "nome": "X", "preco_centavos": 100},
                {"id": 5, "nome": "Y", "preco_centavos": 200},
            ])
            assert False, "deveria ter levantado ValueError"
        except ValueError:
            pass
        assert caminho.read_bytes() == bytes_valido

        # campo ausente
        try:
            validar_catalogo([{"id": 1, "nome": "Sem preco"}])
            assert False, "deveria ter levantado ValueError"
        except ValueError as e:
            assert "preco_centavos" in str(e)

        # preco_centavos zero ou negativo
        try:
            validar_catalogo([{"id": 1, "nome": "X", "preco_centavos": 0}])
            assert False, "deveria ter levantado ValueError"
        except ValueError:
            pass

        # round-trip preserva os dados
        salvar_catalogo(caminho, CATALOGO_VALIDO)
        assert ler_catalogo(caminho) == CATALOGO_VALIDO

        # previsão deliberadamente errada — deve falhar com AssertionError
        try:
            assert ler_catalogo(caminho) == [], "previsao falsa intencional"
            assert False, "deveria ter falhado na linha anterior"
        except AssertionError as e:
            assert "previsao falsa intencional" in str(e)

        # previsão correta restaurada — dados reais não foram alterados
        assert ler_catalogo(caminho) == CATALOGO_VALIDO

    return True


def verificar_navegacao():
    """Troca de catálogo e cancelamento não devem alterar o pedido em andamento."""
    arroz = Produto("1", "Arroz", 2590)
    feijao = Produto("2", "Feijão", 890)

    pedido = Pedido()
    pedido.adicionar(arroz, "2")
    versao_antes = pedido.versao()
    itens_antes = len(pedido.itens)
    total_antes = pedido.total_centavos()

    # simula troca de aba: carrega outro catálogo sem tocar no pedido
    with tempfile.TemporaryDirectory() as pasta:
        caminho = Path(pasta) / "catalogo2.json"
        outro_catalogo = [{"id": 10, "nome": "Suco", "preco_centavos": 600}]
        salvar_catalogo(caminho, outro_catalogo)
        catalogo_carregado = ler_catalogo(caminho)

    assert catalogo_carregado == outro_catalogo
    # pedido não foi alterado pela troca de catálogo
    assert pedido.versao() == versao_antes
    assert len(pedido.itens) == itens_antes
    assert pedido.total_centavos() == total_antes

    # simula cancelamento: tentativa inválida não altera o pedido
    try:
        pedido.adicionar(feijao, "abc")
    except ValueError:
        pass
    assert pedido.versao() == versao_antes
    assert len(pedido.itens) == itens_antes
    assert pedido.total_centavos() == total_antes

    # simula cancelamento de finalização: versão errada não fecha o pedido
    try:
        pedido.finalizar("PIX", versao_antes + 99)
    except ValueError:
        pass
    assert pedido.aberto is True
    assert pedido.total_centavos() == total_antes

    # previsão deliberadamente errada sobre o total
    try:
        assert pedido.total_centavos() == 9999, "previsao falsa intencional"
        assert False, "deveria ter falhado na linha anterior"
    except AssertionError as e:
        assert "previsao falsa intencional" in str(e)

    # previsão correta restaurada
    assert pedido.total_centavos() == total_antes

    return True


def verificar():
    casos = [
        ("Catálogo JSON", verificar_catalogo),
        ("Navegação sem perder pedido", verificar_navegacao),
    ]
    todos = True
    for nome, caso in casos:
        resultado = caso()
        status = "OK" if resultado else "pendente"
        print(f"[{status}] {nome}")
        todos = todos and resultado
    return todos


if __name__ == "__main__":
    if verificar():
        print("Casos executados: previsões e resultados conferem.")
    else:
        print("Verificações ainda incompletas.")
