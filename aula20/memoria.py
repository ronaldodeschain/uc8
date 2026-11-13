# A16: assinaturas de apoio; traga sua implementação anterior.
from copy import deepcopy
from repositorio import RepositorioProdutos, validar_nome, validar_preco, validar_id


class ProdutosMemoria(RepositorioProdutos):
    """Repositório de produtos em memória com o mesmo contrato do SQLite."""

    def __init__(self):
        self.produtos = {}

    def listar(self):
        return list(self.produtos.values())

    def salvar(self, codigo, nome, preco):
        codigo = validar_id(codigo)
        if codigo in self.produtos:
            raise ValueError(f"O produto '{codigo}' já existe.")
        self.produtos[codigo] = (
            codigo,
            validar_nome(nome),
            validar_preco(preco),
        )

    def atualizar(self, codigo, nome, preco):
        codigo = validar_id(codigo)
        if codigo not in self.produtos:
            return False
        self.produtos[codigo] = (
            codigo,
            validar_nome(nome),
            validar_preco(preco),
        )
        return True

    def remover(self, codigo):
        codigo = validar_id(codigo)
        return self.produtos.pop(codigo, None) is not None

class RepositorioMemoria:

    def __init__(self):
        """TODO A16: implemente __init__ conforme o contrato e reutilize seu código anterior."""
        raise NotImplementedError('Implemente e teste esta operação.')

    def adicionar_produto(self, nome, preco):
        """TODO A16: implemente adicionar_produto conforme o contrato e reutilize seu código anterior."""
        raise NotImplementedError('Implemente e teste esta operação.')

    def listar_produtos(self):
        """TODO A16: implemente listar_produtos conforme o contrato e reutilize seu código anterior."""
        raise NotImplementedError('Implemente e teste esta operação.')

    def editar_produto(self, codigo, nome, preco):
        """TODO A16: implemente editar_produto conforme o contrato e reutilize seu código anterior."""
        raise NotImplementedError('Implemente e teste esta operação.')

    def excluir_produto(self, codigo, confirmado=False):
        """TODO A16: implemente excluir_produto conforme o contrato e reutilize seu código anterior."""
        raise NotImplementedError('Implemente e teste esta operação.')

    def adicionar_cliente(self, nome):
        """TODO A16: implemente adicionar_cliente conforme o contrato e reutilize seu código anterior."""
        raise NotImplementedError('Implemente e teste esta operação.')

    def listar_clientes(self):
        """TODO A16: implemente listar_clientes conforme o contrato e reutilize seu código anterior."""
        raise NotImplementedError('Implemente e teste esta operação.')

    def editar_cliente(self, codigo, nome):
        """TODO A16: implemente editar_cliente conforme o contrato e reutilize seu código anterior."""
        raise NotImplementedError('Implemente e teste esta operação.')

    def excluir_cliente(self, codigo, confirmado=False):
        """TODO A16: implemente excluir_cliente conforme o contrato e reutilize seu código anterior."""
        raise NotImplementedError('Implemente e teste esta operação.')
