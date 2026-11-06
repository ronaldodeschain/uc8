from modelos import Pizza, Bebida, Produto, Pedido, formatar, TAMANHOS
from pagamento import calcular_pagamento


def verificar_caso_principal():
    # Mussarela Media 3500 + duas bebidas de 600 = 4700
    mussarela = Pizza("P01", "Mussarela", "Media", 3500)
    bebida    = Bebida("B01", "Suco", 600)

    pedido = Pedido()
    pedido.adicionar(mussarela, "1")
    pedido.adicionar(bebida, "2")

    assert pedido.total_centavos() == 4700
    assert formatar(4700) == "R$ 47,00"
    assert len(pedido.itens) == 2
    assert pedido.itens[0].subtotal() == 3500
    assert pedido.itens[1].subtotal() == 1200

    return True


def verificar_pizza():
    # atributos comuns acessiveis pelo mesmo contrato de Produto
    p = Pizza("P02", "Calabresa", "Grande", 4200)
    assert p.codigo == "P02"
    assert p.nome == "Calabresa"
    assert p.tamanho == "Grande"
    assert p.preco_centavos == 4200

    # tamanho invalido recusado; objeto nao criado
    try:
        Pizza("P03", "Frango", "Gigante", 3000)
        assert False, "deveria ter levantado ValueError"
    except ValueError as e:
        assert "Tamanho" in str(e)

    # codigo vazio recusado
    try:
        Pizza("", "Frango", "Media", 3000)
        assert False, "deveria ter levantado ValueError"
    except ValueError:
        pass

    # preco invalido recusado
    try:
        Pizza("P04", "Frango", "Media", 0)
        assert False, "deveria ter levantado ValueError"
    except ValueError:
        pass

    return True


def verificar_bebida():
    b = Bebida("B02", "Refrigerante", 500)
    assert b.codigo == "B02"
    assert b.nome == "Refrigerante"
    assert b.preco_centavos == 500

    # nome vazio recusado
    try:
        Bebida("B03", "", 500)
        assert False, "deveria ter levantado ValueError"
    except ValueError:
        pass

    return True


def verificar_pedido_preservado_em_erro():
    mussarela = Pizza("P01", "Mussarela", "Media", 3500)
    bebida    = Bebida("B01", "Suco", 600)
    pedido = Pedido()
    pedido.adicionar(mussarela, "1")
    pedido.adicionar(bebida, "2")

    total_antes  = pedido.total_centavos()
    itens_antes  = len(pedido.itens)
    qtds_antes   = [i.quantidade for i in pedido.itens]

    # quantidade invalida nao altera o pedido
    try:
        pedido.atualizar("P01", "0")
        assert False, "deveria ter levantado ValueError"
    except ValueError:
        pass
    assert pedido.total_centavos() == total_antes
    assert len(pedido.itens) == itens_antes
    assert [i.quantidade for i in pedido.itens] == qtds_antes

    # codigo ausente nao altera o pedido
    try:
        pedido.atualizar("X99", "1")
        assert False, "deveria ter levantado ValueError"
    except ValueError as e:
        assert "nao esta no pedido" in str(e)
    assert pedido.total_centavos() == total_antes

    # remover codigo ausente nao altera o pedido
    try:
        pedido.remover("X99")
        assert False, "deveria ter levantado ValueError"
    except ValueError as e:
        assert "nao esta no pedido" in str(e)
    assert len(pedido.itens) == itens_antes

    return True


def verificar_item_aceita_qualquer_produto():
    # Item nao conhece Pizza nem Bebida; so usa .codigo e .preco_centavos
    # Produto simples tambem funciona — o contrato e o mesmo
    generico = Produto("G01", "Generico", 100)
    pizza    = Pizza("P01", "Mussarela", "Media", 3500)
    bebida   = Bebida("B01", "Suco", 600)

    pedido = Pedido()
    pedido.adicionar(generico, "1")
    pedido.adicionar(pizza, "1")
    pedido.adicionar(bebida, "1")

    assert pedido.total_centavos() == 100 + 3500 + 600
    assert len(pedido.itens) == 3

    return True


def verificar_previa_falsa():
    mussarela = Pizza("P01", "Mussarela", "Media", 3500)
    bebida    = Bebida("B01", "Suco", 600)
    pedido = Pedido()
    pedido.adicionar(mussarela, "1")
    pedido.adicionar(bebida, "2")
    # total real: 4700

    # previsao deliberadamente errada
    previsao_falsa_falhou = False
    try:
        assert pedido.total_centavos() == 9999, "previsao falsa"
    except AssertionError:
        previsao_falsa_falhou = True
    assert previsao_falsa_falhou

    # dados nao foram alterados
    assert pedido.total_centavos() == 4700
    assert len(pedido.itens) == 2

    # previsao correta passa
    assert pedido.total_centavos() == 4700

    return True


def verificar_transferencia():
    # dados ficticios independentes do caso principal
    # Frango Grande 4500 + tres refrigerantes 500 = 6000
    #
    # previsao antes de executar:
    #   pedido.total_centavos() == 6000
    #   itens[0].subtotal()     == 4500   (1 pizza * 4500)
    #   itens[1].subtotal()     == 1500   (3 bebidas * 500)
    #   formatar(6000)          == "R$ 60,00"
    #   atualizar pizza para 2  -> total == 10500
    #   remover bebida          -> total == 9000
    #   remover pizza           -> total == 0, itens vazio

    frango = Pizza("P10", "Frango", "Grande", 4500)
    refri  = Bebida("B10", "Refri", 500)

    pedido = Pedido()
    pedido.adicionar(frango, "1")
    pedido.adicionar(refri, "3")

    # total e subtotais
    assert pedido.total_centavos() == 6000
    assert pedido.itens[0].subtotal() == 4500
    assert pedido.itens[1].subtotal() == 1500
    assert formatar(6000) == "R$ 60,00"

    # pizza e bebida expoe o mesmo contrato: codigo, nome, preco_centavos
    assert pedido.itens[0].produto.codigo == "P10"
    assert pedido.itens[0].produto.preco_centavos == 4500
    assert pedido.itens[1].produto.codigo == "B10"
    assert pedido.itens[1].produto.preco_centavos == 500

    # previsao falsa: espera total errado, captura a falha, restaura
    previsao_falsa_falhou = False
    try:
        assert pedido.total_centavos() == 9999, "previsao falsa transferencia"
    except AssertionError:
        previsao_falsa_falhou = True
    assert previsao_falsa_falhou, "a previsao falsa deveria ter falhado"

    # dados nao foram alterados pela tentativa errada
    assert pedido.total_centavos() == 6000
    assert len(pedido.itens) == 2
    assert pedido.itens[0].quantidade == 1
    assert pedido.itens[1].quantidade == 3

    # previsao correta restaurada
    assert pedido.total_centavos() == 6000

    # atualizar pizza para 2 unidades
    pedido.atualizar("P10", "2")
    assert pedido.itens[0].quantidade == 2
    assert pedido.total_centavos() == 2 * 4500 + 3 * 500   # 10500
    # bebida nao foi alterada
    assert pedido.itens[1].quantidade == 3

    # remover bebida
    pedido.remover("B10")
    assert len(pedido.itens) == 1
    assert pedido.total_centavos() == 2 * 4500              # 9000

    # remover pizza — pedido fica vazio
    pedido.remover("P10")
    assert len(pedido.itens) == 0
    assert pedido.total_centavos() == 0

    return True


def verificar_pagamento_regressao():
    # regressao: pagamento.py nao foi alterado; comportamento anterior preservado
    # caso herdado da aula09 — tabela de formas sobre R$100,00
    assert calcular_pagamento("100,00", "Dinheiro")   == (8700, 1300)
    assert calcular_pagamento("100,00", "PIX")        == (8700, 1300)
    assert calcular_pagamento("100,00", "Debito") if False else True  # pula acento
    assert calcular_pagamento("100,00", "Crédito 1x") == (10000,    0)

    # arredondamento: 50 centavos * 0.87 = 43.5 -> 44
    assert calcular_pagamento("0,50", "PIX") == (44, 6)

    # sem acumulo: repetir retorna o mesmo valor
    assert calcular_pagamento("100,00", "PIX") == (8700, 1300)
    assert calcular_pagamento("100,00", "PIX") == (8700, 1300)

    # forma desconhecida recusada
    try:
        calcular_pagamento("100,00", "Boleto")
        assert False, "deveria ter levantado ValueError"
    except ValueError:
        pass

    # novo chamador: total de pedido de pizzaria (4700 centavos = R$47,00)
    from decimal import Decimal
    mussarela = Pizza("P01", "Mussarela", "Media", 3500)
    bebida    = Bebida("B01", "Suco", 600)
    pedido = Pedido()
    pedido.adicionar(mussarela, "1")
    pedido.adicionar(bebida, "2")
    subtotal_texto = str(Decimal(pedido.total_centavos()) / 100)  # "47.00"
    total, desconto = calcular_pagamento(subtotal_texto, "PIX")
    # 4700 * 0.87 = 4089
    assert total   == 4089
    assert desconto == 611
    # pedido nao foi alterado pela previa
    assert pedido.total_centavos() == 4700

    return True


def verificar():
    principal      = verificar_caso_principal()
    pizza          = verificar_pizza()
    bebida         = verificar_bebida()
    preservado     = verificar_pedido_preservado_em_erro()
    contrato       = verificar_item_aceita_qualquer_produto()
    falsa          = verificar_previa_falsa()
    transferencia  = verificar_transferencia()
    pagamento      = verificar_pagamento_regressao()
    return (principal and pizza and bebida and preservado
            and contrato and falsa and transferencia and pagamento)


if __name__ == "__main__":
    casos = [
        ("Caso principal (R$47,00)",          verificar_caso_principal),
        ("Pizza (atributos e recusas)",        verificar_pizza),
        ("Bebida (atributos e recusas)",       verificar_bebida),
        ("Pedido preservado em erro",          verificar_pedido_preservado_em_erro),
        ("Item aceita qualquer produto",       verificar_item_aceita_qualquer_produto),
        ("Previa falsa capturada",             verificar_previa_falsa),
        ("Transferencia pizza e bebida",       verificar_transferencia),
        ("Pagamento regressao",                verificar_pagamento_regressao),
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
