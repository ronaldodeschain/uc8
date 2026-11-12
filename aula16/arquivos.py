"""A12 — leitura e gravação segura do catálogo JSON."""
import json
import os
import tempfile
from pathlib import Path
from modelos import Produto


def carregar_catalogo(caminho):
    """Lê o catálogo em caminho.

    Retorna status, mensagem e produtos. Se o arquivo estiver ausente,
    retorna status falso; se estiver inválido, levanta ValueError.
    """
    dados = ler_catalogo(caminho)
    if dados is None:
        return False, "Arquivo não encontrado", []
    catalogo = [
        Produto(item["id"], item["nome"], item["preco_centavos"])
        for item in dados
    ]
    return True, "Catálogo carregado", catalogo


def validar_catalogo(dados):
    """Recebe dados Python já decodificados e verifica a estrutura.

    Levanta ValueError se:
    - dados não for uma lista
    - algum item não tiver id, nome e preco_centavos
    - id não for texto ou inteiro
    - preco_centavos não for inteiro positivo
    - houver ids repetidos
    Retorna a lista validada.
    """
    if not isinstance(dados, list):
        raise ValueError("Catálogo deve ser uma lista.")
    ids_vistos = set()
    for i, item in enumerate(dados):
        if not isinstance(item, dict):
            raise ValueError(f"Item {i} deve ser um objeto.")
        for campo in ("id", "nome", "preco_centavos"):
            if campo not in item:
                raise ValueError(f"Item {i} sem campo '{campo}'.")
        if type(item["id"]) not in (str, int):
            raise ValueError(f"Item {i}: id deve ser texto ou inteiro.")
        if type(item["preco_centavos"]) is not int or item["preco_centavos"] <= 0:
            raise ValueError(f"Item {i}: preco_centavos deve ser inteiro positivo.")
        if not isinstance(item["nome"], str) or not item["nome"].strip():
            raise ValueError(f"Item {i}: nome não pode ser vazio.")
        id_item = str(item["id"]).strip()
        if not id_item:
            raise ValueError(f"Item {i}: id não pode ser vazio.")
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
    try:
        texto = caminho.read_text(encoding="utf-8")
        dados = json.loads(texto)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
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
