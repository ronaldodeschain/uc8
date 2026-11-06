"""A10 — pizzaria com Pizza, Bebida, Treeview e previa de pagamento."""
import tkinter as tk
from tkinter import ttk
from decimal import Decimal
from modelos import Pizza, Bebida, Pedido, formatar, TAMANHOS
from pagamento import calcular_pagamento, FATORES

# cada combinacao sabor+tamanho tem codigo proprio
CATALOGO = [
    Pizza("PM1", "Mussarela",  "Media",  3500),
    Pizza("PG1", "Mussarela",  "Grande", 4500),
    Pizza("PM2", "Calabresa",  "Media",  3800),
    Pizza("PG2", "Calabresa",  "Grande", 4800),
    Pizza("PM3", "Frango",     "Media",  3600),
    Pizza("PG3", "Frango",     "Grande", 4600),
    Bebida("B01", "Suco",        600),
    Bebida("B02", "Refrigerante", 500),
    Bebida("B03", "Agua",         300),
]


def _label_catalogo(produto):
    tamanho = f" ({produto.tamanho})" if isinstance(produto, Pizza) else ""
    return f"{produto.codigo}  {produto.nome}{tamanho}  {formatar(produto.preco_centavos)}"


def redesenhar(tree, lbl_total, pedido):
    tree.delete(*tree.get_children())
    for item in pedido.itens:
        tamanho = item.produto.tamanho if isinstance(item.produto, Pizza) else "-"
        tree.insert(
            "", tk.END,
            iid=item.produto.codigo,
            values=(
                item.produto.codigo,
                item.produto.nome,
                tamanho,
                item.quantidade,
                formatar(item.subtotal()),
            ),
        )
    total = pedido.total_centavos()
    lbl_total.configure(text=f"Total: {formatar(total)}" if total else "Total: R$ 0,00")


def codigo_selecionado(tree):
    sel = tree.selection()
    return sel[0] if sel else None


