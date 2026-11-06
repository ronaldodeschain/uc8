from modelos import Pizza, Bebida, Produto, Pedido, Comprovante, formatar, TAMANHOS
from pagamento import calcular_pagamento


def verificar_cancelar():
    # novo() em montagem descarta itens e reinicia versao
    mussarela = Pizza("PM1", "Mussarela", "Media", 3500)
    bebida    = Bebida("B01", "Suco", 600)
    pedido = Pedido()
    pedido.adicionar(mussarela, "1")
    pedido.adicionar(bebida, "2")
    assert pedido.total_centavos() == 4700
    versao_antes = pedido.versao()

    pedido.novo()

    assert len(pedido.itens) == 0
    assert pedido.total_centavos() == 0
    assert pedido.aberto is True
    assert pedido.versao() == 0
    # versao zerou — diferente da versao antes do cancelamento
    assert pedido.versao() != versao_antes

    return True


def verificar_confirmar():
    # fluxo normal: previa -> confirmar -> comprovante independente
    mussarela = Pizza("PM1", "Mussarela", "Media", 3500)
    bebida    = Bebida("B01", "Suco", 600)
    pedido = Pedido()
    pedido.adicionar(mussarela, "1")
    pedido.adicionar(bebida, "2")
    assert pedido.total_centavos() == 4700

    # guarda versao no momento da previa
    versao_previa = pedido.versao()

    comprovante = pedido.finalizar("PIX", versao_previa)

    # pedido esta finalizado
    assert pedido.aberto is False

    # comprovante e independente: tem seus proprios dados
    assert isinstance(comprovante, Comprovante)
    assert comprovante.total_centavos == 4700
    assert comprovante.forma == "PIX"
    assert any("Mussarela" in l for l in comprovante.linhas)
    assert any("Suco" in l for l in comprovante.linhas)

    return True


def verificar_repetir_finalizacao():
    # finalizar um pedido ja finalizado levanta RuntimeError
    mussarela = Pizza("PM1", "Mussarela", "Media", 3500)
    pedido = Pedido()
    pedido.adicionar(mussarela, "1")
    versao_previa = pedido.versao()
    pedido.finalizar("PIX", versao_previa)
    assert pedido.aberto is False

    # segunda tentativa de finalizar
    try:
        pedido.finalizar("PIX", versao_previa)
        assert False, "deveria ter levantado RuntimeError"
    except RuntimeError as e:
        assert "finalizado" in str(e)

    # adicionar tambem recusado
    try:
        pedido.adicionar(mussarela, "1")
        assert False, "deveria ter levantado RuntimeError"
    except RuntimeError:
        pass

    return True


def verificar_previa_desatualizada():
    # pedido muda apos a previa: finalizar com versao antiga deve falhar
    mussarela = Pizza("PM1", "Mussarela", "Media", 3500)
    bebida    = Bebida("B01", "Suco", 600)
    pedido = Pedido()
    pedido.adicionar(mussarela, "1")

    # usuario abre a previa aqui
    versao_previa = pedido.versao()

    # usuario acrescenta item depois de abrir a previa
    pedido.adicionar(bebida, "2")

    # versao mudou
    assert pedido.versao() != versao_previa

    # tentar confirmar com versao antiga deve falhar
    try:
        pedido.finalizar("PIX", versao_previa)
        assert False, "deveria ter levantado ValueError"
    except ValueError as e:
        assert "previa" in str(e).lower() or "alterado" in str(e).lower()

    # pedido continua em montagem com os dois itens
    assert pedido.aberto is True
    assert len(pedido.itens) == 2
    assert pedido.total_centavos() == 3500 + 2 * 600

    return True


def verificar_comprovante_independente():
    # comprovante nao muda quando novo pedido comeca
    mussarela = Pizza("PM1", "Mussarela", "Media", 3500)
    pedido = Pedido()
    pedido.adicionar(mussarela, "1")
    versao_previa = pedido.versao()
    comprovante = pedido.finalizar("Dinheiro", versao_previa)

    total_comprovante = comprovante.total_centavos
    linhas_comprovante = list(comprovante.linhas)

    # inicia novo pedido com itens diferentes
    pedido.novo()
    calabresa = Pizza("PM2", "Calabresa", "Grande", 4800)
    pedido.adicionar(calabresa, "3")

    # comprovante nao foi alterado
    assert comprovante.total_centavos == total_comprovante
    assert comprovante.linhas == linhas_comprovante
    assert comprovante.forma == "Dinheiro"

    return True


