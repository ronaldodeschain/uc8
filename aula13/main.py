"""A13 — pizzaria com pedido, abas, catálogo JSON e Relatórios CSV."""
import os
import csv
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from decimal import Decimal
from pathlib import Path
from arquivos import ler_catalogo, salvar_catalogo, validar_catalogo
from modelos import Pedido, Produto, formatar
from relatorios import registrar_venda_csv
from pagamento import calcular_pagamento, FATORES
from perfis import SessaoDemo


CAMINHO_VENDAS = Path(__file__).resolve().parent.parent / "vendas.csv"


def _label_catalogo(produto):
    return f"{produto.codigo} {produto.nome}  {formatar(produto.preco_centavos)}"


def redesenhar(tree, lbl_total, pedido):
    tree.delete(*tree.get_children())
    for item in pedido.itens:
        tree.insert(
            "", tk.END,
            iid=item.produto.codigo,
            values=(
                item.produto.codigo,
                item.produto.nome,
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
        row=sep_row +4, column=0, columnspan=2, sticky="ew", pady=6)

    ttk.Label(frame,text="Registro CSV que será gerado: ",
              font=("",9,"bold")).grid(
        row=sep_row+5, column=0, columnspan=2, sticky="w")
    
    linha_csv = (
        f"11/11/2026;"
        f"{forma};"
        f"{pedido.total_centavos()/100:.2f};"
        f"{len(pedido.itens)}"
    )

    ttk.Label(frame,text=linha_csv,wraplength=340).grid(
        row=sep_row+6,column=0,columnspan=2,sticky="w")

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
            # grava a venda no csv
            registrar_venda_csv(comprovante, CAMINHO_VENDAS)

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
    janela.title("Pizzaria — A12")
    janela.geometry("680x720")
    janela.minsize(540, 580)
    janela.columnconfigure(0, weight=1)
    janela.rowconfigure(0, weight=1)

    notebook = ttk.Notebook(janela)
    notebook.grid(row=0, column=0, sticky="nsew")
    aba_pedido = ttk.Frame(notebook, padding=12)
    aba_catalogo = ttk.Frame(notebook, padding=12)
    aba_csv = ttk.Frame(notebook,padding=12)
    aba_perfis = ttk.Frame(notebook, padding=12)
    notebook.add(aba_pedido, text="Pedido")
    notebook.add(aba_catalogo, text="Catálogo JSON")
    notebook.add(aba_csv, text="Relatórios CSV")
    notebook.add(aba_perfis, text="Perfis")

    sessao = SessaoDemo()
    aba_perfis.columnconfigure(1, weight=1)
    ttk.Label(aba_perfis, text="Nome:").grid(
        row=0, column=0, sticky="w", padx=(0, 8), pady=4
    )
    entrada_nome_perfil = ttk.Entry(aba_perfis)
    entrada_nome_perfil.grid(row=0, column=1, sticky="ew", pady=4)

    ttk.Label(aba_perfis, text="Perfil:").grid(
        row=1, column=0, sticky="w", padx=(0, 8), pady=4
    )
    combo_perfil = ttk.Combobox(
        aba_perfis,
        values=("Caixa", "Administração"),
        state="readonly",
    )
    combo_perfil.grid(row=1, column=1, sticky="ew", pady=4)
    combo_perfil.current(0)

    lbl_sessao = ttk.Label(aba_perfis, text="Nenhuma sessão ativa.")
    lbl_sessao.grid(row=3, column=0, columnspan=2, sticky="w", pady=(12, 4))
    lbl_permissoes = ttk.Label(aba_perfis, text="Permissões: não verificadas.")
    lbl_permissoes.grid(row=4, column=0, columnspan=2, sticky="w", pady=4)

    lbl_usuario_atual = ttk.Label(aba_pedido, text="Nenhuma sessão ativa.")
    lbl_usuario_atual.grid(row=0, column=0, sticky="e", pady=(0, 8))

    def entrar_perfil():
        perfil = (
            "Administracao"
            if combo_perfil.get() == "Administração"
            else combo_perfil.get()
        )
        try:
            sessao.entrar(entrada_nome_perfil.get(), perfil)
        except ValueError as erro:
            messagebox.showerror("Dados inválidos", str(erro))
            return

        perfil_exibicao = (
            "Administração" if sessao.perfil == "Administracao" else sessao.perfil
        )
        lbl_sessao.configure(
            text=f"Logado: {sessao.nome} ({perfil_exibicao})"
        )
        lbl_usuario_atual.configure(
            text=f"{sessao.nome} ({perfil_exibicao})"
        )
        if sessao.pode_operar_vendas():
            permissoes = (
                "Pode operar vendas. Não pode acessar configurações."
            )
        else:
            permissoes = "Pode acessar configurações."
        lbl_permissoes.configure(text=f"Permissões: {permissoes}")

    def sair_perfil():
        sessao.sair()
        entrada_nome_perfil.delete(0, tk.END)
        combo_perfil.set("")
        lbl_sessao.configure(text="Nenhuma sessão ativa.")
        lbl_usuario_atual.configure(text="Nenhuma sessão ativa.")
        lbl_permissoes.configure(text="Permissões: não verificadas.")

    acoes_perfil = ttk.Frame(aba_perfis)
    acoes_perfil.grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))
    ttk.Button(acoes_perfil, text="Entrar", command=entrar_perfil).grid(
        row=0, column=0, padx=(0, 6)
    )
    ttk.Button(acoes_perfil, text="Sair", command=sair_perfil).grid(
        row=0, column=1
    )

    # --- aba relatórios csv ---
    aba_csv.columnconfigure(0,weight=1)
    aba_csv.rowconfigure(1, weight=1)

    colunas_csv=(
        "data_hora",
        "forma_pagamento",
        "total_centavos",
        "total_reais",
    )

    tree_csv = ttk.Treeview(
        aba_csv,
        columns=colunas_csv,
        show="headings"
    )

    tree_csv.heading("data_hora",text="Data e Hora")
    tree_csv.heading("forma_pagamento",text="Pagamento")
    tree_csv.heading("total_centavos",text="Centavos")
    tree_csv.heading("total_reais", text="Valor (R$)")

    tree_csv.column("data_hora",width=180,anchor="center")
    tree_csv.grid(row=1, column=0, sticky="nsew")

    menu = tk.Menu(janela)
    menu_navegacao = tk.Menu(menu, tearoff=False)
    menu_navegacao.add_command(
        label="Pedido\tCtrl+1",
        command=lambda: notebook.select(aba_pedido),
    )
    menu_navegacao.add_command(
        label="Catálogo JSON\tCtrl+2",
        command=lambda: notebook.select(aba_catalogo),
    )
    menu_navegacao.add_command(
        label="Abrir vendas.csv",
        command=lambda: notebook.select(aba_csv),
    )
    menu_navegacao.add_command(
        label="Perfis\tCtrl+4",
        command=lambda: notebook.select(aba_perfis),
    )
    menu.add_cascade(label="Navegar", menu=menu_navegacao)
    janela.configure(menu=menu)
    janela.bind_all(
        "<Control-Key-1>",
        lambda _: (notebook.select(aba_pedido), "break")[1],
    )
    janela.bind_all(
        "<Control-Key-2>",
        lambda _: (notebook.select(aba_catalogo), "break")[1],
    )
    janela.bind_all(
        "<Control-Key-3>",
        lambda _: (notebook.select(aba_csv), "break")[1],
    )
    janela.bind_all(
        "<Control-Key-4>",
        lambda _: (notebook.select(aba_perfis), "break")[1],
    )

    catalogo = []
    caminho_padrao = Path(__file__).with_name("catalogo.json")
    aviso_inicial = "Selecione um produto e informe a quantidade."
    dados_iniciais = None
    texto_inicial = None
    try:
        dados_iniciais = ler_catalogo(caminho_padrao)
        if dados_iniciais is None:
            aviso_inicial = "Catálogo ausente. Crie ou carregue um JSON na aba Catálogo."
        else:
            catalogo = [
                Produto(item["id"], item["nome"], item["preco_centavos"])
                for item in dados_iniciais
            ]
    except (ValueError, OSError) as erro:
        aviso_inicial = f"Catálogo inválido; corrija-o na aba Catálogo: {erro}"
        try:
            texto_inicial = caminho_padrao.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            pass

    base = ttk.Frame(aba_pedido)
    base.grid(row=1, column=0, sticky="nsew")
    base.columnconfigure(0, weight=1)
    aba_pedido.columnconfigure(0, weight=1)
    aba_pedido.rowconfigure(1, weight=1)

    pedido = Pedido()

    # --- catalogo ---
    grupo_cat = ttk.LabelFrame(base, text="Catalogo", padding=6)
    grupo_cat.grid(row=0, column=0, sticky="ew", pady=4)
    grupo_cat.columnconfigure(0, weight=1)

    rotulos = [_label_catalogo(p) for p in catalogo]
    combo_produto = ttk.Combobox(grupo_cat, values=rotulos, state="readonly")
    combo_produto.grid(row=0, column=0, sticky="ew", padx=4, pady=4)
    if rotulos:
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
        indice = combo_produto.current()
        if not 0 <= indice < len(catalogo):
            aviso.configure(text="Carregue ou cadastre produtos na aba Catálogo JSON.")
            notebook.select(aba_catalogo)
            catalogo_editor.focus_set()
            return
        produto = catalogo[indice]
        try:
            pedido.adicionar(produto, entrada_qtd.get())
            redesenhar(tree, lbl_total, pedido)
            aviso.config(text=f"Adicionado: {produto.nome} x{entrada_qtd.get()}")
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

    btn_adicionar = ttk.Button(acoes, text="Adicionar", command=ao_adicionar)
    btn_adicionar.grid(
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

    colunas = ("codigo", "nome", "qtd", "subtotal")
    tree = ttk.Treeview(
        grupo_ped, columns=colunas, show="headings",
        height=6, selectmode="browse",
    )
    tree.heading("codigo",   text="Codigo")
    tree.heading("nome",     text="Nome")
    tree.heading("qtd",      text="Qtd")
    tree.heading("subtotal", text="Subtotal")
    tree.column("codigo",   width=55,  anchor="center")
    tree.column("nome",     width=110, anchor="w")
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
    aviso = ttk.Label(base, text=aviso_inicial,
                      wraplength=430)
    aviso.grid(row=6, column=0, pady=6, sticky="w")

    aba_catalogo.columnconfigure(0, weight=1)
    aba_catalogo.rowconfigure(2, weight=1)
    ttk.Label(aba_catalogo, text="Arquivo do catálogo (JSON):").grid(
        row=0, column=0, sticky="w", pady=(0, 3))

    caminho_catalogo = tk.StringVar(value=str(caminho_padrao))
    linha_caminho = ttk.Frame(aba_catalogo)
    linha_caminho.grid(row=1, column=0, sticky="ew", pady=(0, 8))
    linha_caminho.columnconfigure(0, weight=1)
    entrada_caminho = ttk.Entry(linha_caminho, textvariable=caminho_catalogo)
    entrada_caminho.grid(row=0, column=0, sticky="ew", padx=(0, 6))

    acoes_catalogo = ttk.Frame(linha_caminho)
    acoes_catalogo.grid(row=0, column=1, sticky="e")
    btn_carregar = ttk.Button(acoes_catalogo, text="Carregar")
    btn_carregar.grid(row=0, column=0, padx=(0, 4))
    btn_salvar = ttk.Button(acoes_catalogo, text="Salvar")
    btn_salvar.grid(row=0, column=1)

    editor_frame = ttk.Frame(aba_catalogo)
    editor_frame.grid(row=2, column=0, sticky="nsew")
    editor_frame.columnconfigure(0, weight=1)
    editor_frame.rowconfigure(0, weight=1)
    catalogo_editor = ScrolledText(
        editor_frame,
        height=18,
        width=70,
        wrap="none",
        undo=True,
        takefocus=True,
    )
    catalogo_editor.grid(row=0, column=0, sticky="nsew")
    catalogo_aviso = ttk.Label(
        aba_catalogo,
        text=(
            aviso_inicial
            if "Catálogo" in aviso_inicial
            else "Edite uma lista JSON com id, nome e preco_centavos."
        ),
        wraplength=620,
    )
    catalogo_aviso.grid(row=3, column=0, sticky="w", pady=(8, 0))

    def definir_editor(dados):
        catalogo_editor.delete("1.0", tk.END)
        catalogo_editor.insert(
            "1.0",
            json.dumps(dados, ensure_ascii=False, indent=4),
        )
        catalogo_editor.edit_modified(False)

    def atualizar_catalogo(dados):
        nonlocal catalogo
        codigo_atual = (
            catalogo[combo_produto.current()].codigo
            if 0 <= combo_produto.current() < len(catalogo)
            else None
        )
        catalogo = [
            Produto(item["id"], item["nome"], item["preco_centavos"])
            for item in dados
        ]
        rotulos = [_label_catalogo(produto) for produto in catalogo]
        combo_produto.configure(values=rotulos)
        codigos = [produto.codigo for produto in catalogo]
        if codigo_atual in codigos:
            combo_produto.current(codigos.index(codigo_atual))
        elif catalogo:
            combo_produto.current(0)
        else:
            combo_produto.set("")

    def obter_caminho_catalogo():
        texto = caminho_catalogo.get().strip()
        if not texto:
            catalogo_aviso.configure(text="Informe o caminho do arquivo JSON.")
            entrada_caminho.focus_set()
            return None
        caminho = Path(texto)
        if not caminho.is_absolute():
            caminho = Path(__file__).parent / caminho
        return caminho

    def ao_carregar_catalogo():
        caminho = obter_caminho_catalogo()
        if caminho is None:
            return
        if catalogo_editor.edit_modified():
            pode_descartar = messagebox.askyesno(
                "Descartar edição?",
                "A edição JSON foi alterada. Descartar as alterações e carregar o arquivo?",
                parent=janela,
            )
            if not pode_descartar:
                catalogo_aviso.configure(
                    text="Carregamento cancelado. A edição atual foi preservada."
                )
                catalogo_editor.focus_set()
                return
        try:
            dados = ler_catalogo(caminho)
        except (OSError, ValueError) as erro:
            try:
                texto_original = caminho.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                texto_original = None
            if texto_original is not None:
                catalogo_editor.delete("1.0", tk.END)
                catalogo_editor.insert("1.0", texto_original)
                catalogo_editor.edit_modified(False)
            catalogo_aviso.configure(
                text=f"Catálogo inválido ou inacessível; arquivo preservado: {erro}"
            )
            catalogo_editor.focus_set()
            return

        if dados is None:
            dados = []
            mensagem = "Arquivo ausente. Catálogo vazio carregado; o pedido foi preservado."
        else:
            mensagem = f"Catálogo carregado: {len(dados)} produto(s). Pedido preservado."
        definir_editor(dados)
        atualizar_catalogo(dados)
        catalogo_aviso.configure(text=mensagem)
        combo_produto.focus_set()

    def ao_salvar_catalogo():
        caminho = obter_caminho_catalogo()
        if caminho is None:
            return
        try:
            dados = json.loads(catalogo_editor.get("1.0", "end-1c"))
            validar_catalogo(dados)
        except (json.JSONDecodeError, ValueError) as erro:
            catalogo_aviso.configure(
                text=f"JSON ou catálogo inválido; corrija a edição. Arquivo não alterado: {erro}"
            )
            catalogo_editor.focus_set()
            return

        acao = "Substituir" if caminho.exists() else "Criar"
        pode_salvar = messagebox.askyesno(
            "Confirmar salvamento",
            f"{acao} o catálogo neste caminho?\n{caminho}",
            parent=janela,
        )
        if not pode_salvar:
            catalogo_aviso.configure(
                text="Salvamento cancelado. Edição e arquivo foram preservados."
            )
            catalogo_editor.focus_set()
            return
        try:
            salvar_catalogo(caminho, dados)
        except (OSError, ValueError) as erro:
            catalogo_aviso.configure(
                text=f"Não foi possível salvar; edição e arquivo preservados: {erro}"
            )
            catalogo_editor.focus_set()
            return

        definir_editor(dados)
        atualizar_catalogo(dados)
        catalogo_aviso.configure(
            text=f"Catálogo salvo: {len(dados)} produto(s). Pedido preservado."
        )
        combo_produto.focus_set()

    def abrir_vendas():
        janela_vendas = tk.Toplevel(janela)
        janela_vendas.title("Vendas")

        colunas = ("data_hora","forma_pagamento","total_centavos","total_reais")
        tree = ttk.Treeview(janela_vendas, columns=colunas, show="headings")

        tree.heading("data_hora",text="Data e Hora")
        tree.heading("forma_pagamento", text="Forma de Pagamento")
        tree.heading("total_centavos", text="Total em Centavos")
        tree.heading("total_reais", text="Valor (R$)")

        tree.column("data_hora",width=180,anchor="center")
        tree.column("forma_pagamento", width=120, anchor="center")
        tree.column("total_centavos", width=100, anchor="center")
        tree.column("total_reais", width=100, anchor="center")

        try:
            with open("vendas.csv",newline="",encoding="utf-8") as arquivo_csv:
                leitor = csv.DictReader(arquivo_csv)
                for linha in leitor:
                    tree.insert("", tk.END,values=(
                        linha["data_hora"],
                        linha["forma_pagamento"],
                        linha["total_centavos"],
                        linha["total_reais"]
                    ))
        except FileNotFoundError:
            messagebox.showerror("Erro","Arquivo vendas.csv não encontrado.")
            return
        except KeyError:
            messagebox.showerror("Erro","Arquivo vendas.csv inválido.")
            return

        tree.pack(fill=tk.BOTH, expand=True)

    def abrir_csv():
        tree_csv.delete(*tree_csv.get_children())

        try:
            linhas = ler_linhas_csv()
        except FileNotFoundError:
            messagebox.showinfo(
                "Relatorios",
                "Nenhum arquivo vendas.csv foi gerado ainda"
            )
            return
        except (OSError, UnicodeError, csv.Error, ValueError) as erro:
            messagebox.showerror(
                "Erro ao carregar relatório",
                f"Não foi possível ler vendas.csv: {erro}",
            )
            return

        for linha in linhas:
            tree_csv.insert("", tk.END, values=linha)

    def ler_linhas_csv():
        with CAMINHO_VENDAS.open(newline="", encoding="utf-8") as arquivo:
            leitor = csv.reader(arquivo, delimiter=";")
            cabecalho = next(leitor, None)
            if cabecalho != list(colunas_csv):
                raise ValueError("Cabeçalho do arquivo vendas.csv inválido.")

            linhas = []
            for numero, linha in enumerate(leitor, start=2):
                if len(linha) != len(colunas_csv):
                    raise ValueError(
                        f"Quantidade de colunas inválida na linha {numero}."
                    )
                linhas.append(linha)
        return linhas

    def exportar_relatorio():
        try:
            linhas = ler_linhas_csv()
        except FileNotFoundError:
            messagebox.showinfo(
                "Relatorios",
                "Nenhum arquivo vendas.csv foi gerado ainda"
            )
            return
        except (OSError, UnicodeError, csv.Error, ValueError) as erro:
            messagebox.showerror(
                "Erro ao carregar relatório",
                f"Não foi possível ler vendas.csv: {erro}",
            )
            return

        destino = filedialog.asksaveasfilename(
            title="Exportar relatório",
            initialfile="relatorio_vendas.csv",
            filetypes=(("Arquivo CSV", "*.csv"), ("Arquivo de texto", "*.txt")),
            defaultextension=".csv",
        )
        if not destino:
            return

        caminho_destino = Path(destino)
        extensao = caminho_destino.suffix.lower()
        if extensao not in (".csv", ".txt"):
            messagebox.showerror(
                "Formato inválido",
                "Escolha um nome de arquivo com extensão .csv ou .txt.",
            )
            return

        delimitador = ";" if extensao == ".csv" else "\t"
        try:
            with caminho_destino.open("w", newline="", encoding="utf-8") as arquivo:
                escritor = csv.writer(arquivo, delimiter=delimitador)
                escritor.writerow(colunas_csv)
                escritor.writerows(linhas)
        except (OSError, csv.Error) as erro:
            messagebox.showerror(
                "Erro ao exportar relatório",
                f"Não foi possível salvar o relatório: {erro}",
            )
            return

        messagebox.showinfo(
            "Relatório exportado",
            f"Relatório salvo em:\n{caminho_destino}",
        )

    ttk.Button(
        aba_csv,
        text="Exportar relatório",
        command=exportar_relatorio,
    ).grid(row=0, column=0, sticky="e", pady=(0, 8))

    def ao_mudar_aba(event):
        if event.widget.select() == str(aba_csv):
            abrir_csv()

    notebook.bind("<<NotebookTabChanged>>", ao_mudar_aba)

    btn_carregar.configure(command=ao_carregar_catalogo)
    btn_salvar.configure(command=ao_salvar_catalogo)
    catalogo_editor.bind(
        "<Tab>",
        lambda evento: (evento.widget.tk_focusNext().focus_set(), "break")[1],
    )
    catalogo_editor.bind(
        "<Shift-Tab>",
        lambda evento: (evento.widget.tk_focusPrev().focus_set(), "break")[1],
    )
    if texto_inicial is not None:
        catalogo_editor.insert("1.0", texto_inicial)
        catalogo_editor.edit_modified(False)
    else:
        definir_editor(dados_iniciais if dados_iniciais is not None else [])

    if catalogo:
        combo_produto.focus_set()
    else:
        notebook.select(aba_catalogo)
        entrada_caminho.focus_set()
    return janela



if __name__ == "__main__":
    criar_janela().mainloop()
