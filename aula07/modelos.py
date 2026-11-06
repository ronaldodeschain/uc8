# A07: assinaturas de apoio; traga sua implementação anterior.
def quantidade(texto):
    """TODO A07: implemente quantidade conforme o contrato e reutilize seu código anterior."""
    valor = int(str(texto).strip())
    if valor <= 0:
        raise ValueError("Quantidade deve ser maior que zero.")
    if valor > 999:
        raise ValueError("Quantidade máxima é 999.")
    return valor

def formatar(centavos):
    """TODO A07: implemente formatar conforme o contrato e reutilize seu código anterior."""
    return f"R$ {centavos // 100},{centavos % 100:02d}"

class Produto:

    def __init__(self, codigo, nome, preco_centavos):
        """TODO A07: implemente __init__ conforme o contrato e reutilize seu código anterior."""
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
        """TODO A07: implemente __init__ conforme o contrato e reutilize 
        seu código anterior."""
        self.produto = produto
        self.quantidade = quantidade(texto_quantidade)

    def subtotal(self):
        """TODO A07: implemente subtotal conforme o contrato e reutilize 
        seu código anterior."""
        return self.produto.preco_centavos * self.quantidade

class Pedido:

    def __init__(self):
        """TODO A07: implemente __init__ conforme o contrato e reutilize 
        seu código anterior."""
        self.itens = {}
        self.aberto = True

    def exigir_aberto(self):
        """TODO A07: implemente exigir_aberto conforme o contrato e reutilize 
        seu código anterior."""
        if not self.aberto:
            raise RuntimeError("Pedido ja esta fechado.")

    def adicionar(self, produto, texto_quantidade):
        """TODO A07: implemente adicionar conforme o contrato e reutilize 
        seu código anterior."""
        self.exigir_aberto()
        qtd = quantidade(texto_quantidade)
        if produto.codigo in self.itens:
            novo_total = self.itens[produto.codigo].quantidade + qtd
            if novo_total > 999:
                raise ValueError("Quantidade máxima é 999.")
            self.itens[produto.codigo].quantidade = novo_total
        else:
            self.itens[produto.codigo] = Item(produto, texto_quantidade)

    def subtrair(self, produto, texto_quantidade):
        self.exigir_aberto()
        qtd = quantidade(texto_quantidade)
        if produto.codigo not in self.itens:
            raise ValueError(f"Produto '{produto.codigo}' não está no pedido.")
        novo_total = self.itens[produto.codigo].quantidade - qtd
        if novo_total < 0:
            raise ValueError("Quantidade não pode ser menor que zero.")
        if novo_total == 0:
            del self.itens[produto.codigo]
        else:
            self.itens[produto.codigo].quantidade = novo_total

    def total_centavos(self):
        """TODO A07: implemente total_centavos conforme o contrato e reutilize 
        seu código anterior."""
        return sum(item.subtotal() for item in self.itens.values())

    def linhas(self):
        """TODO A07: implemente linhas conforme o contrato e reutilize 
        seu código anterior."""
        resultado = []
        for item in self.itens.values():
            resultado.append(
                f"{item.produto.codigo} {item.produto.nome} "
                f"x{item.quantidade} = {formatar(item.subtotal())}"
            )
        resultado.append(f"Total: {formatar(self.total_centavos())}")
        return resultado
