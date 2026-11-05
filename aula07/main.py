"""A07 — interface da sorveteria; integra modelos.py sem duplicar regras."""
import tkinter as tk
from tkinter import ttk
from modelos import Produto, Pedido, formatar

# catalogo ficticio: preco em centavos
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
    janela.title("Sorveteria ficticia — A07")
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
    var_produto = tk.StringVar(value=nomes[0])
    combo = ttk.Combobox(grupo_cat, textvariable=var_produto, values=nomes, state="readonly")
    combo.grid(row=0, column=0, sticky="ew", padx=4, pady=4)
    combo.current(0)

    # --- grupo quantidade ---
    grupo_qtd = ttk.LabelFrame(base, text="Quantidade", padding=6)
    grupo_qtd.grid(row=1, column=0, sticky="ew", pady=4)
    grupo_qtd.columnconfigure(1, weight=1)

    ttk.Label(grupo_qtd, text="Qtd:").grid(row=0, column=0, padx=6, pady=4, sticky="w")
    entrada_qtd = ttk.Entry(grupo_qtd)
    entrada_qtd.grid(row=0, column=1, padx=6, pady=4, sticky="ew")

    # --- botao adicionar ---
    acoes = ttk.Frame(base)
    acoes.grid(row=2, column=0, sticky="ew", pady=4)
    acoes.columnconfigure(0, weight=1)

    def ao_adicionar():
        # ler selecao e quantidade; delegar ao modelo
        indice = combo.current()
        produto = CATALOGO[indice]
        texto_qtd = entrada_qtd.get()
        try:
            pedido.adicionar(produto, texto_qtd)
            aviso.configure(text=f"Adicionado: {produto.nome} x{texto_qtd}")
            atualizar_listagem(listbox, pedido)
            entrada_qtd.delete(0, tk.END)
        except ValueError as e:
            aviso.configure(text=f"Recusado: {e}")
        except RuntimeError as e:
            aviso.configure(text=f"Erro: {e}")
        entrada_qtd.focus_set()

    ttk.Button(acoes, text="Adicionar ao pedido", command=ao_adicionar).grid(
        row=0, column=0, pady=6)

    # --- listagem do pedido ---
    grupo_ped = ttk.LabelFrame(base, text="Pedido", padding=6)
    grupo_ped.grid(row=3, column=0, sticky="ew", pady=4)
    grupo_ped.columnconfigure(0, weight=1)

    listbox = tk.Listbox(grupo_ped, height=8)
    listbox.grid(row=0, column=0, sticky="ew", padx=4, pady=4)

    # --- aviso ---
    aviso = ttk.Label(base, text="Selecione um produto e informe a quantidade.",
                    wraplength=400)
    aviso.grid(row=4, column=0, pady=6, sticky="w")

    combo.focus_set()
    return janela


if __name__ == "__main__":
    criar_janela().mainloop()
