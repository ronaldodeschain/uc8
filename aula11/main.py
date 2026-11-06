"""A11 — pizzaria com confirmacao em Toplevel, versao de previa e comprovante."""
import tkinter as tk
from tkinter import ttk
from decimal import Decimal
from modelos import Pizza, Bebida, Pedido, formatar, TAMANHOS
from pagamento import calcular_pagamento, FATORES

CATALOGO = [
    Pizza("PM1", "Mussarela",   "Media",  3500),
    Pizza("PG1", "Mussarela",   "Grande", 4500),
    Pizza("PM2", "Calabresa",   "Media",  3800),
    Pizza("PG2", "Calabresa",   "Grande", 4800),
    Pizza("PM3", "Frango",      "Media",  3600),
    Pizza("PG3", "Frango",      "Grande", 4600),
    Bebida("B01", "Suco",         600),
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


def abrir_previa(janela, pedido, forma, aviso, tree, lbl_total, combo_produto):
    """Abre Toplevel de confirmacao. Somente o botao Confirmar finaliza."""
    if not pedido.itens:
        aviso.configure(text="Pedido vazio. Adicione itens antes de confirmar.")
        return

    versao_previa = pedido.versao()

    subtotal_texto = str(Decimal(pedido.total_centavos()) / 100)
    try:
        total_pag, desconto = calcular_pagamento(subtotal_texto, forma)
    except ValueError as e:
        aviso.configure(text=f"Recusado: {e}")
        return

    top = tk.Toplevel(janela)
    top.title("Confirmar pedido")
    top.resizable(False, False)
    top.transient(janela)

    frame = ttk.Frame(top, padding=14)
    frame.grid(row=0, column=0, sticky="nsew")
    frame.columnconfigure(0, weight=1)

    ttk.Label(frame, text="Resumo do pedido", font=("", 10, "bold")).grid(
        row=0, column=0, columnspan=2, pady=(0, 6), sticky="w")

    for i, linha in enumerate(pedido.linhas()):
        ttk.Label(frame, text=linha, wraplength=340).grid(
            row=1 + i, column=0, columnspan=2, sticky="w")

    sep_row = 1 + len(pedido.linhas())
    ttk.Separator(frame, orient="horizontal").grid(
        row=sep_row, column=0, columnspan=2, sticky="ew", pady=6)

    ttk.Label(frame, text=f"Forma: {forma}").grid(
        row=sep_row + 1, column=0, columnspan=2, sticky="w")
    ttk.Label(frame, text=f"Total com desconto: {formatar(total_pag)}").grid(
        row=sep_row + 2, column=0, columnspan=2, sticky="w")
    ttk.Label(frame, text=f"Desconto: {formatar(desconto)}").grid(
        row=sep_row + 3, column=0, columnspan=2, sticky="w", pady=(0, 8))

    btn_row = sep_row + 4
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)

    def ao_confirmar():
        try:
            comprovante = pedido.finalizar(forma, versao_previa)
            top.destroy()
            mostrar_comprovante(janela, comprovante, aviso, tree, lbl_total,
                                combo_produto)
        except (ValueError, RuntimeError) as e:
            top.destroy()
            aviso.configure(text=f"Recusado: {e}")

    def ao_cancelar_previa():
        # X, Escape e Cancelar: apenas fecha, nao altera o pedido
        top.destroy()
        aviso.configure(text="Confirmacao cancelada. Pedido preservado.")

    btn_confirmar = ttk.Button(frame, text="Confirmar", command=ao_confirmar)
    btn_confirmar.grid(row=btn_row, column=0, padx=(0, 4), pady=6, sticky="ew")

    btn_cancelar = ttk.Button(frame, text="Cancelar", command=ao_cancelar_previa)
    btn_cancelar.grid(row=btn_row, column=1, padx=(4, 0), pady=6, sticky="ew")

    top.protocol("WM_DELETE_WINDOW", ao_cancelar_previa)
    top.bind("<Escape>", lambda _: ao_cancelar_previa())

    # foco inicial em Cancelar — evita confirmacao involuntaria pelo teclado
    btn_cancelar.focus_set()
    top.grab_set()


