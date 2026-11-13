"""A13 — pizzaria com pedido, abas, catálogo JSON e Relatórios CSV."""
import os
import csv
import json
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from decimal import Decimal
from datetime import datetime
from pathlib import Path
from arquivos import ler_catalogo, validar_catalogo
from modelos import Pedido, Produto, formatar
from relatorios import registrar_venda_csv
from pagamento import calcular_pagamento, FATORES
from perfis import SessaoDemo
from controller import ProdutoController
from repositorio import ProdutosSQLite
from banco import (
    CAMINHO_BANCO,
    atualizar_cliente,
    listar_clientes,
    listar_produtos as listar_produtos_banco,
    listar_vendas as listar_vendas_banco,
    registrar_pedido,
    remover_cliente,
    salvar_cliente,
    sincronizar_produtos,
)


CAMINHO_VENDAS = Path(__file__).resolve().parent.parent / "vendas.csv"


def _label_catalogo(produto):
    return f"{produto.codigo} {produto.nome}  {formatar(produto.preco_centavos)}"


def _preco_em_centavos(texto):
    try:
        preco_centavos = int(texto.strip())
    except ValueError as erro:
        raise ValueError("Informe o preço em centavos, por exemplo 4990.") from erro
    if preco_centavos <= 0:
        raise ValueError("O preço deve ser maior que zero centavos.")
    return preco_centavos


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

    nome_cliente = pedido.cliente[1] if pedido.cliente else "Não informado"
    ttk.Label(frame, text=f"Cliente: {nome_cliente}").grid(
        row=1, column=0, columnspan=2, sticky="w"
    )

    for i, linha in enumerate(pedido.linhas()):
        ttk.Label(frame, text=linha, wraplength=340).grid(
            row=2 + i, column=0, columnspan=2, sticky="w")

    sep_row = 2 + len(pedido.linhas())
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
            _registrar_pedido_no_banco(pedido, forma, versao_previa)
            comprovante = pedido.finalizar(forma, versao_previa)
        except (ValueError, RuntimeError) as e:
            top.destroy()
            aviso.configure(text=f"Recusado: {e}")
            return
        except sqlite3.Error as e:
            top.destroy()
            aviso.configure(text=f"Não foi possível registrar a venda no SQLite: {e}")
            return

        top.destroy()
        try:
            registrar_venda_csv(comprovante, CAMINHO_VENDAS)
        except (OSError, csv.Error) as e:
            messagebox.showwarning(
                "Venda registrada; CSV não atualizado",
                f"A venda foi gravada no SQLite, mas não foi possível atualizar o CSV:\n{e}",
                parent=janela,
            )
        mostrar_comprovante(
            janela, comprovante, aviso, tree, lbl_total, combo_produto
        )

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