def criar_janela():
    janela = tk.Tk()
    janela.title("Pizzaria — A10")
    janela.columnconfigure(0, weight=1)
    janela.rowconfigure(0, weight=1)

    base = ttk.Frame(janela, padding=12)
    base.grid(row=0, column=0, sticky="nsew")
    base.columnconfigure(0, weight=1)

    pedido = Pedido()

    # --- catalogo ---
    grupo_cat = ttk.LabelFrame(base, text="Catalogo", padding=6)
    grupo_cat.grid(row=0, column=0, sticky="ew", pady=4)
    grupo_cat.columnconfigure(0, weight=1)

    rotulos = [_label_catalogo(p) for p in CATALOGO]
    combo_produto = ttk.Combobox(grupo_cat, values=rotulos, state="readonly")
    combo_produto.grid(row=0, column=0, sticky="ew", padx=4, pady=4)
    combo_produto.current(0)

    # --- quantidade ---
    grupo_qtd = ttk.LabelFrame(base, text="Quantidade", padding=6)
    grupo_qtd.grid(row=1, column=0, sticky="ew", pady=4)
    grupo_qtd.columnconfigure(1, weight=1)

    ttk.Label(grupo_qtd, text="Qtd:").grid(row=0, column=0, padx=6, pady=4, sticky="w")
    entrada_qtd = ttk.Entry(grupo_qtd)
    entrada_qtd.grid(row=0, column=1, padx=6, pady=4, sticky="ew")

    # --- botoes ---
    acoes = ttk.Frame(base)
    acoes.grid(row=2, column=0, sticky="ew", pady=4)
    for col in range(3):
        acoes.columnconfigure(col, weight=1)

    def ao_adicionar():
        # campo/selecao -> callback -> pedido.adicionar
        produto = CATALOGO[combo_produto.current()]
        try:
            pedido.adicionar(produto, entrada_qtd.get())
            aviso.configure(text=f"Adicionado: {produto.nome} x{entrada_qtd.get()}")
            redesenhar(tree, lbl_total, pedido)
            entrada_qtd.delete(0, tk.END)
        except (ValueError, RuntimeError) as e:
            aviso.configure(text=f"Recusado: {e}")
        entrada_qtd.focus_set()

    def ao_atualizar():
        # selecao -> callback -> pedido.atualizar(codigo, qtd)
        codigo = codigo_selecionado(tree)
        if not codigo:
            aviso.configure(text="Selecione um item na tabela para atualizar.")
            return
        try:
            pedido.atualizar(codigo, entrada_qtd.get())
            aviso.configure(text=f"Atualizado: {codigo} -> x{entrada_qtd.get()}")
            redesenhar(tree, lbl_total, pedido)
            entrada_qtd.delete(0, tk.END)
        except (ValueError, RuntimeError) as e:
            aviso.configure(text=f"Recusado: {e}")
        entrada_qtd.focus_set()

    def ao_remover():
        # selecao -> callback -> pedido.remover(codigo)
        codigo = codigo_selecionado(tree)
        if not codigo:
            aviso.configure(text="Selecione um item na tabela para remover.")
            return
        try:
            pedido.remover(codigo)
            aviso.configure(text=f"Removido: {codigo}")
            redesenhar(tree, lbl_total, pedido)
        except (ValueError, RuntimeError) as e:
            aviso.configure(text=f"Recusado: {e}")

    ttk.Button(acoes, text="Adicionar", command=ao_adicionar).grid(
        row=0, column=0, padx=4, pady=6, sticky="ew")
    ttk.Button(acoes, text="Atualizar", command=ao_atualizar).grid(
        row=0, column=1, padx=4, pady=6, sticky="ew")
    ttk.Button(acoes, text="Remover",   command=ao_remover).grid(
        row=0, column=2, padx=4, pady=6, sticky="ew")

    entrada_qtd.bind("<Return>", lambda _: ao_adicionar())

    # --- treeview com scrollbar ---
    grupo_ped = ttk.LabelFrame(base, text="Pedido", padding=6)
    grupo_ped.grid(row=3, column=0, sticky="nsew", pady=4)
    grupo_ped.columnconfigure(0, weight=1)
    grupo_ped.rowconfigure(0, weight=1)
    base.rowconfigure(3, weight=1)

    colunas = ("codigo", "nome", "tamanho", "qtd", "subtotal")
    tree = ttk.Treeview(
        grupo_ped, columns=colunas, show="headings",
        height=6, selectmode="browse",
    )
    tree.heading("codigo",   text="Codigo")
    tree.heading("nome",     text="Nome")
    tree.heading("tamanho",  text="Tamanho")
    tree.heading("qtd",      text="Qtd")
    tree.heading("subtotal", text="Subtotal")
    tree.column("codigo",   width=55,  anchor="center")
    tree.column("nome",     width=110, anchor="w")
    tree.column("tamanho",  width=70,  anchor="center")
    tree.column("qtd",      width=45,  anchor="center")
    tree.column("subtotal", width=95,  anchor="e")
    tree.grid(row=0, column=0, sticky="nsew")

    scroll = ttk.Scrollbar(grupo_ped, orient="vertical", command=tree.yview)
    scroll.grid(row=0, column=1, sticky="ns")
    tree.configure(yscrollcommand=scroll.set)

    tree.bind("<Return>", lambda _: ao_atualizar())
    tree.bind("<Delete>", lambda _: ao_remover())

    # --- total ---
    lbl_total = ttk.Label(base, text="Total: R$ 0,00", font=("", 10, "bold"))
    lbl_total.grid(row=4, column=0, sticky="e", padx=4, pady=2)

    # --- previa de pagamento ---
    grupo_pag = ttk.LabelFrame(base, text="Previa de pagamento", padding=6)
    grupo_pag.grid(row=5, column=0, sticky="ew", pady=4)
    grupo_pag.columnconfigure(1, weight=1)

    ttk.Label(grupo_pag, text="Forma:").grid(row=0, column=0, padx=6, pady=4, sticky="w")
    combo_forma = ttk.Combobox(grupo_pag, values=list(FATORES.keys()), state="readonly")
    combo_forma.grid(row=0, column=1, padx=6, pady=4, sticky="ew")
    combo_forma.current(0)

    lbl_previa = ttk.Label(grupo_pag, text="", wraplength=380)
    lbl_previa.grid(row=1, column=0, columnspan=2, padx=6, pady=4, sticky="w")

    def ao_calcular_previa():
        if not pedido.itens:
            aviso.configure(text="Pedido vazio. Adicione itens antes de calcular.")
            return
        subtotal_texto = str(Decimal(pedido.total_centavos()) / 100)
        forma = combo_forma.get()
        try:
            total, desconto = calcular_pagamento(subtotal_texto, forma)
            lbl_previa.configure(
                text=f"{forma}: total {formatar(total)}  desconto {formatar(desconto)}"
            )
            aviso.configure(text="Previa calculada. Pedido nao foi alterado.")
        except ValueError as e:
            lbl_previa.configure(text="")
            aviso.configure(text=f"Recusado: {e}")

    ttk.Button(grupo_pag, text="Calcular previa", command=ao_calcular_previa).grid(
        row=2, column=0, columnspan=2, pady=6)

    # --- aviso ---
    aviso = ttk.Label(base, text="Selecione um produto e informe a quantidade.",
                      wraplength=430)
    aviso.grid(row=6, column=0, pady=6, sticky="w")

    combo_produto.focus_set()
    return janela


if __name__ == "__main__":
    criar_janela().mainloop()
