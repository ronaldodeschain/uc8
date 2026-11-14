# Roteiro de demonstração — A19

## Preparação

No PowerShell, executar o app a partir da pasta `aula19`:

```powershell
Set-Location \uc8\aula19
python .\main.py
```

Use dados fictícios. O perfil é uma simulação para a demonstração, não um
login com autenticação real.

## Fluxo completo

1. **Login demonstrativo** — abrir a aba **Perfis**, informar `Demo` como nome,
   escolher **Caixa** e clicar em **Entrar**. Conferir a mensagem de sessão.
2. **Produto válido** — abrir **Produtos SQLite** e adicionar `P99`, nome
   `Pizza teste`, preço `5000` centavos. Conferir a mensagem de sucesso e o
   produto na lista.
3. **Recusa** — tentar adicionar novamente o código `P99`. O app deve avisar
   que o código está duplicado; a lista não deve ganhar outro produto.
4. **Correção** — trocar o código para `P100` e salvar. Conferir que o novo
   produto aparece na lista e fica disponível para o pedido.
5. **Pedido** — abrir **Pedido**, escolher `P100`, informar quantidade `1` e
   clicar em **Adicionar**. Conferir o item e o total.
6. **Confirmação** — clicar em **Confirmar pedido**, conferir a prévia e
   clicar em **Confirmar**. A venda e o item são persistidos no SQLite antes
   do CSV; então o app mostra o comprovante.
7. **Resultado** — abrir **Vendas SQLite** e conferir a nova venda. Abrir
   **Relatórios CSV** para conferir o registro em `..\vendas.csv` (na pasta
   acima de `aula19`).

Se o código `P99` já existir antes da demonstração, use outro código livre
para o caso válido e tente cadastrá-lo novamente para demonstrar a recusa.

Se a confirmação for recusada por alteração no catálogo, o pedido permanece
montado. Confira o preço na aba **Produtos SQLite**, corrija os dados do
catálogo/pedido e tente confirmar novamente.

## Fazer backup do banco

Feche o aplicativo e, no PowerShell, ainda na pasta `aula19`, execute:

```powershell
python .\backup_sqlite.py
```

O comando cria `backup.db` ao lado de `produtos.db`. Não substitui um backup
existente; para guardar outra cópia, informe um novo nome:

```powershell
python .\backup_sqlite.py .\produtos.db .\backup-segunda-copia.db
```
