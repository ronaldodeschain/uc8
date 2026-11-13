import csv
from pathlib import Path
from datetime import datetime
from typing import Union


COLUNAS_VENDAS = (
    "data_hora",
    "forma_pagamento",
    "total_centavos",
    "total_reais",
)


def _linha_venda(comprovante):
    return [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        comprovante.forma,
        comprovante.total_centavos,
        f"{comprovante.total_centavos / 100:.2f}",
    ]


def exportar_csv(caminho: Union[str, Path], comprovante):
    caminho = Path(caminho)
    with caminho.open("w", newline="", encoding="utf-8") as arquivo_csv:
        writer = csv.writer(arquivo_csv, delimiter=";")
        writer.writerow(COLUNAS_VENDAS)
        writer.writerow(_linha_venda(comprovante))


def registrar_venda_csv(
    comprovante,
    arquivo: Union[str, Path] = "vendas.csv",
):
    caminho = Path(arquivo)

    existe = caminho.exists()

    with caminho.open("a", newline="", encoding="utf-8") as arquivo_csv:
        writer = csv.writer(arquivo_csv, delimiter=";")

        if not existe:
            writer.writerow(COLUNAS_VENDAS)

        writer.writerow(_linha_venda(comprovante))