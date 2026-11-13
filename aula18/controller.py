# A16: assinaturas de apoio; traga sua implementação anterior.
from pagamento import preco_para_centavos
from repositorio import validar_id, validar_nome, validar_preco


class ProdutoController:
    """Valida e encaminha operações de produtos ao repositório."""

    def __init__(self, repositorio):
        self.repositorio = repositorio

    def listar_produtos(self):
        return self.repositorio.listar()

    def salvar_produto(self, codigo, nome, preco):
        codigo = validar_id(codigo)
        nome = validar_nome(nome)
        preco = validar_preco(preco)
        return self.repositorio.salvar(codigo, nome, preco)

    def atualizar_produto(self, codigo, nome, preco):
        codigo = validar_id(codigo)
        nome = validar_nome(nome)
        preco = validar_preco(preco)
        return self.repositorio.atualizar(codigo, nome, preco)

    def remover_produto(self, codigo):
        codigo = validar_id(codigo)
        return self.repositorio.remover(codigo)

class CadastroController:

    def __init__(self, repositorio):
        """TODO A16: implemente __init__ conforme o contrato e reutilize seu código anterior."""
        raise NotImplementedError('Implemente e teste esta operação.')

    def listar(self, tipo):
        """TODO A16: implemente listar conforme o contrato e reutilize seu código anterior."""
        raise NotImplementedError('Implemente e teste esta operação.')

    def salvar(self, tipo, nome, preco_texto='', codigo=None):
        """TODO A16: implemente salvar conforme o contrato e reutilize seu código anterior."""
        raise NotImplementedError('Implemente e teste esta operação.')

    def excluir(self, tipo, codigo, confirmado):
        """TODO A16: implemente excluir conforme o contrato e reutilize seu código anterior."""
        raise NotImplementedError('Implemente e teste esta operação.')
