"""A03 — complete as funções antes de conectá-las à janela."""
def calcular(campos, registro):
    # TODO: ler reais e as duas cotações; aceitar vírgula ou ponto decimal.
    # TODO: tratar conversão inválida, reais negativos e cotações <= 0.
    # TODO: dividir reais por cada cotação.
    # TODO: confirmar entradas e os dois resultados somente após validar tudo.
    print(campos["reais"])
    print(campos["cotacao_dolar"])
    print(campos["cotacao_euro"])
    print("Print printoresco") 
    if float(campos["reais"].replace(',', '.')) or float(campos["cotacao_dolar"]) or (campos["cotacao_euro"]) <= 0:
        return "Valores inválidos. Use apenas números positivos e cotações maiores que zero."
    try:
        valor_real = float(campos["reais"].replace(',', '.'))
        valor_dolar = float(campos["cotacao_dolar"].replace(',', '.'))
        valor_euro = float(campos["cotacao_euro"].replace(',', '.'))
    except ValueError:
        return "Valores inválidos. Use apenas números."
    cotacao_real_dolar = valor_real / valor_dolar
    cotacao_real_euro = valor_real / valor_euro
    print(f"A cotação do real para o dolar é {cotacao_real_dolar:.2f}".replace('.', ','))
    print(f"A cotação do real para o euro é {cotacao_real_euro:.2f}".replace('.', ','))
    # formatted = f"{value:.2f}".replace('.', ',')
    #validação menor ou igual a zero
    
    return "Complete a função calcular."


def exibir(registro):
    # TODO: tratar ausência de conversão; consultar somente registro.
    # TODO: mostrar entradas usadas e resultados, estes com duas casas.
    return "Complete a função exibir."


def limpar(campos):
    # TODO: esvaziar os três campos; preservar registro e resultados.
    pass


if __name__ == "__main__":
    campos = {"reais": "100", "cotacao_dolar": "0", "cotacao_euro": "4"}
    registro = []
    print(exibir(registro))
    print(calcular(campos, registro))
    print(exibir(registro))
    # Acrescente as outras sequências da matriz, prevendo antes de executar.
