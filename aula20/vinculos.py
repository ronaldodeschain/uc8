# A20: assinaturas de apoio; traga sua implementação anterior.
clientes = {
    1: "João",
}

produtos = {
    "P1": "Pizza",
}

venda = {
    "cliente_id": 1,
}


def vinculo_valido(dados):
    return dados["cliente_id"] in clientes


def demonstrar():
    print(vinculo_valido(venda))

    clientes[1] = "João Silva"
    print(vinculo_valido(venda))

    venda["cliente_id"] = 99
    print(vinculo_valido(venda))


def _validar_id_vinculo(valor, entidade):
    if type(valor) is not int or valor <= 0:
        raise ValueError(f"ID de {entidade} deve ser um inteiro positivo.")
    return valor


def _validar_matriculas(matriculas):
    if not isinstance(matriculas, list):
        raise ValueError("Matrículas devem ser informadas em uma lista.")

    pares = []
    pares_vistos = set()
    for indice, matricula in enumerate(matriculas, start=1):
        if not isinstance(matricula, dict):
            raise ValueError(f"Matrícula {indice} deve ser um dicionário.")
        if "aluno_id" not in matricula or "plano_id" not in matricula:
            raise ValueError(
                f"Matrícula {indice} deve conter aluno_id e plano_id."
            )

        aluno_id = _validar_id_vinculo(matricula["aluno_id"], "aluno")
        plano_id = _validar_id_vinculo(matricula["plano_id"], "plano")
        par = (aluno_id, plano_id)
        if par in pares_vistos:
            raise ValueError(
                f"Matrícula duplicada para aluno {aluno_id} e plano {plano_id}."
            )
        pares_vistos.add(par)
        pares.append(par)

    return pares


def validar_vinculos(alunos, planos, matriculas):
    """Valida referências por ID e retorna True quando todos os vínculos existem."""
    if not isinstance(alunos, dict):
        raise ValueError("Alunos devem ser informados como dicionário ID→nome.")
    if not isinstance(planos, dict):
        raise ValueError("Planos devem ser informados como dicionário ID→nome.")

    for aluno_id in alunos:
        _validar_id_vinculo(aluno_id, "aluno")
    for plano_id in planos:
        _validar_id_vinculo(plano_id, "plano")

    for aluno_id, plano_id in _validar_matriculas(matriculas):
        if aluno_id not in alunos:
            raise ValueError(f"Aluno {aluno_id} não existe.")
        if plano_id not in planos:
            raise ValueError(f"Plano {plano_id} não existe.")

    return True


def pode_excluir_aluno(codigo, matriculas):
    """Retorna False se houver matrícula vinculada; valida IDs e duplicidades."""
    aluno_id = _validar_id_vinculo(codigo, "aluno")
    return not any(
        matricula_aluno_id == aluno_id
        for matricula_aluno_id, _ in _validar_matriculas(matriculas)
    )


if __name__ == "__main__":
    demonstrar()
