"""A08 — sorveteria com previa de pagamento; integra modelos.py e pagamentos.py."""
import tkinter as tk
from tkinter import ttk
from modelos import Produto, Pedido, formatar
from pagamentos import calcular_pagamento, preco_para_centavos, FATORES

CATALOGO = [
    Produto("F01", "Fruta",  150),
    Produto("L01", "Leite",  300),
    Produto("C01", "Creme",  250),
    Produto("S01", "Sorbet", 200),
]


def atualizar_listagem(listbox, pedido):
    listbox.delete(0, tk.END)
    for linha in pedido.linhas():
        listbox.insert(tk.END, linha)


def criar_janela():
    janela = tk.Tk()
    janela.title("Sorveteria ficticia — A08")
    janela.columnconfigure(0, weight=1)
    janela.rowconfigure(0, weight=1)

    base = ttk.Frame(janela, padding=12)
    base.grid(row=0, column=0, sticky="nsew")
    base.columnconfigure(0, weight=1)

    pedido = Pedido()

    # --- grupo catalogo ---
    grupo_cat = ttk.LabelFrame(base, text="Catalogo", padding=6)
    grupo_cat.grid(row=0, column=0, sticky="ew", pady=4)
    grupo_cat.columnconfigure(0, weight=1)

    nomes = [f"{p.codigo}  {p.nome}  {formatar(p.preco_centavos)}" for p in CATALOGO]
    combo_produto = ttk.Combobox(grupo_cat, values=nomes, state="readonly")
    combo_produto.grid(row=0, column=0, sticky="ew", padx=4, pady=4)
    combo_produto.current(0)

    # --- grupo quantidade ---
    grupo_qtd = ttk.LabelFrame(base, text="Quantidade", padding=6)
    grupo_qtd.grid(row=1, column=0, sticky="ew", pady=4)
    grupo_qtd.columnconfigure(1, weight=1)

    ttk.Label(grupo_qtd, text="Qtd:").grid(row=0, column=0, padx=6, pady=4, sticky="w")
    entrada_qtd = ttk.Entry(grupo_qtd)
    entrada_qtd.grid(row=0, column=1, padx=6, pady=4, sticky="ew")

    # --- botao adicionar ---
    acoes_pedido = ttk.Frame(base)
    acoes_pedido.grid(row=2, column=0, sticky="ew", pady=4)
    acoes_pedido.columnconfigure(0, weight=1)

    def ao_adicionar():
        # campo/selecao -> callback -> pedido.adicionar
        produto = CATALOGO[combo_produto.current()]
        try:
            pedido.adicionar(produto, entrada_qtd.get())
            aviso.configure(text=f"Adicionado: {produto.nome} x{entrada_qtd.get()}")
            atualizar_listagem(listbox, pedido)
            entrada_qtd.delete(0, tk.END)
        except (ValueError, RuntimeError) as e:
            aviso.configure(text=f"Recusado: {e}")
        entrada_qtd.focus_set()

    def ao_subtrair():
        # campo/selecao -> callback -> pedido.subtrair
        produto = CATALOGO[combo_produto.current()]
        try:
            pedido.subtrair(produto, entrada_qtd.get())
            aviso.configure(text=f"Subtraido: {produto.nome} x{entrada_qtd.get()}")
            atualizar_listagem(listbox, pedido)
            entrada_qtd.delete(0, tk.END)
        except (ValueError, RuntimeError) as e:
            aviso.configure(text=f"Recusado: {e}")
        entrada_qtd.focus_set()

    acoes_pedido.columnconfigure(1, weight=1)
    ttk.Button(acoes_pedido, text="Adicionar", command=ao_adicionar).grid(
        row=0, column=0, padx=4, pady=6)
    ttk.Button(acoes_pedido, text="Subtrair", command=ao_subtrair).grid(
        row=0, column=1, padx=4, pady=6)

    # --- listagem do pedido ---
    grupo_ped = ttk.LabelFrame(base, text="Pedido", padding=6)
    grupo_ped.grid(row=3, column=0, sticky="ew", pady=4)
    grupo_ped.columnconfigure(0, weight=1)

    listbox = tk.Listbox(grupo_ped, height=6)
    listbox.grid(row=0, column=0, sticky="ew", padx=4, pady=4)

    # --- grupo previa de pagamento ---
    grupo_pag = ttk.LabelFrame(base, text="Previa de pagamento", padding=6)
    grupo_pag.grid(row=4, column=0, sticky="ew", pady=4)
    grupo_pag.columnconfigure(1, weight=1)

    ttk.Label(grupo_pag, text="Forma:").grid(row=0, column=0, padx=6, pady=4, sticky="w")
    formas = list(FATORES.keys())
    combo_forma = ttk.Combobox(grupo_pag, values=formas, state="readonly")
    combo_forma.grid(row=0, column=1, padx=6, pady=4, sticky="ew")
    combo_forma.current(0)

    resultado_pag = ttk.Label(grupo_pag, text="", wraplength=380)
    resultado_pag.grid(row=1, column=0, columnspan=2, padx=6, pady=4, sticky="w")

    # --- botao calcular previa ---
    acoes_pag = ttk.Frame(base)
    acoes_pag.grid(row=5, column=0, sticky="ew", pady=4)
    acoes_pag.columnconfigure(0, weight=1)

    def ao_calcular_previa():
        # usa total atual do pedido; nao altera o pedido
        if not pedido.itens:
            aviso.configure(text="Pedido vazio. Adicione itens antes de calcular a previa.")
            return
        total_pedido = pedido.total_centavos()
        forma = combo_forma.get()
        from decimal import Decimal
        subtotal_texto = str(Decimal(total_pedido) / 100)
        try:
            total, desconto = calcular_pagamento(subtotal_texto, forma)
            resultado_pag.configure(
                text=f"{forma}: total {formatar(total)}  desconto {formatar(desconto)}"
            )
            aviso.configure(text="Previa calculada. Pedido nao foi alterado.")
        except ValueError as e:
            resultado_pag.configure(text="")
            aviso.configure(text=f"Recusado: {e}")

    ttk.Button(acoes_pag, text="Calcular previa", command=ao_calcular_previa).grid(
        row=0, column=0, pady=6)

    # --- aviso ---
    aviso = ttk.Label(base, text="Selecione um produto ou informe o subtotal.", wraplength=430)
    aviso.grid(row=6, column=0, pady=6, sticky="w")

    combo_produto.focus_set()
    return janela


if __name__ == "__main__":
    criar_janela().mainloop()
