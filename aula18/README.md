# Aula 18 — executar e testar

## Requisitos

- Windows com Python 3 instalado.
- Tkinter disponível na instalação do Python (é usado pela interface).
- Não é necessário instalar pacotes com `pip`.

## Abrir o aplicativo

Abra o PowerShell, entre nesta pasta e execute:

```powershell
Set-Location C:\Users\Pichau\Documents\senac\uc8\aula18
python .\main.py
```

O aplicativo abre a janela da sorveteria. Use a aba **Pedido** para montar
um pedido; as demais abas permitem consultar catálogo, produtos, clientes,
relatórios e vendas. Feche a janela para encerrar.

## Executar os testes

Na mesma pasta, execute:

```powershell
python .\verificar.py
```

Os testes são executados sem abrir a interface gráfica. A saída mostra os
grupos testados e termina com o total de verificações concluídas. Se houver
falha, o Python informa o teste e a linha que precisam ser investigados.

Os testes de banco e arquivos temporários usam uma pasta temporária; o banco
de teste não substitui `produtos.db`.
