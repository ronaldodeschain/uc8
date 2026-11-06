# Meu registro A10 — Pizzaria: transferir o modelo de pedido

Nome/código individual, turma e data:

## Retomada sem consulta
Minha hipótese inicial para cada item:

## Arquitetura antes do código
Desenho dos módulos, dependências e duração dos dados:

## Matriz de execução
Para cada caso, registre previsão, observado, correção e nova execução.

T01 — Mussarela média 35,00 +dois refrigerantes 6,00: total 47,00.
Previsão: refrigerante 5,00. Total 45,00
Observado: conforme previsto
Correção/reteste ou pendência: sem ajuste

T02 — Pizza com tamanho desconhecido: recusar.
Previsão: Se os atributos não forem preenchidos não aceita
Observado: modelo trata a entrada de tamanho, não aceita se estiver fora do escopo
Correção/reteste ou pendência: sem ajustes

T03 — Bebida e pizza coexistem com IDs distintos.
Previsão: Sim, usam composição com Produto, cada um tem seus atributos distintos
Observado: tudo conforme o previsto
Correção/reteste ou pendência: sem ajustes

T04 — Atualizar/remover preserva alvo por ID.
Previsão: O ID do produto não some se for removido, fica ligado ao produto
Observado: atualizar não modifica o ID do produto e a remoção não altera o ID
Correção/reteste ou pendência: sem ajustes

T05 — Quantidades inválidas mantêm o pedido anterior.
Previsão: quantidade inválida é tratada e não permite 
Observado:
Correção/reteste ou pendência:

T06 — Pagamento usa as mesmas regras da A08, sem desconto acumulado.
Previsão:
Observado:
Correção/reteste ou pendência:

T07 — Comparação de eventos não duplica o modelo nem exige migração.
Previsão:
Observado:
Correção/reteste ou pendência:

T08 — Demonstração opcional informa ausência da biblioteca sem instalar nada.
Previsão:
Observado:
Correção/reteste ou pendência:

## Explicação individual
Uma decisão que consigo justificar:
Uma dificuldade, apoio e próxima tentativa:

## Arquivos
Versão executada e arquivos baixados:
Caminho de dados fictícios usado (se houver):
Entrega pelo fluxo combinado conferida por mim:

## Teoria e transferência
Consigo separar o que mudou do que foi reutilizado.
Minha explicação:
Consigo explicar composição apontando a referência entre objetos.
Minha explicação:
Consigo mostrar como código/tamanho/preço chegam ao pedido.
Minha explicação:
Ligação entre o ensaio e meus arquivos da atividade:
Minha previsão antes da alteração guiada e o resultado observado:

## Continuação em casa
Arquivos/versão executados:
Pasta e comando usados:
Justificativa de 5–8 linhas ou nome do áudio de cerca de 60 segundos:
Decisão do meu código sobre transferência Produto/Pizza/Bebida, composição e contrato do pedido:
Minha explicação / anexo:

## Checklist da interface
Controles e rótulos que conferi:
Percurso por Tab/Shift+Tab e acionamento:
Mensagem após erro e possibilidade de corrigir:
Redimensionamento e comportamento que observei:

## Pendências
O que não executei e por quê, incluindo falta de ambiente:
Caso para nova tentativa em sala:
