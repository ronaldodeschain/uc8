# A13: assinaturas de apoio; traga sua implementação anterior.
import csv
import os
import tempfile
from pathlib import Path
from datetime import datetime

def exportar_csv(caminho, comprovante):
    """TODO A13: implemente exportar_csv conforme o contrato e reutilize seu código anterior."""
    raise NotImplementedError('Implemente e teste esta operação.')

def registrar_venda_csv(comprovante,arquivo="vendas.csv"):
    caminho = Path(arquivo)

    existe = caminho.exists()

    with open(caminho,"a",newline="",encoding="utf-8") as arquivo_csv:
        writer = csv.writer(arquivo_csv,delimiter=";")

        if not existe:
            writer.writerow([
                "data_hora",
                "forma_pagamento",
                "total_centavos",
                "total_reais",
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            comprovante.forma,
            comprovante.total_centavos,
            f"{comprovante.total_centavos/100:.2f}",
        ])