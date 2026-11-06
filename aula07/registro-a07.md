# Meu registro A07 — Sorveteria: produtos, itens e pedido

Nome/código individual, turma e data:

## Retomada sem consulta
Minha hipótese inicial para cada item:

## Arquitetura antes do código
Desenho dos módulos, dependências e duração dos dados:

## Matriz de execução
Para cada caso, registre previsão, observado, correção e nova execução.

T01 — Duas frutas a R$5,00 e três leites a R$7,50: subtotal 10,00 +22,50 =32,50.
Previsão: vai exibir os valores de acordo
Observado: conforme previsto
Correção/reteste ou pendência: funciona como esperado

T02 — Pedido novo sem itens e sem compartilhar a coleção do anterior.
Previsão: recusa e exibe erro de exceção
Observado: ocorre como previsto
Correção/reteste ou pendência: a msg funciona para desenvolvedor, poderia pensar em algo para usuário

T03 — Adicionar o mesmo código soma quantidades; nome igual com ID distinto continua distinto.
Previsão: Ele não permite editar novas quantidades do mesmo código
Observado: conforme previsto
Correção/reteste ou pendência: poderia adicionar quantidade, mas teria que tratar uma edição mais complexa.

T04 — Sem seleção: orientar e preservar pedido.
Previsão: Sem seleção ele mantem os dados já inseridos no carrinho
Observado: conforme o previsto
Correção/reteste ou pendência: poderia implementar um botão para registrar o pedido e salvar em uma lista como nos outros casos

T05 — Quantidade vazia, texto, 0, negativa, decimal ou acima de 999: recusar sem alteração.
Previsão: exibe mensagem de erro de validação
Observado: conforme previsto
Correção/reteste ou pendência: sem ajuste

T06 — Acumular quantidade acima de 999: preservar a linha anterior.
Previsão: não permite que a quantidade fique acima de 999
Observado: conforme esperado
Correção/reteste ou pendência: criei um botão para subtrair 

T07 — Total recalculado depois de cada inclusão válida.
Previsão: ele altera o valor em tempo real a cada adicão/subtração
Observado: funcionamento segue o previsto
Correção/reteste ou pendência: sem ajustes

T08 — Percurso por teclado, rótulos, expansão e execução sem imagem. 
Previsão: No momento está sem imagem, navegação por teclado funciona, mas não confirma utilizando enter,etc
Observado: conforme previsto
Correção/reteste ou pendência: poderia adicionar essa função de permitir o enter, mas não será feito no momento

## Explicação individual
Uma decisão que consigo justificar: resolvi adicionar um botão de subtrair para ter um controle maior da operação, poderia fazer apenas uma verificação de - antes do número, mas um botão acho que fica mais interessante e me ajuda a praticar a replica da lógica
Uma dificuldade, apoio e próxima tentativa:

## Arquivos
Versão executada e arquivos baixados:
Caminho de dados fictícios usado (se houver):
Entrega pelo fluxo combinado conferida por mim:

## Teoria e transferência
O que são classe e instância no ensaio das caixas:
O que __init__ prepara e qual objeto self identifica:
Por que cada pedido precisa de sua própria coleção:
Onde ficam preço, quantidade, subtotal e total no meu código:
Como meu código localiza um produto pelo código:
O que mudou no ensaio quando dois nomes apontaram para o mesmo objeto:

## Continuação em casa
Arquivos e versão que realmente executei:
Comando e pasta usados:
Justificativa de 5–8 linhas ou nome do áudio de aproximadamente 60 segundos:
Escolhi explicar independência, identificação por código ou validação antes da alteração:
Minha explicação / arquivo anexado:

## Checklist da interface
Seleção identificável — observação:
Mensagem compreensível após erro — observação:
Percurso por Tab/Shift+Tab e acionamento — observação:
Correção na mesma janela — observação:

## O que ainda não executei
Caso pendente e motivo, incluindo falta de ambiente quando houver:
Próxima tentativa que levarei para conferência:
