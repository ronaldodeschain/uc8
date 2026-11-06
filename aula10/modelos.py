def quantidade(texto):
    valor = int(str(texto).strip())
    if valor <= 0:
        raise ValueError("Quantidade deve ser maior que zero.")
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


TAMANHOS = ("Media", "Grande")


class Pizza:
    """Produto com tamanho. Usa Produto internamente para os dados comuns."""

    def __init__(self, codigo, nome, tamanho, preco_centavos):
        if tamanho not in TAMANHOS:
            raise ValueError(f"Tamanho deve ser um de {TAMANHOS}.")
        self._produto = Produto(codigo, nome, preco_centavos)
        self.tamanho = tamanho

    @property
    def codigo(self):
        return self._produto.codigo

    @property
    def nome(self):
        return self._produto.nome

    @property
    def preco_centavos(self):
        return self._produto.preco_centavos


class Bebida:
    """Produto sem tamanho. Usa Produto internamente para os dados comuns."""

    def __init__(self, codigo, nome, preco_centavos):
        self._produto = Produto(codigo, nome, preco_centavos)

    @property
    def codigo(self):
        return self._produto.codigo

    @property
    def nome(self):
        return self._produto.nome

    @property
    def preco_centavos(self):
        return self._produto.preco_centavos


class Item:

    def __init__(self, produto, texto_quantidade):
        self.produto = produto
        self.quantidade = quantidade(texto_quantidade)

    def subtotal(self):
        return self.produto.preco_centavos * self.quantidade


class Pedido:

    def __init__(self):
        self.itens = []
        self.aberto = True

    def exigir_aberto(self):
        if not self.aberto:
            raise RuntimeError("Pedido ja esta fechado.")

    def adicionar(self, produto, texto_quantidade):
        self.exigir_aberto()
        qtd = quantidade(texto_quantidade)
        for item in self.itens:
            if item.produto.codigo == produto.codigo:
                item.quantidade += qtd
                return
        self.itens.append(Item(produto, texto_quantidade))

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

    def atualizar(self, codigo, texto_quantidade):
        self.exigir_aberto()
        nova_qtd = quantidade(texto_quantidade)
        for item in self.itens:
            if item.produto.codigo == codigo:
                item.quantidade = nova_qtd
                return
        raise ValueError(f"Codigo '{codigo}' nao esta no pedido.")

    def remover(self, codigo):
        self.exigir_aberto()
        for item in self.itens:
            if item.produto.codigo == codigo:
                self.itens.remove(item)
                return
        raise ValueError(f"Codigo '{codigo}' nao esta no pedido.")
