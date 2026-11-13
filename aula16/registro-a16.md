# Meu registro A16 — Controllers e contratos: concluir clientes

Nome/código individual, turma e data:

## Retomada sem consulta
Minha hipótese inicial para cada item:

## Arquitetura antes do código
Desenho dos módulos, dependências e duração dos dados:

## Matriz de execução
Para cada caso, registre previsão, observado, correção e nova execução.

T01 — Controller executa sem importar Tkinter.
Previsão: sim, conforme executado em testes 
Observado: sim, controller pode ser usando sem GUI
Correção/reteste ou pendência: testes confirmam

T02 — Mesmo contrato com memória/SQLite inclui, lista e edita por ID.
Previsão: contrato igual, adaptado para sqlite
Observado: contrato segue inalterado
Correção/reteste ou pendência: sem ajustes

T03 — Memória começa vazia numa nova instância; SQLite reabre com dados.
Previsão: Sim, memoria nao tem dados inicialmente carregados, apenas no caso de catalogo que já há uma inserção para alimentar o sqlite caso não hajam dados
Observado: conforme observado, campos ficam vazios ao iniciar o app
Correção/reteste ou pendência: sem ajustes

T04 — Editar/excluir clientes mantém alvo por ID.
Previsão: Sim, alterações são feitas por ID, tratamento garante isso
Observado: ocorre conforme previsto
Correção/reteste ou pendência: sem ajuste

T05 — Cancelar exclusão de cliente não altera banco nem lista.
Previsão: Sim, cancelar a exclusão não altera nada no banco. Apenas apos selecionar e clicar em botão relativo é que faz alteração
Observado: conforme previsto
Correção/reteste ou pendência: testes ok

T06 — Tipo de cadastro desconhecido é rejeitado.
Previsão: Sim, os tratamentos protegem
Observado: As verificações e a lógica do sistema impede que seja feito cadastro inválido
Correção/reteste ou pendência: sem ajuste

T07 — Falha do repositório é comunicada e conserva formulário.
Previsão: Sim, cada chamada no sistema tem suas validações, apenas apos tudo ser ok é feito o registro
Observado: conforme previsto
Correção/reteste ou pendência: sem ajustes

T08 — Cópia retornada pela memória não permite alterar o armazenamento por fora.
Previsão: Sim, só vai alterar o que for persistido usando as chamadas pertinentes no sistema
Observado: conforme previsto
Correção/reteste ou pendência: sem ajuste

T09 — Componentes mantêm campos/seleções independentes.
Previsão: Sim, o get busca os campos de modo independente, não deveria ter problemas de seleção
Observado: ocorre como esperado
Correção/reteste ou pendência: sem ajustes

## Explicação individual
Uma decisão que consigo justificar:
Uma dificuldade, apoio e próxima tentativa:

## Arquivos
Versão executada e arquivos baixados:
Caminho de dados fictícios usado (se houver):
Entrega pelo fluxo combinado conferida por mim:

## Teoria e transferência
Consigo seguir uma chamada da interface ao controller e ao repositório.
Minha explicação:
Consigo descrever o contrato e o que fica igual nas duas implementações.
Minha explicação:
Consigo distinguir a duração dos dados em memória e SQLite.
Minha explicação:
Ligação entre o ensaio e meus arquivos da atividade:
Minha previsão antes da alteração guiada e o resultado observado:

## Continuação em casa
Arquivos/versão executados:
Pasta e comando usados:
Justificativa de 5–8 linhas ou nome do áudio de cerca de 60 segundos:
Decisão do meu código sobre controller, contrato de repositório, componentes e conclusão do CRUD de clientes:
Minha explicação / anexo:

## Checklist da interface
Controles e rótulos que conferi:
Percurso por Tab/Shift+Tab e acionamento:
Mensagem após erro e possibilidade de corrigir:
Redimensionamento e comportamento que observei:

## Pendências
O que não executei e por quê, incluindo falta de ambiente:
Caso para nova tentativa em sala:
