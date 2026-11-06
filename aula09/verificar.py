# Complete os casos do registro; não marque sucesso sem verificá-los.
from modelos import Produto, Pedido, formatar
from pagamentos import calcular_pagamento


def verificar_adicionar():
    # regressao: caso anterior preservado
    fruta = Produto("F01", "Fruta", 150)
    leite = Produto("L01", "Leite", 300)
    pedido = Pedido()
    pedido.adicionar(fruta, "2")
    pedido.adicionar(leite, "3")
    assert pedido.itens[0].quantidade == 2
    assert pedido.itens[1].quantidade == 3
    assert pedido.total_centavos() == 1200

    # adicionar mesmo codigo incrementa — nao duplica
    pedido.adicionar(fruta, "1")
    assert len(pedido.itens) == 2
    assert pedido.itens[0].quantidade == 3
    assert pedido.total_centavos() == 1350

    return True


def verificar_atualizar():
    fruta = Produto("F01", "Fruta", 150)
    leite = Produto("L01", "Leite", 300)
    pedido = Pedido()
    pedido.adicionar(fruta, "2")
    pedido.adicionar(leite, "3")

    # atualizar substitui quantidade; nao soma
    total_antes = pedido.total_centavos()
    pedido.atualizar("F01", "5")
    assert pedido.itens[0].quantidade == 5
    assert pedido.total_centavos() != total_antes
    assert pedido.total_centavos() == 5 * 150 + 3 * 300

    # atualizar nao muda a ordem dos itens
    assert pedido.itens[0].produto.codigo == "F01"
    assert pedido.itens[1].produto.codigo == "L01"

    # codigo ausente levanta ValueError; pedido preservado
    itens_antes = len(pedido.itens)
    total_antes = pedido.total_centavos()
    try:
        pedido.atualizar("X99", "1")
        assert False, "deveria ter levantado ValueError"
    except ValueError as e:
        assert "nao esta no pedido" in str(e)
    assert len(pedido.itens) == itens_antes
    assert pedido.total_centavos() == total_antes

    # quantidade invalida levanta ValueError; pedido preservado
    try:
        pedido.atualizar("F01", "0")
        assert False, "deveria ter levantado ValueError"
    except ValueError:
        pass
    assert pedido.itens[0].quantidade == 5

    return True


def verificar_remover():
    fruta = Produto("F01", "Fruta", 150)
    leite = Produto("L01", "Leite", 300)
    creme = Produto("C01", "Creme", 250)
    pedido = Pedido()
    pedido.adicionar(fruta, "2")
    pedido.adicionar(leite, "3")
    pedido.adicionar(creme, "1")

    # remover item do meio; ordem dos restantes preservada
    pedido.remover("L01")
    assert len(pedido.itens) == 2
    assert pedido.itens[0].produto.codigo == "F01"
    assert pedido.itens[1].produto.codigo == "C01"
    assert pedido.total_centavos() == 2 * 150 + 1 * 250

    # remover ate vazio
    pedido.remover("F01")
    pedido.remover("C01")
    assert len(pedido.itens) == 0
    assert pedido.total_centavos() == 0

    # codigo ausente levanta ValueError
    try:
        pedido.remover("X99")
        assert False, "deveria ter levantado ValueError"
    except ValueError as e:
        assert "nao esta no pedido" in str(e)

    return True


def verificar_identidade():
    # codigo identifica o produto independente da posicao visual
    fruta = Produto("F01", "Fruta", 150)
    leite = Produto("L01", "Leite", 300)
    pedido = Pedido()
    pedido.adicionar(fruta, "1")
    pedido.adicionar(leite, "2")

    # mesmo que a ordem visual mude, atualizar por codigo acha o produto certo
    pedido.atualizar("L01", "5")
    assert pedido.itens[1].produto.codigo == "L01"
    assert pedido.itens[1].quantidade == 5
    # fruta nao foi alterada
    assert pedido.itens[0].quantidade == 1

    return True


def verificar_pedido_fechado():
    fruta = Produto("F01", "Fruta", 150)
    pedido = Pedido()
    pedido.adicionar(fruta, "1")
    pedido.aberto = False

    try:
        pedido.atualizar("F01", "2")
        assert False, "deveria ter levantado RuntimeError"
    except RuntimeError as e:
        assert "fechado" in str(e)

    try:
        pedido.remover("F01")
        assert False, "deveria ter levantado RuntimeError"
    except RuntimeError as e:
        assert "fechado" in str(e)

    # item nao foi alterado
    assert pedido.itens[0].quantidade == 1

    return True


def verificar_ordem_visual():
    # dados ficticios: tres produtos adicionados em ordem A, B, C
    alfa = Produto("A01", "Alfa", 100)
    beta = Produto("B01", "Beta", 200)
    gama = Produto("G01", "Gama", 300)
    pedido = Pedido()
    pedido.adicionar(alfa, "1")
    pedido.adicionar(beta, "1")
    pedido.adicionar(gama, "1")

    # simula mudanca de ordem visual: remove B01 e readiciona no final
    pedido.remover("B01")
    pedido.adicionar(beta, "1")

    # ordem visual agora e A01, G01, B01
    assert pedido.itens[0].produto.codigo == "A01"
    assert pedido.itens[1].produto.codigo == "G01"
    assert pedido.itens[2].produto.codigo == "B01"

    # atualizar por codigo ainda encontra o produto certo independente da posicao
    pedido.atualizar("B01", "4")
    assert pedido.itens[2].produto.codigo == "B01"
    assert pedido.itens[2].quantidade == 4

    # os outros nao foram alterados
    assert pedido.itens[0].quantidade == 1
    assert pedido.itens[1].quantidade == 1

    # total reflete posicoes corretas
    assert pedido.total_centavos() == 1 * 100 + 1 * 300 + 4 * 200

    return True


def verificar_selecao_ausente():
    # selecionar um codigo que nao esta no pedido deve levantar ValueError
    alfa = Produto("A01", "Alfa", 100)
    pedido = Pedido()
    pedido.adicionar(alfa, "2")

    # atualizar codigo ausente
    try:
        pedido.atualizar("Z99", "3")
        assert False, "deveria ter levantado ValueError"
    except ValueError as e:
        assert "nao esta no pedido" in str(e)

    # remover codigo ausente
    try:
        pedido.remover("Z99")
        assert False, "deveria ter levantado ValueError"
    except ValueError as e:
        assert "nao esta no pedido" in str(e)

    # pedido nao foi alterado
    assert len(pedido.itens) == 1
    assert pedido.itens[0].produto.codigo == "A01"
    assert pedido.itens[0].quantidade == 2

    return True


def verificar_previa_falsa():
    # previsao deliberadamente errada: espera total incorreto, captura a falha,
    # depois corrige a previsao e confirma sem alterar os dados reais
    alfa = Produto("A01", "Alfa", 100)
    beta = Produto("B01", "Beta", 200)
    pedido = Pedido()
    pedido.adicionar(alfa, "3")
    pedido.adicionar(beta, "2")
    # total real: 3*100 + 2*200 = 700

    # previsao falsa: esperamos 999 — deve falhar
    previsao_falsa_falhou = False
    try:
        assert pedido.total_centavos() == 999, "previsao falsa"
        previsao_falsa_falhou = False
    except AssertionError:
        previsao_falsa_falhou = True
    assert previsao_falsa_falhou, "a previsao falsa deveria ter falhado"

    # dados nao foram alterados pela tentativa errada
    assert len(pedido.itens) == 2
    assert pedido.itens[0].quantidade == 3
    assert pedido.itens[1].quantidade == 2

    # previsao correta passa
    assert pedido.total_centavos() == 700

    return True


def verificar():
    adicionar      = verificar_adicionar()
    atualizar      = verificar_atualizar()
    remover        = verificar_remover()
    identidade     = verificar_identidade()
    fechado        = verificar_pedido_fechado()
    ordem_visual   = verificar_ordem_visual()
    selecao_ausente = verificar_selecao_ausente()
    previa_falsa   = verificar_previa_falsa()
    return (adicionar and atualizar and remover and identidade
            and fechado and ordem_visual and selecao_ausente and previa_falsa)


if __name__ == "__main__":
    casos = [
        ("Adicionar (regressao)",        verificar_adicionar),
        ("Atualizar",                    verificar_atualizar),
        ("Remover ate vazio",            verificar_remover),
        ("Identidade por codigo",        verificar_identidade),
        ("Pedido fechado recusa tudo",   verificar_pedido_fechado),
        ("Ordem visual",                 verificar_ordem_visual),
        ("Selecao ausente",              verificar_selecao_ausente),
        ("Previa falsa capturada",       verificar_previa_falsa),
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
