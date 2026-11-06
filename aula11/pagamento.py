from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

FATORES = {'Dinheiro': '0.87', 'PIX': '0.87', 'Débito': '0.92', 'Crédito 1x': '1.00'}


def valor_monetario(texto, permitir_zero=True):
    texto = str(texto).strip().replace(",", ".")
    try:
        valor = Decimal(texto)
    except InvalidOperation:
        raise ValueError(f"Valor monetario invalido: '{texto}'.")
    if valor < 0:
        raise ValueError("Valor nao pode ser negativo.")
    if not permitir_zero and valor == 0:
        raise ValueError("Valor nao pode ser zero.")
    return valor


def calcular_pagamento(subtotal_texto, forma):
    if forma not in FATORES:
        raise ValueError(f"Forma de pagamento desconhecida: '{forma}'.")
    base = valor_monetario(subtotal_texto, permitir_zero=True)
    base_centavos = (base * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    fator = Decimal(FATORES[forma])
    total = (base_centavos * fator).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    desconto = base_centavos - total
    return int(total), int(desconto)


def preco_para_centavos(texto):
    valor = valor_monetario(texto, permitir_zero=False)
    centavos = (valor * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(centavos)
