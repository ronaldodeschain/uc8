# Pizzaria/Mercado - Sistema de Pedidos

Aplicação desktop desenvolvida em Python com Tkinter para montagem e
confirmação de pedidos, gerenciamento de produtos e clientes e persistência
dos dados em SQLite. O projeto também permite importar e editar um catálogo
em JSON e exportar vendas em CSV.

Versão final entregue na pasta `aula20`.

## 1. Nome do Projeto

**Pizzaria/Mercado - Sistema de Pedidos**

Sistema desktop desenvolvido em Python com Tkinter para gerenciamento de
produtos, clientes, pedidos, vendas e persistência em SQLite.

## 2. Funcionalidades

- Cadastro, edição, listagem e exclusão de produtos.
- Cadastro, edição, listagem e exclusão de clientes.
- Montagem de pedidos com seleção de cliente e produto.
- Inclusão, alteração e remoção de itens do pedido.
- Cálculo de quantidade, subtotal e total em centavos.
- Cálculo de desconto por forma de pagamento.
- Prévia e confirmação explícita antes da gravação.
- Persistência de vendas e itens no SQLite.
- Importação e sincronização de catálogo em JSON.
- Exportação e leitura de vendas em CSV.
- Perfis demonstrativos de Caixa e Administração.
- Backup de banco SQLite.
- Validação de vínculos por ID.
- Bloqueio de exclusão de registros relacionados.
- Cancelamento de operações sem apagar dados já persistidos.

## 3. Tecnologias Utilizadas

- Python 3.11 ou superior
- Tkinter e ttk
- SQLite3
- JSON
- CSV
- Biblioteca padrão do Python

Não é necessário instalar bibliotecas externas para executar o projeto.

## 4. Estrutura de Pastas

```text
uc8/
├── aula20/
│   ├── main.py
│   ├── banco.py
│   ├── controller.py
│   ├── repositorio.py
│   ├── memoria.py
│   ├── modelos.py
│   ├── pagamento.py
│   ├── perfis.py
│   ├── arquivos.py
│   ├── relatorios.py
│   ├── relacoes_sqlite.py
│   ├── vinculos.py
│   ├── verificar.py
│   ├── backup_sqlite.py
│   ├── catalogo.json
│   ├── produtos.db
│   ├── backup.db
│   ├── registro-a20.md
│   ├── roteiro-demo.md
│   └── entrega-final.md
├── vendas.csv
└── readme.md
```

O banco principal é criado ou utilizado em `aula20/produtos.db`. O relatório
CSV é gravado na pasta acima de `aula20`, ou seja, `uc8/vendas.csv`.

## 5. Como Executar

Abra o PowerShell na raiz do projeto e execute:

```powershell
cd C:\Users\Pichau\Documents\senac\uc8\aula20
python .\main.py
```

Também é possível executar a partir da raiz:

```powershell
cd C:\Users\Pichau\Documents\senac\uc8
python .\aula20\main.py
```

Para executar os testes automatizados sem interface:

```powershell
cd C:\Users\Pichau\Documents\senac\uc8\aula20
python .\verificar.py
```

Para criar uma cópia do banco:

```powershell
python .\backup_sqlite.py
```

O comando acima cria `aula20/backup.db`. Para escolher outro destino:

```powershell
python .\backup_sqlite.py .\produtos.db .\backup-segunda-copia.db
```

## 6. Dados para Teste

### Produto

- Código: `P99`
- Nome: `Pizza teste`
- Preço: `5000` centavos

### Produto alternativo

- Código: `P100`
- Nome: `Pizza Especial`
- Preço: `5990` centavos

### Cliente

- Nome: `João Silva`
- Telefone: `51999999999`

### Pedido

- Cliente: selecionar o cliente recém-cadastrado.
- Produto: `P100 - Pizza Especial`
- Quantidade: `1`
- Forma de pagamento: `PIX`

### Referências válidas

Os IDs reais dos produtos podem ser conferidos na aba **Produtos SQLite**.
Os IDs dos clientes podem ser conferidos na aba **Clientes**. A venda criada
pela interface deve referenciar um cliente existente e códigos de produto
existentes.

