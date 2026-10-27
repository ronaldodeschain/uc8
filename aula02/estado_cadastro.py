"""A02 — prática 1: campos em edição e registro confirmado."""

def registrar(campos, registro):
    campos["nome"] = campos["nome"].strip()
    if campos["nome"] == "":
        return "Nome não pode ser vazio."
    campos["sobrenome"] = campos["sobrenome"].strip()
    if campos["sobrenome"] == "":
        return "Sobrenome não pode ser vazio."
    try:
        campos["idade"] = int(campos["idade"])
        if campos["idade"] <= 0:
            return "idade deve ser maior que zero"
    except ValueError as e:
            return f"idade deve ser um número inteiro maior que zero: {e}"
    else:
        registro.add = campos
        return campos["nome"] + " " + campos["sobrenome"] + " de idade " + campos["idade"]


def exibir(registro):
    # TODO: tratar a ausência de registro e consultar o último válido.
    return registro


def limpar(campos):
    # TODO: esvaziar os três textos editáveis.
    # O registro confirmado é separado e não é recebido por esta função.
    pass


if __name__ == "__main__":
    campos = {"nome": "Lia", "sobrenome": "Costa", "idade": "-5"}
    registro = {}
    print(registrar(campos, registro))
    print(exibir(registro))
    limpar(campos)
    print("Campos após limpar:", campos)
    print(exibir(registro))
    # Acrescente os outros cenários da matriz, um de cada vez.