def mostrar_comprovante(janela, comprovante, aviso, tree, lbl_total, combo_produto):
    """Exibe comprovante em Toplevel apos confirmacao."""
    top = tk.Toplevel(janela)
    top.title("Comprovante")
    top.resizable(False, False)
    top.transient(janela)

    frame = ttk.Frame(top, padding=14)
    frame.grid(row=0, column=0, sticky="nsew")
    frame.columnconfigure(0, weight=1)

    ttk.Label(frame, text="Pedido confirmado", font=("", 10, "bold")).grid(
        row=0, column=0, pady=(0, 6), sticky="w")

    for i, linha in enumerate(comprovante.linhas):
        ttk.Label(frame, text=linha, wraplength=340).grid(
            row=1 + i, column=0, sticky="w")

    sep_row = 1 + len(comprovante.linhas)
    ttk.Separator(frame, orient="horizontal").grid(
        row=sep_row, column=0, sticky="ew", pady=6)
    ttk.Label(frame, text=f"Forma: {comprovante.forma}").grid(
        row=sep_row + 1, column=0, sticky="w")
    ttk.Label(frame, text=f"Total com desconto: {formatar(comprovante.total_centavos)}").grid(
        row=sep_row + 2, column=0, sticky="w", pady=(0, 8))

    aviso.configure(text="Pedido confirmado. Clique em Novo pedido para comecar.")

    def ao_fechar():
        top.destroy()
        combo_produto.focus_set()

    ttk.Button(frame, text="Fechar", command=ao_fechar).grid(
        row=sep_row + 3, column=0, pady=4)

    top.protocol("WM_DELETE_WINDOW", ao_fechar)
    top.bind("<Escape>", lambda _: ao_fechar())
    top.grab_set()


def criar_janela():
    janela = tk.Tk()
    janela.title("Pizzaria — A11")
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

    # --- botoes de montagem ---
    acoes = ttk.Frame(base)
    acoes.grid(row=2, column=0, sticky="ew", pady=4)
    for col in range(3):
        acoes.columnconfigure(col, weight=1)

    def ao_adicionar():
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

    # --- forma de pagamento + confirmar/novo ---
    grupo_pag = ttk.LabelFrame(base, text="Pagamento", padding=6)
    grupo_pag.grid(row=5, column=0, sticky="ew", pady=4)
    grupo_pag.columnconfigure(1, weight=1)

    ttk.Label(grupo_pag, text="Forma:").grid(row=0, column=0, padx=6, pady=4, sticky="w")
    combo_forma = ttk.Combobox(grupo_pag, values=list(FATORES.keys()), state="readonly")
    combo_forma.grid(row=0, column=1, padx=6, pady=4, sticky="ew")
    combo_forma.current(0)

    acoes_pag = ttk.Frame(grupo_pag)
    acoes_pag.grid(row=1, column=0, columnspan=2, sticky="ew", pady=4)
    acoes_pag.columnconfigure(0, weight=1)
    acoes_pag.columnconfigure(1, weight=1)

    def ao_confirmar_pedido():
        abrir_previa(janela, pedido, combo_forma.get(), aviso,
                     tree, lbl_total, combo_produto)

    def ao_novo_pedido():
        if pedido.itens:
            # guarda: pergunta antes de descartar montagem em andamento
            top = tk.Toplevel(janela)
            top.title("Descartar pedido?")
            top.resizable(False, False)
            top.transient(janela)

            frame = ttk.Frame(top, padding=14)
            frame.grid(row=0, column=0, sticky="nsew")
            frame.columnconfigure(0, weight=1)
            frame.columnconfigure(1, weight=1)

            ttk.Label(frame, text="Descartar a montagem atual e comecar um novo pedido?",
                      wraplength=300).grid(row=0, column=0, columnspan=2, pady=(0, 10))

            def ao_descartar():
                pedido.novo()
                redesenhar(tree, lbl_total, pedido)
                aviso.configure(text="Novo pedido iniciado.")
                top.destroy()
                combo_produto.focus_set()

            def ao_manter():
                # cancelar a pergunta preserva todos os itens
                top.destroy()
                aviso.configure(text="Descarte cancelado. Montagem preservada.")
                combo_produto.focus_set()

            ttk.Button(frame, text="Descartar", command=ao_descartar).grid(
                row=1, column=0, padx=(0, 4), sticky="ew")
            btn_manter = ttk.Button(frame, text="Manter", command=ao_manter)
            btn_manter.grid(row=1, column=1, padx=(4, 0), sticky="ew")

            top.protocol("WM_DELETE_WINDOW", ao_manter)
            top.bind("<Escape>", lambda _: ao_manter())
            btn_manter.focus_set()   # foco em Manter — evita descarte acidental
            top.grab_set()
        else:
            pedido.novo()
            redesenhar(tree, lbl_total, pedido)
            aviso.configure(text="Novo pedido iniciado.")
            combo_produto.focus_set()

    ttk.Button(acoes_pag, text="Confirmar pedido", command=ao_confirmar_pedido).grid(
        row=0, column=0, padx=(0, 4), sticky="ew")
    ttk.Button(acoes_pag, text="Novo pedido", command=ao_novo_pedido).grid(
        row=0, column=1, padx=(4, 0), sticky="ew")

    # --- aviso ---
    aviso = ttk.Label(base, text="Selecione um produto e informe a quantidade.",
                      wraplength=430)
    aviso.grid(row=6, column=0, pady=6, sticky="w")

    combo_produto.focus_set()
    return janela


if __name__ == "__main__":
    criar_janela().mainloop()