## 7. Regras de Negócio

### Produtos e clientes

- O código do produto não pode estar vazio nem repetido.
- Nome e código não podem estar vazios.
- O preço deve ser um número inteiro positivo de centavos.
- Quantidades devem ser inteiras, positivas e limitadas a 999 unidades.
- O nome do cliente não pode estar vazio.

### Vínculos por ID

- Uma venda pode informar um `cliente_id` existente ou deixar o cliente
  não informado.
- Uma venda pode conter itens associados a códigos de produto existentes.
- A venda não pode referenciar cliente inexistente.
- Um item não pode referenciar produto inexistente.
- Alterar o nome de um cliente ou produto não altera o ID ou código usado
  pelo vínculo já existente.

### Exclusão

- Não é permitido excluir um cliente que possua vendas vinculadas.
- Não é permitido excluir um produto que possua itens de venda vinculados.
- As regras são aplicadas no contrato da aplicação e reforçadas pelo SQLite
  com `PRAGMA foreign_keys = ON` e `ON DELETE RESTRICT`.
- A exclusão vinculada exibe uma mensagem de recusa e preserva os registros.

### Confirmação e integridade

- Alterações realizadas no pedido invalidam uma prévia antiga.
- O preço do produto é comparado com o catálogo antes da confirmação.
- Se o catálogo tiver sido alterado, a venda é recusada.
- Venda e itens são gravados na mesma transação.
- Falha ao inserir um item provoca rollback da venda inteira.

## 8. Testes Realizados

Os testes foram executados em `19/11/2026` pelo comando
`python .\verificar.py`. Resultado: 31 verificações concluídas.

| Caso | Resultado |
|---|---|
| Cálculo e validação de pagamento | OK |
| Cadastro, atualização e exclusão de produto | OK |
| Cadastro, atualização e exclusão de cliente | OK |
| Produto com código duplicado | Recusado |
| Produto inexistente em venda | Recusado |
| Cliente inexistente em venda | Recusado |
| Exclusão de cliente vinculado | Bloqueada |
| Exclusão de produto vinculado | Bloqueada |
| Alteração do nome mantendo o vínculo | OK |
| Alteração do preço durante o pedido | Recusada |
| Venda com rollback em caso de falha | OK |
| Backup sem sobrescrever destino existente | OK |
| Exportação e leitura de CSV | OK |
| Migração com dados órfãos | Preservada e recusada |

Os testes cobrem memória, SQLite, chave estrangeira, migração, vendas,
itens, relatório CSV, permissões demonstrativas e vínculos por ID.

## 9. Correção Realizada Desde a A19

### Problema

A revisão identificou a necessidade de impedir exclusões que deixassem vendas
ou itens de venda apontando para registros removidos.

### Correção

Foi adicionada validação no sistema antes da exclusão de cliente e produto.
No SQLite, as tabelas relacionadas passaram a usar chave estrangeira com
`ON DELETE RESTRICT`. Migrações de bancos antigos com vendas órfãs são
recusadas sem substituição silenciosa dos dados.

### Evidência

Teste realizado em `19/11/2026` tentando remover:

- um cliente vinculado a uma venda;
- um produto vinculado a itens de venda.

Em ambos os casos o sistema bloqueou a exclusão e manteve os registros
originais. Os testes executados pelo script `verificar.py` passaram.

## 10. Limitações Conhecidas

- Não possui autenticação real; os perfis são uma simulação local.
- Não oferece controle de usuários em rede ou concorrência distribuída.
- Não possui backup automático; o backup deve ser iniciado manualmente.
- Não possui geração de relatório em PDF.
- Não possui criptografia de banco ou dados.
- Não há camada web ou API.
- O banco é local e não sincroniza entre diferentes computadores.
- Os dados podem variar conforme o banco `produtos.db` já existente.
- O catálogo inicial contém dados fictícios usados para demonstração.
- O nome visual da interface pode ser entendido como Pizzaria/Mercado; isso
  não altera a lógica de pedidos implementada.

## 11. Autor

- Nome: Ronaldo Lemos
- Curso: TDS - Noite
- Disciplina: UC8 - Python com Tkinter e ttk - Aplicações Desktop
