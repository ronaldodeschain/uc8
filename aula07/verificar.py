# Complete os casos do registro; não marque sucesso sem verificá-los.
from modelos import Produto, Pedido, quantidade, formatar

def verificar_produto():
    # produto valido
    p = Produto("F01", "Fruta", 150)
    assert p.codigo == "F01"
    assert p.nome == "Fruta"
    assert p.preco_centavos == 150

    # codigo ou nome vazios levantam ValueError
    try:
        Produto("", "Fruta", 150)
        assert False, "deveria ter levantado ValueError"
    except ValueError:
        pass

    try:
        Produto("F01", "", 150)
        assert False, "deveria ter levantado ValueError"
    except ValueError:
        pass

    # preco invalido levanta ValueError
    try:
        Produto("F01", "Fruta", 0)
        assert False, "deveria ter levantado ValueError"
    except ValueError:
        pass

    try:
        Produto("F01", "Fruta", -1)
        assert False, "deveria ter levantado ValueError"
    except ValueError:
        pass

    return True

def verificar_item():
    fruta = Produto("F01", "Fruta", 150)

    # item valido
    from modelos import Item
    item = Item(fruta, "2")
    assert item.quantidade == 2
    assert item.subtotal() == 300

    # quantidade zero levanta ValueError
    try:
        Item(fruta, "0")
        assert False, "deveria ter levantado ValueError"
    except ValueError:
        pass

    # quantidade texto levanta ValueError
    try:
        Item(fruta, "abc")
        assert False, "deveria ter levantado ValueError"
    except ValueError:
        pass

    return True

def verificar_pedido():
    fruta = Produto("F01", "Fruta", 150)
    leite = Produto("L01", "Leite", 300)

    # duas frutas e tres leites
    pedido = Pedido()
    pedido.adicionar(fruta, "2")
    pedido.adicionar(leite, "3")

    assert len(pedido.itens) == 2
    assert pedido.itens[0].quantidade == 2
    assert pedido.itens[1].quantidade == 3
    assert pedido.itens[0].subtotal() == 300
    assert pedido.itens[1].subtotal() == 900
    assert pedido.total_centavos() == 1200
    assert formatar(1200) == "R$ 12,00"

    # repeticao por codigo acumula quantidade
    qtd_antes = pedido.itens["F01"].quantidade
    pedido.adicionar(fruta, "1")
    assert pedido.itens["F01"].quantidade == qtd_antes + 1
    assert len(pedido.itens) == 2

    # quantidade invalida preserva pedido
    outro = Produto("A01", "Outro", 200)
    try:
        pedido.adicionar(outro, "0")
        assert False, "deveria ter levantado ValueError"
    except ValueError:
        pass
    assert len(pedido.itens) == 2

    try:
        pedido.adicionar(outro, "abc")
        assert False, "deveria ter levantado ValueError"
    except ValueError:
        pass
    assert len(pedido.itens) == 2

    # pedido fechado recusa adicionar
    pedido.aberto = False
    try:
        pedido.adicionar(outro, "1")
        assert False, "deveria ter levantado RuntimeError"
    except RuntimeError as e:
        assert "fechado" in str(e)

    # linhas inclui codigos e total
    pedido2 = Pedido()
    pedido2.adicionar(fruta, "2")
    pedido2.adicionar(leite, "3")
    linhas = pedido2.linhas()
    assert any("F01" in l for l in linhas)
    assert any("L01" in l for l in linhas)
    assert any("Total" in l for l in linhas)

    # previsao deliberadamente errada — deve falhar com AssertionError
    try:
        assert pedido2.total_centavos() == 9999, "previsao falsa intencional"
        assert False, "deveria ter falhado na linha anterior"
    except AssertionError as e:
        assert "previsao falsa intencional" in str(e)

    # previsao correta restaurada — dados reais nao foram alterados
    assert pedido2.total_centavos() == 1200

    return True


def verificar():
    # TODO: criar dados fictícios, executar e comparar com assert.
    fruta = Produto("F01", "Fruta", 150)

    # TODO: testar limites — quantidade 1 e valor alto.
    p2 = Produto("B01", "Produto B", 9999)
    pedido2 = Pedido()
    pedido2.adicionar(p2, "1")
    assert pedido2.itens[0].quantidade == 1
    assert pedido2.itens[0].subtotal() == 9999
    assert formatar(9999) == "R$ 99,99"

    # uma correcao: nova execucao com quantidade corrigida
    pedido3 = Pedido()
    pedido3.adicionar(fruta, "5")
    assert pedido3.total_centavos() == 750
    assert formatar(750) == "R$ 7,50"

    return True


if __name__ == "__main__":
    casos = [
        ("Produto", verificar_produto),
        ("Item", verificar_item),
        ("Pedido", verificar_pedido),
        ("Geral", verificar),
    ]
    todos = True
    for nome, teste in casos:
        resultado = teste()
        status = "OK" if resultado else "pendente"
        print(f"[{status}] {nome}")
        todos = todos and resultado
    if todos:
        print("Casos executados: previsoes e resultados conferem.")
    else:
        print("Verificacoes ainda incompletas.")