def verificar_vazio_nao_finaliza():
    # pedido vazio nao pode ser finalizado
    pedido = Pedido()
    try:
        pedido.finalizar("PIX", pedido.versao())
        assert False, "deveria ter levantado ValueError"
    except ValueError as e:
        assert "vazio" in str(e).lower()
    assert pedido.aberto is True

    return True


def verificar_novo_apos_finalizado():
    # novo() apos finalizacao reinicia o pedido para montagem
    mussarela = Pizza("PM1", "Mussarela", "Media", 3500)
    pedido = Pedido()
    pedido.adicionar(mussarela, "1")
    pedido.finalizar("PIX", pedido.versao())
    assert pedido.aberto is False

    pedido.novo()
    assert pedido.aberto is True
    assert len(pedido.itens) == 0
    assert pedido.versao() == 0

    # pode adicionar normalmente apos novo()
    bebida = Bebida("B01", "Suco", 600)
    pedido.adicionar(bebida, "1")
    assert pedido.total_centavos() == 600

    return True


def verificar_regressao_aula10():
    # regressao: comportamento de Pizza, Bebida e Pedido preservado
    frango = Pizza("PG3", "Frango", "Grande", 4600)
    refri  = Bebida("B02", "Refrigerante", 500)
    pedido = Pedido()
    pedido.adicionar(frango, "1")
    pedido.adicionar(refri, "2")
    assert pedido.total_centavos() == 4600 + 2 * 500   # 5600

    pedido.atualizar("PG3", "2")
    assert pedido.itens[0].quantidade == 2
    assert pedido.total_centavos() == 2 * 4600 + 2 * 500  # 10200

    pedido.remover("B02")
    assert len(pedido.itens) == 1
    assert pedido.total_centavos() == 2 * 4600  # 9200

    # tamanho invalido ainda recusado
    try:
        Pizza("X", "X", "Mini", 100)
        assert False, "deveria ter levantado ValueError"
    except ValueError:
        pass

    return True


def verificar_estados_sequencia():
    # dados ficticios independentes dos outros casos
    # Calabresa Grande 4800 + dois sucos 600 = 6000
    #
    # previsao antes de executar:
    #   cancelar em montagem -> itens=0, versao=0, aberto=True
    #   confirmar com versao correta -> comprovante.total=6000, aberto=False
    #   repetir finalizacao -> RuntimeError com "finalizado"
    #   previa desatualizada -> ValueError, pedido preservado em montagem

    calabresa = Pizza("PG2", "Calabresa", "Grande", 4800)
    suco      = Bebida("B01", "Suco", 600)

    # --- cancelar em montagem ---
    pedido = Pedido()
    pedido.adicionar(calabresa, "1")
    pedido.adicionar(suco, "2")
    assert pedido.total_centavos() == 6000
    assert len(pedido.itens) == 2
    versao_montagem = pedido.versao()
    assert versao_montagem > 0

    # previsao falsa: espera que cancelar mantenha os itens
    previsao_falsa_falhou = False
    pedido.novo()   # cancela
    try:
        assert len(pedido.itens) == 2, "previsao falsa: itens deveriam ter sido descartados"
    except AssertionError:
        previsao_falsa_falhou = True
    assert previsao_falsa_falhou, "a previsao falsa deveria ter falhado"

    # previsao correta: itens zerados, versao zerada, aberto
    assert len(pedido.itens) == 0
    assert pedido.total_centavos() == 0
    assert pedido.versao() == 0
    assert pedido.aberto is True

    # --- confirmar com versao correta ---
    pedido.adicionar(calabresa, "1")
    pedido.adicionar(suco, "2")
    assert pedido.total_centavos() == 6000

    versao_previa = pedido.versao()
    comprovante = pedido.finalizar("PIX", versao_previa)

    assert pedido.aberto is False
    assert isinstance(comprovante, Comprovante)
    assert comprovante.total_centavos == 6000
    assert comprovante.forma == "PIX"
    assert any("Calabresa" in l for l in comprovante.linhas)
    assert any("Suco" in l for l in comprovante.linhas)

    # --- repetir finalizacao recusada ---
    try:
        pedido.finalizar("PIX", versao_previa)
        assert False, "deveria ter levantado RuntimeError"
    except RuntimeError as e:
        assert "finalizado" in str(e)

    # estado nao mudou
    assert pedido.aberto is False
    assert comprovante.total_centavos == 6000

    # --- previa desatualizada: novo pedido, muda apos abrir previa ---
    pedido.novo()
    assert pedido.aberto is True

    pedido.adicionar(calabresa, "1")
    versao_previa_antiga = pedido.versao()   # previa aberta aqui

    pedido.adicionar(suco, "1")              # pedido muda depois
    assert pedido.versao() != versao_previa_antiga

    itens_antes = len(pedido.itens)
    total_antes = pedido.total_centavos()

    try:
        pedido.finalizar("PIX", versao_previa_antiga)
        assert False, "deveria ter levantado ValueError"
    except ValueError as e:
        assert "previa" in str(e).lower() or "alterado" in str(e).lower()

    # pedido preservado em montagem
    assert pedido.aberto is True
    assert len(pedido.itens) == itens_antes
    assert pedido.total_centavos() == total_antes

    # previsao correta: confirmar com versao atual passa
    versao_atual = pedido.versao()
    comprovante2 = pedido.finalizar("Dinheiro", versao_atual)
    assert comprovante2.total_centavos == 4800 + 600
    assert comprovante2.forma == "Dinheiro"
    assert pedido.aberto is False

    return True


def verificar_pagamento_regressao():
    # regressao: pagamento.py nao foi alterado pela mudanca de estados
    # caso herdado da aula10 — tabela de formas sobre R$100,00
    assert calcular_pagamento("100,00", "Dinheiro")   == (8700, 1300)
    assert calcular_pagamento("100,00", "PIX")        == (8700, 1300)
    assert calcular_pagamento("100,00", "Cr\u00e9dito 1x") == (10000,    0)

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

    # novo chamador: pedido passa pelo fluxo completo de estados
    from decimal import Decimal
    mussarela = Pizza("PM1", "Mussarela", "Media", 3500)
    bebida    = Bebida("B01", "Suco", 600)
    pedido = Pedido()
    pedido.adicionar(mussarela, "1")
    pedido.adicionar(bebida, "2")
    # total: 4700; guarda versao e finaliza
    versao_previa = pedido.versao()
    comprovante = pedido.finalizar("PIX", versao_previa)
    assert comprovante.total_centavos == 4700

    # calcula pagamento sobre o total do comprovante
    subtotal_texto = str(Decimal(comprovante.total_centavos) / 100)  # "47.00"
    total, desconto = calcular_pagamento(subtotal_texto, "PIX")
    # 4700 * 0.87 = 4089
    assert total    == 4089
    assert desconto == 611

    # comprovante nao foi alterado pela chamada ao pagamento
    assert comprovante.total_centavos == 4700
    assert comprovante.forma == "PIX"

    # novo pedido apos finalizacao — pagamento ainda funciona normalmente
    pedido.novo()
    assert calcular_pagamento("100,00", "PIX") == (8700, 1300)

    return True


def verificar():
    cancelar       = verificar_cancelar()
    confirmar      = verificar_confirmar()
    repetir        = verificar_repetir_finalizacao()
    desatualizada  = verificar_previa_desatualizada()
    independente   = verificar_comprovante_independente()
    vazio          = verificar_vazio_nao_finaliza()
    novo_apos      = verificar_novo_apos_finalizado()
    regressao      = verificar_regressao_aula10()
    pagamento      = verificar_pagamento_regressao()
    estados        = verificar_estados_sequencia()
    return (cancelar and confirmar and repetir and desatualizada
            and independente and vazio and novo_apos and regressao
            and pagamento and estados)


if __name__ == "__main__":
    casos = [
        ("Cancelar (novo em montagem)",          verificar_cancelar),
        ("Confirmar (fluxo normal)",              verificar_confirmar),
        ("Repetir finalizacao recusada",          verificar_repetir_finalizacao),
        ("Previa desatualizada recusada",         verificar_previa_desatualizada),
        ("Comprovante independente do pedido",    verificar_comprovante_independente),
        ("Vazio nao finaliza",                    verificar_vazio_nao_finaliza),
        ("Novo apos finalizado",                  verificar_novo_apos_finalizado),
        ("Regressao aula10",                      verificar_regressao_aula10),
        ("Pagamento regressao",                   verificar_pagamento_regressao),
        ("Estados sequencia completa",            verificar_estados_sequencia),
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
