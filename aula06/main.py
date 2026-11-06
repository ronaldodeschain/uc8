"""A06 — interface integrada ao modelo Aluno."""
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from aluno import Aluno


def inserir_marca(container, caminho=None):
    # TODO: procurar marca-a05.png ao lado do script com pathlib.
        caminho = caminho or Path(__file__).parent / "crab.png"
        # TODO: usar PhotoImage e conservar uma referência enquanto o rótulo existir.
        try:
            img = tk.PhotoImage(file=str(caminho))
            rotulo = ttk.Label(container, image=img)
            rotulo.image = img #type: ignore
            return rotulo
        # TODO: manter texto se o PNG não existir ou não puder ser lido.
        except Exception:
            return ttk.Label(container, text="Sistema escolar fictício — A06")


def abrir_consulta(principal, registro):
    if not registro:
        return None
    grupos = {}
    for aluno in registro:
        grupos.setdefault(aluno.turma, []).append(aluno)
    linhas = []
    for turma, alunos in sorted(grupos.items()):
        linhas.append(f"Turma: {turma}")
        for a in alunos:
            notas = " | ".join(str(n) for n in a.notas)
            linhas.append(f"  {a.nome}  Notas: {notas}  Média: {a.media:.1f}")
        media_turma = sum(a.media for a in alunos) / len(alunos)
        linhas.append(f"  Média da turma: {media_turma:.1f}")
    texto = "\n".join(linhas)
    consulta = tk.Toplevel(principal)
    consulta.title("Consulta — registros confirmados")
    consulta.resizable(False, False)
    ttk.Label(consulta, text=texto, wraplength=380, justify="left").pack(padx=20, pady=16)
    ttk.Button(consulta, text="Fechar", command=consulta.destroy).pack(pady=(0, 12))
    # botão, X e Escape fecham somente a consulta
    consulta.bind("<Escape>", lambda e: consulta.destroy())
    consulta.protocol("WM_DELETE_WINDOW", consulta.destroy)
    consulta.transient(principal)
    return consulta


def criar_janela():
    janela = tk.Tk()
    janela.title("Sistema escolar — A06")
    janela.columnconfigure(0, weight=1)
    janela.rowconfigure(0, weight=1)

    base = ttk.Frame(janela, padding=12)
    base.grid(row=0, column=0, sticky="nsew")
    base.columnconfigure(0, weight=1)
    base.columnconfigure(1, weight=1)

    registro = []

    inserir_marca(base).grid(row=0, column=0, columnspan=2, pady=6, sticky="w")

    # grupos reutilizados da A05
    identificacao = ttk.LabelFrame(base, text="Identificação", padding=6)
    identificacao.grid(row=1, column=0, columnspan=2, sticky="ew", pady=4)
    identificacao.columnconfigure(1, weight=1)

    grupo_notas = ttk.LabelFrame(base, text="Notas", padding=6)
    grupo_notas.grid(row=2, column=0, columnspan=2, sticky="ew", pady=4)
    grupo_notas.columnconfigure(1, weight=1)

    acoes = ttk.Frame(base)
    acoes.grid(row=3, column=0, columnspan=2, sticky="ew", pady=4)
    acoes.columnconfigure(0, weight=1)
    acoes.columnconfigure(1, weight=1)

    ttk.Label(identificacao, text="Nome fictício:").grid(row=0, column=0, padx=6, pady=4, sticky="w")
    entrada_nome = ttk.Entry(identificacao)
    entrada_nome.grid(row=0, column=1, padx=6, pady=4, sticky="ew")

    ttk.Label(identificacao, text="Turma fictícia:").grid(row=1, column=0, padx=6, pady=4, sticky="w")
    entrada_turma = ttk.Entry(identificacao)
    entrada_turma.grid(row=1, column=1, padx=6, pady=4, sticky="ew")

    entradas_notas = []
    for numero in range(1, 6):
        ttk.Label(grupo_notas, text=f"Nota {numero} (0 a 10):").grid(row=numero-1, column=0, padx=6, pady=4, sticky="w")
        entrada = ttk.Entry(grupo_notas)
        entrada.grid(row=numero-1, column=1, padx=6, pady=4, sticky="ew")
        entradas_notas.append(entrada)

    def ao_calcular():
        aluno = Aluno()
        mensagem = aluno.confirmar(
            entrada_nome.get(),
            entrada_turma.get(),
            [e.get() for e in entradas_notas],
        )
        if mensagem.startswith("Confirmado"):
            registro.append(aluno)
        aviso.configure(text=mensagem)

    def ao_consultar():
        if not registro:
            aviso.configure(text="Confirme um registro antes de consultar.")
            return
        abrir_consulta(janela, registro)

    def ao_limpar():
        # limpa somente os widgets; modelo preserva o último confirmado
        entrada_nome.delete(0, tk.END)
        entrada_turma.delete(0, tk.END)
        for e in entradas_notas:
            e.delete(0, tk.END)
        entrada_nome.focus_set()
        aviso.configure(text="Campos limpos. Registro anterior preservado.")

    ttk.Button(acoes, text="Calcular média", command=ao_calcular).grid(row=0, column=0, padx=4, pady=6)
    ttk.Button(acoes, text="Consultar", command=ao_consultar).grid(row=0, column=1, padx=4, pady=6)
    ttk.Button(acoes, text="Limpar campos", command=ao_limpar).grid(row=1, column=0, columnspan=2, padx=4, pady=6)

    aviso = ttk.Label(base, text="Use dados fictícios e confira as cinco notas.", wraplength=430)
    aviso.grid(row=4, column=0, columnspan=2, pady=6, sticky="w")

    entrada_nome.focus_set()
    return janela


if __name__ == "__main__":
    criar_janela().mainloop()
