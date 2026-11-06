# Complete os casos do registro; não marque sucesso sem verificá-los.
from modelos import Produto, Pedido, formatar
from pagamentos import calcular_pagamento, preco_para_centavos, FATORES


def verificar_pagamento():
    # tabela para R$100,00 nas quatro formas
    assert calcular_pagamento("100,00", "Dinheiro")   == (8700, 1300)
    assert calcular_pagamento("100,00", "PIX")        == (8700, 1300)
    assert calcular_pagamento("100,00", "Débito")     == (9200,  800)
    assert calcular_pagamento("100,00", "Crédito 1x") == (10000,   0)

    # PIX sobre R$0,50; 50 * 0.87 = 43.5 -> arredonda para 44; desconto = 6
    assert calcular_pagamento("0,50", "PIX") == (44, 6)

    # sem desconto acumulado: repetir a chamada retorna o mesmo valor
    assert calcular_pagamento("100,00", "PIX") == (8700, 1300)
    assert calcular_pagamento("100,00", "PIX") == (8700, 1300)

    # ponto decimal tambem aceito
    assert calcular_pagamento("100.00", "PIX") == (8700, 1300)

    # forma desconhecida levanta ValueError
    try:
        calcular_pagamento("100,00", "Boleto")
        assert False, "deveria ter levantado ValueError"
    except ValueError:
        pass

    return True


def verificar_preco_para_centavos():
    assert preco_para_centavos("1,50") == 150
    assert preco_para_centavos("1.50") == 150
    assert preco_para_centavos("3,00") == 300

    # zero nao permitido
    try:
        preco_para_centavos("0")
        assert False, "deveria ter levantado ValueError"
    except ValueError:
        pass

    return True


def verificar_modelos_preservado():
    # caso anterior: duas frutas e tres leites, total e formatar
    fruta = Produto("F01", "Fruta", 150)
    leite = Produto("L01", "Leite", 300)
    pedido = Pedido()
    pedido.adicionar(fruta, "2")
    pedido.adicionar(leite, "3")
    assert pedido.total_centavos() == 1200
    assert formatar(1200) == "R$ 12,00"

    # repeticao por codigo incrementa quantidade — nao duplica item
    pedido.adicionar(fruta, "1")
    assert len(pedido.itens) == 2
    assert pedido.itens[0].quantidade == 3
    assert pedido.total_centavos() == 3 * 150 + 3 * 300

    return True


def verificar_previa():
    # dados ficticios: subtotal de R$100,00 nas quatro formas
    casos = [
        ("100,00", "Dinheiro",   (8700, 1300)),
        ("100,00", "PIX",        (8700, 1300)),
        ("100,00", "Débito",     (9200,  800)),
        ("100,00", "Crédito 1x", (10000,   0)),
    ]
    for subtotal, forma, esperado in casos:
        assert calcular_pagamento(subtotal, forma) == esperado, (
            f"{forma}: esperado {esperado}, obtido {calcular_pagamento(subtotal, forma)}"
        )

    # R$0,50 em PIX
    assert calcular_pagamento("0,50", "PIX") == (44, 6)

    # repeticao da chamada nao acumula desconto
    primeira = calcular_pagamento("100,00", "PIX")
    segunda  = calcular_pagamento("100,00", "PIX")
    terceira = calcular_pagamento("100,00", "PIX")
    assert primeira == segunda == terceira == (8700, 1300)

    # previsao deliberadamente errada — deve falhar com AssertionError
    try:
        assert calcular_pagamento("100,00", "PIX") == (9999, 1), "previsao falsa intencional"
        assert False, "deveria ter falhado na linha anterior"
    except AssertionError as e:
        assert "previsao falsa intencional" in str(e)

    # previsao correta restaurada — dados reais nao foram alterados
    assert calcular_pagamento("100,00", "PIX") == (8700, 1300)

    # falha nao altera dados do pedido existente
    fruta = Produto("F01", "Fruta", 150)
    pedido = Pedido()
    pedido.adicionar(fruta, "2")
    total_antes = pedido.total_centavos()
    try:
        calcular_pagamento("100,00", "Boleto")
    except ValueError:
        pass
    assert pedido.total_centavos() == total_antes

    return True


def verificar():
    pagamento = verificar_pagamento()
    preco = verificar_preco_para_centavos()
    modelos = verificar_modelos_preservado()
    previa = verificar_previa()
    return pagamento and preco and modelos and previa


if __name__ == "__main__":
    casos = [
        ("Pagamento (tabela + sem acumulo)", verificar_pagamento),
        ("Preco para centavos", verificar_preco_para_centavos),
        ("Modelos preservado (caso anterior)", verificar_modelos_preservado),
        ("Previa de pagamento", verificar_previa),
    ]
    todos = True
    for nome, fn in casos:
        resultado = fn()
        status = "OK" if resultado else "pendente"
        print(f"[{status}] {nome}")
        todos = todos and resultado
    if todos:
        print("Casos executados: previsoes e resultados conferem.")
    else:
        print("Verificacoes ainda incompletas.")
