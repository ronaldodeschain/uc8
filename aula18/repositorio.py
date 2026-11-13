# A14: assinaturas de apoio; traga sua implementação anterior.
from contextlib import closing
from pathlib import Path
import sqlite3

from banco import (
    CAMINHO_BANCO,
    atualizar_produto as _atualizar_produto,
    criar_banco,
    listar_produtos as _listar_produtos,
    remover_produto as _remover_produto,
    salvar_produto as _salvar_produto,
)


class RepositorioProdutos:
    """Contrato para repositórios de produtos, independente do armazenamento."""

    def listar(self):
        raise NotImplementedError

    def salvar(self, codigo, nome, preco):
        raise NotImplementedError

    def atualizar(self, codigo, nome, preco):
        raise NotImplementedError

    def remover(self, codigo):
        raise NotImplementedError


class ProdutosSQLite(RepositorioProdutos):
    """Adapter do contrato de produtos para o banco SQLite."""

    def __init__(self, caminho=CAMINHO_BANCO):
        self.caminho = caminho

    def iniciar(self):
        criar_banco(self.caminho)

    def listar(self):
        return _listar_produtos(self.caminho)

    def salvar(self, codigo, nome, preco):
        return _salvar_produto(codigo, nome, preco, self.caminho)

    def atualizar(self, codigo, nome, preco):
        return _atualizar_produto(codigo, nome, preco, self.caminho)

    def remover(self, codigo):
        return _remover_produto(codigo, self.caminho)


def validar_nome(nome):
    if not isinstance(nome, str) or not nome.strip():
        raise ValueError("O nome do produto não pode ser vazio.")
    return nome.strip()

def validar_id(codigo):
    if not isinstance(codigo, str) or not codigo.strip():
        raise ValueError("O código do produto não pode ser vazio.")
    return codigo.strip()

def validar_preco(preco):
    if type(preco) is not int or preco <= 0:
        raise ValueError("O preço deve ser um inteiro positivo em centavos.")
    return preco

class RepositorioSqlite:

    def __init__(self, caminho):
        """TODO A14: implemente __init__ conforme o contrato e reutilize seu código anterior."""
        raise NotImplementedError('Implemente e teste esta operação.')

    def conectar(self):
        """TODO A14: implemente conectar conforme o contrato e reutilize seu código anterior."""
        raise NotImplementedError('Implemente e teste esta operação.')

    def iniciar(self):
        """TODO A14: implemente iniciar conforme o contrato e reutilize seu código anterior."""
        raise NotImplementedError('Implemente e teste esta operação.')

    def adicionar_produto(self, nome, preco):
        """TODO A14: implemente adicionar_produto conforme o contrato e reutilize seu código anterior."""
        raise NotImplementedError('Implemente e teste esta operação.')

    def listar_produtos(self):
        """TODO A14: implemente listar_produtos conforme o contrato e reutilize seu código anterior."""
        raise NotImplementedError('Implemente e teste esta operação.')

    def adicionar_cliente(self, nome):
        """TODO A14: implemente adicionar_cliente conforme o contrato e reutilize seu código anterior."""
        raise NotImplementedError('Implemente e teste esta operação.')

    def listar_clientes(self):
        """TODO A14: implemente listar_clientes conforme o contrato e reutilize seu código anterior."""
        raise NotImplementedError('Implemente e teste esta operação.')
