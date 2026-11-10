"""A12 — leitura e gravação segura do catálogo JSON."""
from pathlib import Path
import json
import os
import tempfile
from modelos import Produto

def carregar_catalogo(caminho):
    """Lê o catálogo em caminho.

    Se o arquivo não existir, retorna uma lista vazia.
    Se o arquivo estiver corrompido, levanta ValueError.
    """
    try:
        with open(caminho,"r",encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        catalogo = []
        
        for item in dados:
            catalogo.append(Produto(
                item["id"],
                item["nome"],
                item["preco_centavos"]))

        return True, "Catalogo carregado",catalogo
    
    except FileNotFoundError:
        return False, "Arquivo não encontrado", []
    
    except json.JSONDecodeError as e:
        return False, f"Erro de sintaxe JSON: {e}", []

def validar_catalogo(dados):
    """Recebe dados Python já decodificados e verifica a estrutura.

    Levanta ValueError se:
    - dados não for uma lista
    - algum item não tiver id, nome e preco_centavos
    - preco_centavos não for inteiro positivo
    - houver ids repetidos
    Retorna a lista validada.
    """
    if not isinstance(dados, list):
        raise ValueError("Catálogo deve ser uma lista.")
    ids_vistos = set()
    for i, item in enumerate(dados):
        for campo in ("id", "nome", "preco_centavos"):
            if campo not in item:
                raise ValueError(f"Item {i} sem campo '{campo}'.")
        if not isinstance(item["preco_centavos"], int) or item["preco_centavos"] <= 0:
            raise ValueError(f"Item {i}: preco_centavos deve ser inteiro positivo.")
        if not str(item["nome"]).strip():
            raise ValueError(f"Item {i}: nome não pode ser vazio.")
        id_item = item["id"]
        if id_item in ids_vistos:
            raise ValueError(f"ID repetido: {id_item}.")
        ids_vistos.add(id_item)
    return dados


def ler_catalogo(caminho):
    """Lê e valida o catálogo em caminho.

    - Arquivo ausente: retorna None (situação esperada na primeira execução).
    - JSON inválido ou estrutura errada: levanta ValueError sem alterar o arquivo.
    Retorna a lista validada ou None.
    """
    caminho = Path(caminho)
    if not caminho.exists():
        return None
    texto = caminho.read_text(encoding="utf-8")
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON inválido em '{caminho}': {e}") from e
    return validar_catalogo(dados)


def salvar_catalogo(caminho, dados):
    """Valida dados e grava em caminho de forma segura.

    Escreve em arquivo temporário no mesmo diretório e só substitui
    o destino após a escrita completa. Uma interrupção não destrói
    o arquivo anterior.
    Levanta ValueError se dados forem inválidos.
    """
    caminho = Path(caminho)
    validar_catalogo(dados)
    texto = json.dumps(dados, ensure_ascii=False, indent=4)
    diretorio = caminho.parent
    fd, tmp = tempfile.mkstemp(dir=diretorio, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(texto)
        os.replace(tmp, caminho)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
