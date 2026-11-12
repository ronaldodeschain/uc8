"""A12 — modelos reutilizados da aula anterior."""
from decimal import Decimal
from pagamento import calcular_pagamento


def quantidade(texto):
    valor = int(str(texto).strip())
    if valor <= 0:
        raise ValueError("Quantidade deve ser maior que zero.")
    if valor > 999:
        raise ValueError("Quantidade máxima é 999.")
    return valor


def formatar(centavos):
    return f"R$ {centavos // 100},{centavos % 100:02d}"


class Produto:

    def __init__(self, codigo, nome, preco_centavos):
        codigo = str(codigo).strip()
        nome = str(nome).strip()
        if not codigo or not nome:
            raise ValueError("Codigo e nome nao podem ser vazios.")
        if not isinstance(preco_centavos, int) or preco_centavos <= 0:
            raise ValueError("Preco deve ser inteiro positivo em centavos.")
        self.codigo = codigo
        self.nome = nome
        self.preco_centavos = preco_centavos


class Item:

    def __init__(self, produto, texto_quantidade):
        self.produto = produto
        self.quantidade = quantidade(texto_quantidade)

    def subtotal(self):
        return self.produto.preco_centavos * self.quantidade


class Comprovante:
    """Retrato imutavel do pedido no momento da confirmacao."""

    def __init__(self, linhas, total_centavos, forma):
        self.linhas = list(linhas)
        self.total_centavos = total_centavos
        self.forma = forma


class Pedido:

    def __init__(self):
        self.itens = []
        self.aberto = True
        self._versao = 0

    def versao(self):
        return self._versao

    def exigir_aberto(self):
        if not self.aberto:
            raise RuntimeError("Pedido ja esta finalizado.")

    def adicionar(self, produto, texto_quantidade):
        self.exigir_aberto()
        qtd = quantidade(texto_quantidade)
        for item in self.itens:
            if item.produto.codigo == produto.codigo:
                if item.quantidade + qtd > 999:
                    raise ValueError("Quantidade máxima é 999.")
                item.quantidade += qtd
                self._versao += 1
                return
        self.itens.append(Item(produto, texto_quantidade))
        self._versao += 1

    def atualizar(self, codigo, texto_quantidade):
        self.exigir_aberto()
        nova_qtd = quantidade(texto_quantidade)
        for item in self.itens:
            if item.produto.codigo == codigo:
                item.quantidade = nova_qtd
                self._versao += 1
                return
        raise ValueError(f"Codigo '{codigo}' nao esta no pedido.")

    def remover(self, codigo):
        self.exigir_aberto()
        for item in self.itens:
            if item.produto.codigo == codigo:
                self.itens.remove(item)
                self._versao += 1
                return
        raise ValueError(f"Codigo '{codigo}' nao esta no pedido.")

    def total_centavos(self):
        return sum(item.subtotal() for item in self.itens)

    def linhas(self):
        resultado = []
        for item in self.itens:
            resultado.append(
                f"{item.produto.codigo} {item.produto.nome} "
                f"x{item.quantidade} = {formatar(item.subtotal())}"
            )
        resultado.append(f"Total: {formatar(self.total_centavos())}")
        return resultado

    def finalizar(self, forma, confirmado):
        self.exigir_aberto()
        if not self.itens:
            raise ValueError("Pedido vazio. Adicione itens antes de finalizar.")
        if confirmado != self._versao:
            raise ValueError(
                "Pedido alterado desde a ultima previa. Solicite uma nova previa."
            )
        subtotal_texto = str(Decimal(self.total_centavos()) / 100)
        total_pag, desconto = calcular_pagamento(subtotal_texto, forma)
        comprovante = Comprovante(self.linhas(), total_pag, forma)
        self.aberto = False
        return comprovante

    def novo(self):
        self.itens = []
        self.aberto = True
        self._versao = 0