def _registrar_pedido_no_banco(
    pedido,
    forma,
    versao_confirmada,
    caminho_banco=CAMINHO_BANCO,
):
    pedido.exigir_aberto()
    if versao_confirmada != pedido.versao():
        raise ValueError(
            "Pedido alterado desde a ultima previa. Solicite uma nova previa."
        )

    precos_atuais = {
        codigo: preco
        for codigo, _, preco in listar_produtos_banco(caminho_banco)
    }
    alteracoes = []
    for item in pedido.itens:
        preco_atual = precos_atuais.get(item.produto.codigo)
        if preco_atual != item.produto.preco_centavos:
            if preco_atual is None:
                situacao = "não está mais no catálogo"
            else:
                situacao = (
                    f"o preço mudou de {formatar(item.produto.preco_centavos)} "
                    f"para {formatar(preco_atual)}"
                )
            alteracoes.append(
                f"{item.produto.nome} ({item.produto.codigo}): {situacao}"
            )
    if alteracoes:
        detalhes = "; ".join(alteracoes)
        raise ValueError(
            "O catálogo foi alterado desde a montagem do pedido. "
            f"Revise os itens antes de confirmar: {detalhes}."
        )

    subtotal_texto = str(Decimal(pedido.total_centavos()) / 100)
    total_centavos, _ = calcular_pagamento(subtotal_texto, forma)
    cliente_id = pedido.cliente[0] if pedido.cliente else None
    itens = [
        (
            item.produto.codigo,
            item.quantidade,
            item.produto.preco_centavos,
        )
        for item in pedido.itens
    ]
    return registrar_pedido(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        forma,
        total_centavos,
        cliente_id,
        itens,
        caminho_banco,
        validar_catalogo=True,
    )


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

    ttk.Label(
        frame,
        text=f"Cliente: {comprovante.cliente[1] if comprovante.cliente else 'Não informado'}",
    ).grid(row=1, column=0, sticky="w")

    for i, linha in enumerate(comprovante.linhas):
        ttk.Label(frame, text=linha, wraplength=340).grid(
            row=2 + i, column=0, sticky="w")

    sep_row = 2 + len(comprovante.linhas)
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
    repositorio_produtos = ProdutosSQLite(CAMINHO_BANCO)
    controller_produtos = ProdutoController(repositorio_produtos)
    try:
        repositorio_produtos.iniciar()
    except sqlite3.Error as erro:
        messagebox.showerror(
            "Erro no banco SQLite",
            (
                f"Não foi possível abrir o banco de dados:\n{CAMINHO_BANCO}\n\n"
                f"{erro}\n\nVerifique se o arquivo está íntegro."
            ),
            parent=janela,
        )
        janela.destroy()
        return None

    janela.title("Mercado — A16")
    janela.geometry("680x720")
    janela.minsize(540, 580)
    janela.columnconfigure(0, weight=1)
    janela.rowconfigure(0, weight=1)

    notebook = ttk.Notebook(janela)
    notebook.grid(row=0, column=0, sticky="nsew")
    aba_pedido = ttk.Frame(notebook, padding=12)
    aba_catalogo = ttk.Frame(notebook, padding=12)
    aba_csv = ttk.Frame(notebook,padding=12)
    aba_historico = ttk.Frame(notebook, padding=12)
    aba_produtos = ttk.Frame(notebook, padding=12)
    aba_clientes = ttk.Frame(notebook, padding=12)
    aba_perfis = ttk.Frame(notebook, padding=12)
    notebook.add(aba_pedido, text="Pedido")
    notebook.add(aba_catalogo, text="Catálogo JSON")
    notebook.add(aba_csv, text="Relatórios CSV")
    notebook.add(aba_historico, text="Vendas SQLite")
    notebook.add(aba_produtos, text="Produtos SQLite")
    notebook.add(aba_clientes, text="Clientes")
    notebook.add(aba_perfis, text="Perfis")

    aba_produtos.columnconfigure(0, weight=1)
    aba_produtos.rowconfigure(2, weight=1)
    ttk.Label(
        aba_produtos,
        text=f"Produtos persistidos no banco: {CAMINHO_BANCO}",
        wraplength=620,
    ).grid(row=0, column=0, sticky="w", pady=(0, 8))

    formulario_produto = ttk.Frame(aba_produtos)
    formulario_produto.grid(row=1, column=0, sticky="ew", pady=(0, 8))
    for coluna in range(6):
        formulario_produto.columnconfigure(coluna, weight=1 if coluna % 2 else 0)

    ttk.Label(formulario_produto, text="Código:").grid(
        row=0, column=0, sticky="w", padx=(0, 5), pady=3
    )
    entrada_codigo_produto = ttk.Entry(formulario_produto)
    entrada_codigo_produto.grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=3)
    ttk.Label(formulario_produto, text="Nome:").grid(
        row=0, column=2, sticky="w", padx=(0, 5), pady=3
    )
    entrada_nome_produto = ttk.Entry(formulario_produto)
    entrada_nome_produto.grid(row=0, column=3, sticky="ew", padx=(0, 8), pady=3)
    ttk.Label(formulario_produto, text="Preço (centavos):").grid(
        row=0, column=4, sticky="w", padx=(0, 5), pady=3
    )
    entrada_preco_produto = ttk.Entry(formulario_produto, width=12)
    entrada_preco_produto.grid(row=0, column=5, sticky="ew", pady=3)

    acoes_produtos = ttk.Frame(aba_produtos)
    acoes_produtos.grid(row=3, column=0, sticky="ew", pady=(8, 0))
    btn_salvar_produto = ttk.Button(acoes_produtos, text="Adicionar")
    btn_salvar_produto.grid(row=0, column=0, padx=(0, 5))
    btn_atualizar_produto = ttk.Button(
        acoes_produtos, text="Salvar Alteração"
    )
    btn_atualizar_produto.grid(
        row=0, column=1, padx=5
    )
    btn_remover_produto = ttk.Button(
        acoes_produtos, text="Excluir"
    )
    btn_remover_produto.grid(
        row=0, column=2, padx=5
    )
    btn_recarregar_produtos = ttk.Button(
        acoes_produtos, text="Atualizar lista"
    )
    btn_recarregar_produtos.grid(
        row=0, column=3, padx=(5, 0)
    )

    colunas_produtos = ("codigo", "nome", "preco_centavos")
    tree_produtos = ttk.Treeview(
        aba_produtos,
        columns=colunas_produtos,
        show="headings",
        selectmode="browse",
    )
    tree_produtos.heading("codigo", text="COD")
    tree_produtos.heading("nome", text="NOME")
    tree_produtos.heading("preco_centavos", text="PREÇO")
    tree_produtos.column("codigo", width=90, anchor="center")
    tree_produtos.column("nome", width=300, anchor="w")
    tree_produtos.column("preco_centavos", width=120, anchor="e")
    tree_produtos.grid(row=2, column=0, sticky="nsew")
    lbl_aviso_produtos = ttk.Label(aba_produtos, text="")
    lbl_aviso_produtos.grid(row=4, column=0, sticky="w", pady=(8, 0))

    aba_clientes.columnconfigure(0, weight=1)
    aba_clientes.rowconfigure(2, weight=1)
    ttk.Label(
        aba_clientes,
        text=f"Clientes persistidos no banco: {CAMINHO_BANCO}",
        wraplength=620,
    ).grid(row=0, column=0, sticky="w", pady=(0, 8))

    formulario_cliente = ttk.Frame(aba_clientes)
    formulario_cliente.grid(row=1, column=0, sticky="ew", pady=(0, 8))
    formulario_cliente.columnconfigure(1, weight=1)
    formulario_cliente.columnconfigure(3, weight=1)
    ttk.Label(formulario_cliente, text="Nome:").grid(
        row=0, column=0, sticky="w", padx=(0, 5), pady=3
    )
    entrada_nome_cliente = ttk.Entry(formulario_cliente)
    entrada_nome_cliente.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=3)
    ttk.Label(formulario_cliente, text="Telefone:").grid(
        row=0, column=2, sticky="w", padx=(0, 5), pady=3
    )
    entrada_telefone_cliente = ttk.Entry(formulario_cliente)
    entrada_telefone_cliente.grid(row=0, column=3, sticky="ew", pady=3)

    acoes_clientes = ttk.Frame(aba_clientes)
    acoes_clientes.grid(row=3, column=0, sticky="ew", pady=(8, 0))
    btn_adicionar_cliente = ttk.Button(acoes_clientes, text="Adicionar")
    btn_adicionar_cliente.grid(row=0, column=0, padx=(0, 5))
    btn_editar_cliente = ttk.Button(acoes_clientes, text="Editar")
    btn_editar_cliente.grid(row=0, column=1, padx=5)
    btn_excluir_cliente = ttk.Button(acoes_clientes, text="Excluir")
    btn_excluir_cliente.grid(row=0, column=2, padx=5)
    btn_atualizar_clientes = ttk.Button(acoes_clientes, text="Atualizar lista")
    btn_atualizar_clientes.grid(row=0, column=3, padx=(5, 0))

    colunas_clientes = ("id", "nome", "telefone")
    tree_clientes = ttk.Treeview(
        aba_clientes,
        columns=colunas_clientes,
        show="headings",
        selectmode="browse",
    )
    tree_clientes.heading("id", text="ID")
    tree_clientes.heading("nome", text="Nome")
    tree_clientes.heading("telefone", text="Telefone")
    tree_clientes.column("id", width=70, anchor="center")
    tree_clientes.column("nome", width=280, anchor="w")
    tree_clientes.column("telefone", width=180, anchor="w")
    tree_clientes.grid(row=2, column=0, sticky="nsew")
    lbl_aviso_clientes = ttk.Label(aba_clientes, text="")
    lbl_aviso_clientes.grid(row=4, column=0, sticky="w", pady=(8, 0))

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

    aba_historico.columnconfigure(0, weight=1)
    aba_historico.rowconfigure(1, weight=1)
    ttk.Label(
        aba_historico,
        text=f"Vendas confirmadas no banco: {CAMINHO_BANCO}",
        wraplength=620,
    ).grid(row=0, column=0, sticky="w", pady=(0, 8))

    colunas_historico = (
        "id",
        "data_hora",
        "forma_pagamento",
        "total_centavos",
        "cliente_id",
    )
    tree_historico = ttk.Treeview(
        aba_historico,
        columns=colunas_historico,
        show="headings",
        selectmode="browse",
    )
    for coluna, titulo in (
        ("id", "Venda"),
        ("data_hora", "Data e hora"),
        ("forma_pagamento", "Pagamento"),
        ("total_centavos", "Total"),
        ("cliente_id", "Cliente ID"),
    ):
        tree_historico.heading(coluna, text=titulo)
    tree_historico.column("id", width=65, anchor="center")
    tree_historico.column("data_hora", width=155, anchor="center")
    tree_historico.column("forma_pagamento", width=120, anchor="center")
    tree_historico.column("total_centavos", width=110, anchor="e")
    tree_historico.column("cliente_id", width=85, anchor="center")
    tree_historico.grid(row=1, column=0, sticky="nsew")

    scroll_historico = ttk.Scrollbar(
        aba_historico, orient="vertical", command=tree_historico.yview
    )
    scroll_historico.grid(row=1, column=1, sticky="ns")
    tree_historico.configure(yscrollcommand=scroll_historico.set)
    lbl_aviso_historico = ttk.Label(aba_historico, text="")
    lbl_aviso_historico.grid(row=3, column=0, sticky="w", pady=(8, 0))

    def abrir_historico_sqlite():
        tree_historico.delete(*tree_historico.get_children())
        try:
            vendas = listar_vendas_banco(CAMINHO_BANCO)
        except (OSError, sqlite3.Error) as erro:
            lbl_aviso_historico.configure(
                text=f"Não foi possível carregar as vendas do SQLite: {erro}"
            )
            return

        for venda_id, data_hora, forma, total_centavos, cliente_id in vendas:
            tree_historico.insert(
                "",
                tk.END,
                values=(
                    venda_id,
                    data_hora,
                    forma,
                    formatar(total_centavos),
                    cliente_id if cliente_id is not None else "—",
                ),
            )
        lbl_aviso_historico.configure(
            text=f"{len(vendas)} venda(s) carregada(s) do SQLite."
        )

    ttk.Button(
        aba_historico,
        text="Atualizar histórico",
        command=abrir_historico_sqlite,
    ).grid(row=2, column=0, sticky="e", pady=(8, 0))

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
        label="Vendas SQLite",
        command=lambda: notebook.select(aba_historico),
    )
    menu_navegacao.add_command(
        label="Produtos SQLite\tCtrl+5",
        command=lambda: notebook.select(aba_produtos),
    )
    menu_navegacao.add_command(
        label="Clientes\tCtrl+6",
        command=lambda: notebook.select(aba_clientes),
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
    janela.bind_all(
        "<Control-Key-5>",
        lambda _: (notebook.select(aba_produtos), "break")[1],
    )
    janela.bind_all(
        "<Control-Key-6>",
        lambda _: (notebook.select(aba_clientes), "break")[1],
    )

    catalogo = []
    clientes = []
    caminho_padrao = Path(__file__).with_name("catalogo.json")
    aviso_inicial = "Selecione um produto e informe a quantidade."
    dados_iniciais = None
    try:
        produtos_banco = controller_produtos.listar_produtos()
        clientes = listar_clientes()
        dados_iniciais = [
            {
                "id": codigo,
                "nome": nome,
                "preco_centavos": preco_centavos,
            }
            for codigo, nome, preco_centavos in produtos_banco
        ]
        catalogo = [
            Produto(item["id"], item["nome"], item["preco_centavos"])
            for item in dados_iniciais
        ]
    except (OSError, sqlite3.Error, ValueError) as erro:
        aviso_inicial = f"Não foi possível carregar produtos do banco SQLite: {erro}"

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
    grupo_cat.columnconfigure(1, weight=1)

    ttk.Label(grupo_cat, text="Cliente:").grid(
        row=0, column=0, sticky="w", padx=4, pady=4
    )
    combo_cliente = ttk.Combobox(grupo_cat, state="readonly")
    combo_cliente.grid(row=0, column=1, sticky="ew", padx=4, pady=4)

    rotulos = [_label_catalogo(p) for p in catalogo]
    combo_produto = ttk.Combobox(grupo_cat, values=rotulos, state="readonly")
    combo_produto.grid(
        row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=4
    )
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
                pedido.definir_cliente(
                    clientes_por_opcao.get(combo_cliente.get())
                )
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
            pedido.definir_cliente(
                clientes_por_opcao.get(combo_cliente.get())
            )
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
    ttk.Label(
        aba_catalogo,
        text="Catálogo JSON para importação; alterações serão salvas no SQLite:",
    ).grid(
        row=0, column=0, sticky="w", pady=(0, 3))

    caminho_catalogo = tk.StringVar(value=str(caminho_padrao))
    linha_caminho = ttk.Frame(aba_catalogo)
    linha_caminho.grid(row=1, column=0, sticky="ew", pady=(0, 8))
    linha_caminho.columnconfigure(0, weight=1)
    entrada_caminho = ttk.Entry(linha_caminho, textvariable=caminho_catalogo)
    entrada_caminho.grid(row=0, column=0, sticky="ew", padx=(0, 6))

    acoes_catalogo = ttk.Frame(linha_caminho)
    acoes_catalogo.grid(row=0, column=1, sticky="e")
    btn_carregar = ttk.Button(acoes_catalogo, text="Carregar JSON")
    btn_carregar.grid(row=0, column=0, padx=(0, 4))
    btn_salvar = ttk.Button(acoes_catalogo, text="Salvar no SQLite")
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

    def recarregar_produtos_sqlite():
        try:
            produtos_banco = controller_produtos.listar_produtos()
        except (OSError, sqlite3.Error) as erro:
            lbl_aviso_produtos.configure(
                text=f"Não foi possível carregar produtos do SQLite: {erro}"
            )
            return False

        dados_banco = [
            {
                "id": codigo,
                "nome": nome,
                "preco_centavos": preco_centavos,
            }
            for codigo, nome, preco_centavos in produtos_banco
        ]
        atualizar_catalogo(dados_banco)
        tree_produtos.delete(*tree_produtos.get_children())
        for codigo, nome, preco_centavos in produtos_banco:
            tree_produtos.insert(
                "",
                tk.END,
                iid=codigo,
                values=(codigo, nome, formatar(preco_centavos)),
            )
        return True

    clientes_por_opcao = {}

    def recarregar_clientes_sqlite(selecionar_id=None):
        nonlocal clientes
        try:
            clientes = listar_clientes()
        except (OSError, sqlite3.Error) as erro:
            lbl_aviso_clientes.configure(
                text=f"Não foi possível carregar clientes do SQLite: {erro}"
            )
            return False

        cliente_atual_id = (
            pedido.cliente[0]
            if pedido.cliente is not None
            else None
        )
        if selecionar_id is not None:
            cliente_atual_id = selecionar_id

        clientes_por_opcao.clear()
        opcoes = []
        for cliente in clientes:
            cliente_id, nome = cliente[:2]
            opcao = f"{cliente_id} - {nome}"
            opcoes.append(opcao)
            clientes_por_opcao[opcao] = cliente

        combo_cliente.configure(values=opcoes)
        opcao_atual = next(
            (
                opcao
                for opcao, cliente in clientes_por_opcao.items()
                if cliente[0] == cliente_atual_id
            ),
            None,
        )
        if opcao_atual is None:
            combo_cliente.set("Selecionar cliente")
            cliente_selecionado = None
        else:
            combo_cliente.set(opcao_atual)
            cliente_selecionado = clientes_por_opcao[opcao_atual]

        if pedido.aberto:
            pedido.definir_cliente(cliente_selecionado)

        tree_clientes.delete(*tree_clientes.get_children())
        for cliente_id, nome, telefone in clientes:
            tree_clientes.insert(
                "",
                tk.END,
                iid=str(cliente_id),
                values=(cliente_id, nome, telefone or ""),
            )
        return True

    def ao_selecionar_cliente(event=None):
        if not pedido.aberto:
            cliente_atual = pedido.cliente
            opcao_atual = next(
                (
                    opcao
                    for opcao, cliente in clientes_por_opcao.items()
                    if cliente == cliente_atual
                ),
                "Selecionar cliente",
            )
            combo_cliente.set(opcao_atual)
            messagebox.showinfo(
                "Pedido finalizado",
                "Inicie um novo pedido antes de trocar o cliente.",
                parent=janela,
            )
            return
        pedido.definir_cliente(clientes_por_opcao.get(combo_cliente.get()))

    def ao_selecionar_cliente_na_lista(event=None):
        selecionados = tree_clientes.selection()
        if not selecionados:
            return
        valores = tree_clientes.item(selecionados[0], "values")
        entrada_nome_cliente.delete(0, tk.END)
        entrada_nome_cliente.insert(0, valores[1])
        entrada_telefone_cliente.delete(0, tk.END)
        entrada_telefone_cliente.insert(0, valores[2])

    def ao_adicionar_cliente():
        nome = entrada_nome_cliente.get().strip()
        telefone = entrada_telefone_cliente.get().strip() or None
        if not nome:
            messagebox.showerror(
                "Dados inválidos", "Informe o nome do cliente.", parent=janela
            )
            return
        try:
            cliente_id = salvar_cliente(nome, telefone)
        except (ValueError, sqlite3.Error, OSError) as erro:
            messagebox.showerror(
                "Não foi possível adicionar cliente", str(erro), parent=janela
            )
            return

        entrada_nome_cliente.delete(0, tk.END)
        entrada_telefone_cliente.delete(0, tk.END)
        if recarregar_clientes_sqlite(selecionar_id=cliente_id):
            lbl_aviso_clientes.configure(
                text=f"Cliente {nome} adicionado ao SQLite."
            )

    def ao_editar_cliente():
        selecionados = tree_clientes.selection()
        if not selecionados:
            messagebox.showinfo(
                "Selecione um cliente",
                "Selecione um cliente na lista para editar.",
                parent=janela,
            )
            return
        cliente_id = int(selecionados[0])
        nome = entrada_nome_cliente.get().strip()
        telefone = entrada_telefone_cliente.get().strip() or None
        if not nome:
            messagebox.showerror(
                "Dados inválidos", "Informe o nome do cliente.", parent=janela
            )
            return
        try:
            if not atualizar_cliente(cliente_id, nome, telefone):
                raise ValueError("O cliente não existe mais no banco SQLite.")
        except (ValueError, sqlite3.Error, OSError) as erro:
            messagebox.showerror(
                "Não foi possível editar cliente", str(erro), parent=janela
            )
            return

        if recarregar_clientes_sqlite(selecionar_id=cliente_id):
            lbl_aviso_clientes.configure(
                text=f"Cliente {nome} atualizado no SQLite."
            )

    def ao_excluir_cliente():
        selecionados = tree_clientes.selection()
        if not selecionados:
            messagebox.showinfo(
                "Selecione um cliente",
                "Selecione um cliente na lista para excluir.",
                parent=janela,
            )
            return
        cliente_id = int(selecionados[0])
        nome = tree_clientes.item(selecionados[0], "values")[1]
        if not messagebox.askyesno(
            "Confirmar exclusão",
            f"Excluir o cliente {nome} permanentemente?",
            parent=janela,
        ):
            return
        try:
            if not remover_cliente(cliente_id):
                raise ValueError("O cliente não existe mais no banco SQLite.")
        except (ValueError, sqlite3.Error, OSError) as erro:
            messagebox.showerror(
                "Não foi possível excluir cliente", str(erro), parent=janela
            )
            return

        entrada_nome_cliente.delete(0, tk.END)
        entrada_telefone_cliente.delete(0, tk.END)
        if recarregar_clientes_sqlite():
            lbl_aviso_clientes.configure(
                text=f"Cliente {nome} excluído do SQLite."
            )

    def ao_selecionar_produto(event=None):
        selecionados = tree_produtos.selection()
        if not selecionados:
            return
        codigo = selecionados[0]
        valores = tree_produtos.item(codigo, "values")
        entrada_codigo_produto.delete(0, tk.END)
        entrada_codigo_produto.insert(0, valores[0])
        entrada_nome_produto.delete(0, tk.END)
        entrada_nome_produto.insert(0, valores[1])
        entrada_preco_produto.delete(0, tk.END)
        produto = next(item for item in catalogo if item.codigo == codigo)
        entrada_preco_produto.insert(
            0, str(produto.preco_centavos)
        )

    def limpar_formulario_produto():
        entrada_codigo_produto.delete(0, tk.END)
        entrada_nome_produto.delete(0, tk.END)
        entrada_preco_produto.delete(0, tk.END)

    def obter_dados_formulario_produto():
        codigo = entrada_codigo_produto.get().strip()
        nome = entrada_nome_produto.get().strip()
        if not codigo:
            raise ValueError("Informe o código do produto.")
        if not nome:
            raise ValueError("Informe o nome do produto.")
        preco_centavos = _preco_em_centavos(entrada_preco_produto.get())
        return codigo, nome, preco_centavos

    def ao_salvar_produto():
        try:
            codigo, nome, preco_centavos = obter_dados_formulario_produto()
            controller_produtos.salvar_produto(codigo, nome, preco_centavos)
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Código duplicado",
                "Já existe um produto cadastrado com esse código.",
                parent=janela,
            )
            return
        except (ValueError, sqlite3.Error, OSError) as erro:
            messagebox.showerror("Não foi possível salvar produto", str(erro), parent=janela)
            return

        limpar_formulario_produto()
        if recarregar_produtos_sqlite():
            lbl_aviso_produtos.configure(
                text=f"Produto {codigo} salvo no SQLite."
            )

    def ao_atualizar_produto():
        selecionados = tree_produtos.selection()
        if not selecionados:
            messagebox.showinfo(
                "Selecione um produto",
                "Selecione um produto na lista para atualizar.",
                parent=janela,
            )
            return
        codigo_selecionado = selecionados[0]
        try:
            codigo, nome, preco_centavos = obter_dados_formulario_produto()
            if codigo != codigo_selecionado:
                raise ValueError("O código não pode ser alterado.")
            if not controller_produtos.atualizar_produto(
                codigo, nome, preco_centavos
            ):
                raise ValueError("O produto não existe mais no banco SQLite.")
        except (ValueError, sqlite3.Error, OSError) as erro:
            messagebox.showerror(
                "Não foi possível atualizar produto", str(erro), parent=janela
            )
            return

        if recarregar_produtos_sqlite():
            lbl_aviso_produtos.configure(
                text=f"Produto {codigo_selecionado} atualizado no SQLite."
            )

    def ao_remover_produto():
        selecionados = tree_produtos.selection()
        if not selecionados:
            messagebox.showinfo(
                "Selecione um produto",
                "Selecione um produto na lista para remover.",
                parent=janela,
            )
            return
        codigo = selecionados[0]
        if not messagebox.askyesno(
            "Confirmar remoção",
            f"Remover o produto {codigo} permanentemente do SQLite?",
            parent=janela,
        ):
            return
        try:
            if not controller_produtos.remover_produto(codigo):
                raise ValueError("O produto não existe mais no banco SQLite.")
        except (ValueError, sqlite3.Error, OSError) as erro:
            messagebox.showerror(
                "Não foi possível remover produto", str(erro), parent=janela
            )
            return

        limpar_formulario_produto()
        if recarregar_produtos_sqlite():
            lbl_aviso_produtos.configure(
                text=f"Produto {codigo} removido do SQLite."
            )

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
        try:
            dados = json.loads(catalogo_editor.get("1.0", "end-1c"))
            validar_catalogo(dados)
        except (json.JSONDecodeError, ValueError) as erro:
            catalogo_aviso.configure(
                text=f"JSON ou catálogo inválido; corrija a edição. Arquivo não alterado: {erro}"
            )
            catalogo_editor.focus_set()
            return

        try:
            produtos_atuais = {
                codigo: (nome, preco)
                for codigo, nome, preco in controller_produtos.listar_produtos()
            }
        except (OSError, sqlite3.Error) as erro:
            catalogo_aviso.configure(
                text=f"Não foi possível ler o banco SQLite; edição preservada: {erro}"
            )
            catalogo_editor.focus_set()
            return

        produtos_desejados = {
            str(item["id"]).strip(): (item["nome"].strip(), item["preco_centavos"])
            for item in dados
        }
        inseridos = len(produtos_desejados.keys() - produtos_atuais.keys())
        removidos = len(produtos_atuais.keys() - produtos_desejados.keys())
        atualizados = sum(
            1
            for codigo in produtos_desejados.keys() & produtos_atuais.keys()
            if produtos_desejados[codigo] != produtos_atuais[codigo]
        )
        pode_salvar = messagebox.askyesno(
            "Confirmar gravação no SQLite",
            (
                f"Gravar alterações em:\n{CAMINHO_BANCO}\n\n"
                f"Novos: {inseridos}\n"
                f"Atualizados: {atualizados}\n"
                f"Removidos: {removidos}"
            ),
            parent=janela,
        )
        if not pode_salvar:
            catalogo_aviso.configure(
                text="Salvamento cancelado. Edição e banco foram preservados."
            )
            catalogo_editor.focus_set()
            return
        try:
            resultado = sincronizar_produtos(dados)
        except (OSError, sqlite3.Error, ValueError) as erro:
            catalogo_aviso.configure(
                text=f"Não foi possível salvar; edição preservada e banco inalterado: {erro}"
            )
            catalogo_editor.focus_set()
            return

        definir_editor(dados)
        atualizar_catalogo(dados)
        catalogo_aviso.configure(
            text=(
                f"SQLite atualizado: {resultado['inseridos']} novo(s), "
                f"{resultado['atualizados']} atualizado(s), "
                f"{resultado['removidos']} removido(s). Pedido preservado."
            )
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
        elif event.widget.select() == str(aba_historico):
            abrir_historico_sqlite()

    notebook.bind("<<NotebookTabChanged>>", ao_mudar_aba)

    btn_carregar.configure(command=ao_carregar_catalogo)
    btn_salvar.configure(command=ao_salvar_catalogo)
    btn_salvar_produto.configure(command=ao_salvar_produto)
    btn_atualizar_produto.configure(command=ao_atualizar_produto)
    btn_remover_produto.configure(command=ao_remover_produto)
    btn_recarregar_produtos.configure(command=recarregar_produtos_sqlite)
    tree_produtos.bind("<<TreeviewSelect>>", ao_selecionar_produto)
    recarregar_produtos_sqlite()
    btn_adicionar_cliente.configure(command=ao_adicionar_cliente)
    btn_editar_cliente.configure(command=ao_editar_cliente)
    btn_excluir_cliente.configure(command=ao_excluir_cliente)
    btn_atualizar_clientes.configure(command=recarregar_clientes_sqlite)
    tree_clientes.bind("<<TreeviewSelect>>", ao_selecionar_cliente_na_lista)
    combo_cliente.bind("<<ComboboxSelected>>", ao_selecionar_cliente)
    recarregar_clientes_sqlite()
    catalogo_editor.bind(
        "<Tab>",
        lambda evento: (evento.widget.tk_focusNext().focus_set(), "break")[1],
    )
    catalogo_editor.bind(
        "<Shift-Tab>",
        lambda evento: (evento.widget.tk_focusPrev().focus_set(), "break")[1],
    )
    definir_editor(dados_iniciais if dados_iniciais is not None else [])

    if catalogo:
        combo_produto.focus_set()
    else:
        notebook.select(aba_catalogo)
        entrada_caminho.focus_set()
    return janela



if __name__ == "__main__":
    janela = criar_janela()
    if janela is not None:
        janela.mainloop()
