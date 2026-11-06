# Meu registro A11 — Pizzaria: estados, confirmação e cancelamento

Nome/código individual, turma e data:

## Retomada sem consulta
Minha hipótese inicial para cada item:

## Arquitetura antes do código
Desenho dos módulos, dependências e duração dos dados:

## Matriz de execução
Para cada caso, registre previsão, observado, correção e nova execução.

T01 — Vazio não finaliza.
Previsão: Notifica que não pode ter pedido vazio
Observado: segue conforme previsto
Correção/reteste ou pendência: sem ajuste

T02 — Forma ausente não finaliza.
Previsão: Forma de pagamento sempre fica marcado e não pode ficar vazio
Observado: segue conforme previsto
Correção/reteste ou pendência: sem ajustes

T03 — Cancelar, X e Escape preservam montagem e itens.
Previsão: Sim, são comandos diferentes
Observado: conforme previsto
Correção/reteste ou pendência: sem pendencia

T04 — Prévia alterada depois da abertura exige nova conferência.
Previsão: Se o pedido for modificado a previa precisa ser reaberta
Observado: conforme previsto
Correção/reteste ou pendência: sem ajuste

T05 — Confirmar gera retrato com subtotal, desconto e total coerentes.
Previsão: Sim, gera e exibe corretamente a janela
Observado: conforme previsto
Correção/reteste ou pendência: foi necessário modificar a exibição na confirmação porque estava exibindo valor sem o desconto abaixo.

T06 — Pedido finalizado bloqueia mutações e segunda finalização.
Previsão: Finaliza o pedido e faz a menção a criação de novo pedido
Observado: conforme previsto
Correção/reteste ou pendência: sem ajuste

T07 — Alterar o recibo retornado não altera o comprovante guardado.
Previsão: Pedido salvo não pode ser alterado, recibos não salvos sim podem sofrer alteração
Observado: como previsto
Correção/reteste ou pendência: sem ajustes

T08 — Novo pedido limpa a montagem; cancelamento de descarte preserva-a.
Previsão: Sim, são comandos distintos na aplicação
Observado: conforme previsto
Correção/reteste ou pendência: sem ajuste

T09 — Principal continua utilizável após fechar confirmação.
Previsão: Sim, principal aguarda a confirmação para voltar a exercer função no loop
Observado: conforme previsto
Correção/reteste ou pendência: sem ajuste

## Explicação individual
Uma decisão que consigo justificar: É importante exibir o valor com e sem o desconto no comprovante, adicionada uma linha para que fique mais nítida a diferença no comprovante
Uma dificuldade, apoio e próxima tentativa:

## Arquivos
Versão executada e arquivos baixados:
Caminho de dados fictícios usado (se houver):
Entrega pelo fluxo combinado conferida por mim:

## Teoria e transferência
Consigo explicar estado e versão com papéis diferentes.
Minha explicação:
Consigo distinguir confirmação explícita de cancelamento.
Minha explicação:
Consigo justificar por que o comprovante precisa de um retrato independente.
Minha explicação:
Ligação entre o ensaio e meus arquivos da atividade:
Minha previsão antes da alteração guiada e o resultado observado:

## Continuação em casa
Arquivos/versão executados:
Pasta e comando usados:
Justificativa de 5–8 linhas ou nome do áudio de cerca de 60 segundos:
Decisão do meu código sobre estados montagem/finalizado, versão da prévia e comprovante independente:
Minha explicação / anexo:

## Checklist da interface
Controles e rótulos que conferi:
Percurso por Tab/Shift+Tab e acionamento:
Mensagem após erro e possibilidade de corrigir:
Redimensionamento e comportamento que observei:

## Pendências
O que não executei e por quê, incluindo falta de ambiente:
Caso para nova tentativa em sala:
