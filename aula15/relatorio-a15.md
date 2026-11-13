# Meu registro A15 — CRUD: editar produtos e iniciar clientes

Nome/código individual, turma e data:

## Retomada sem consulta
Minha hipótese inicial para cada item:

## Arquitetura antes do código
Desenho dos módulos, dependências e duração dos dados:

## Matriz de execução
Para cada caso, registre previsão, observado, correção e nova execução.

T01 — Editar por ID preserva a identidade e não duplica linha.
Previsão: Sim, não pode utilizar o mesmo ID e ele tem auto increment também
Observado: o Crud não afeta o ID, mesmo apagando ele segue indo para o proximo ID na criação de um novo
Correção/reteste ou pendência: Tem testes para garantir que o compartamento siga conforme esperado. O verificar.py tem as verificações, redundamente falando, testados.

T02 — Editar após mover a linha altera o produto certo.
Previsão: Editar segue pelo ID, posição não interfere na edição correta
Observado: Conforme previsto
Correção/reteste ou pendência: sem ajustes

T03 — Preço/nome inválido preserva valor persistido.
Previsão: Os tratamentos preservam os dados persistidos, dados com inconsistencias não são salvos
Observado: segue conforme previsto, a logica está implementada
Correção/reteste ou pendência: tudo ok

T04 — ID inexistente não recebe mensagem de sucesso.
Previsão: Não ocorre entradas de dados com problemas de ID, id incremental evita que tenha problemas de inserção
Observado: testes e a logica cobre corretamente o cenário
Correção/reteste ou pendência: sem ajustes

T05 — Excluir sem seleção pede uma escolha.
Previsão: Sim, exibe um alerta informando que é necessário escolher um item. CRUD baseado em ID, seleção busca ID
Observado: conforme previsto
Correção/reteste ou pendência: sem ajustes necessários

T06 — Cancelar exclusão preserva dados e tela.
Previsão: Sim, só exclui ao selecionar o comando.
Observado: Botão confirma exclusão, sem click não há alteração
Correção/reteste ou pendência: sem ajustes

T07 — Confirmar exclui só o ID escolhido e atualiza lista.
Previsão: Sim, exclusão é feita por ID individualmente, lista é atualizada em tempo real
Observado: segue conforme previsto
Correção/reteste ou pendência: sem ajustes

T08 — Excluir último registro deixa lista vazia utilizável.
Previsão: Se a lista for de catalogo ele é repopulado a partir do catalago.json. Se for cliente, a lista fica vazia
Observado: fica ativo o botão para selecionar um cliente, mas sem associações a serem feitas
Correção/reteste ou pendência: poderia ter uma logica para manter ao menos um "consumidor" marcado se a lista estiver vazia

T09 — Clientes fictícios incluídos/listados e persistidos.
Previsão: Sim, clientes tem Crud e persistem, local de persistência ainda aparece na tela
Observado: conforme previsto
Correção/reteste ou pendência: não deveria manter um caminho aparente na tela, mas para fins academicos não vou alterar a exibição, mas estou ciente de que não deveria deixar

T10 — Reabrir conserva edição/exclusão efetivamente confirmadas.
Previsão: Sim, a logica de persistencia funciona corretamente
Observado: observada a previsão sobre a persistência
Correção/reteste ou pendência: sem ajustes

## Explicação individual
Uma decisão que consigo justificar:
Uma dificuldade, apoio e próxima tentativa:

## Arquivos
Versão executada e arquivos baixados:
Caminho de dados fictícios usado (se houver):
Entrega pelo fluxo combinado conferida por mim:

## Teoria e transferência
Consigo distinguir inclusão, edição e exclusão.
Minha explicação:
Consigo justificar a preservação do ID ao editar.
Minha explicação:
Consigo prever os dados após Cancelar e o comportamento com lista vazia.
Minha explicação:
Ligação entre o ensaio e meus arquivos da atividade:
Minha previsão antes da alteração guiada e o resultado observado:

## Continuação em casa
Arquivos/versão executados:
Pasta e comando usados:
Justificativa de 5–8 linhas ou nome do áudio de cerca de 60 segundos:
Decisão do meu código sobre CRUD de produtos, editar o mesmo ID, Novo, confirmação e início de clientes:
Minha explicação / anexo:

## Checklist da interface
Controles e rótulos que conferi:
Percurso por Tab/Shift+Tab e acionamento:
Mensagem após erro e possibilidade de corrigir:
Redimensionamento e comportamento que observei:

## Pendências
O que não executei e por quê, incluindo falta de ambiente:
Caso para nova tentativa em sala:
