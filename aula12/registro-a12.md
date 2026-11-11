# Meu registro A12 — Mercado: navegação e catálogo em JSON

Nome/código individual, turma e data:

## Retomada sem consulta
Minha hipótese inicial para cada item:

## Arquitetura antes do código
Desenho dos módulos, dependências e duração dos dados:

## Matriz de execução
Para cada caso, registre previsão, observado, correção e nova execução.

T01 — Ausente retorna coleção vazia sem criar arquivo silenciosamente.
Previsão: Tem tratamento para coleção vazio
Observado: funciona como previsto
Correção/reteste ou pendência: sem ajuste

T02 — UTF-8 conserva Picolé/limão.
Previsão: sim, tem encoding na abertura do json
Observado: foi feito o tratamento
Correção/reteste ou pendência: sem ajustes

T03 — JSON malformado e conteúdo com encoding inválido não são sobrescritos.
Previsão: tem tratamento não aceita sobrescrita assim
Observado: funciona conforme previsto
Correção/reteste ou pendência: sem ajuste

T04 — Estrutura incorreta, IDs repetidos e preço inválido são rejeitados.
Previsão: sim, são rejeitados, tem tratamento em arquivos para evitar 
Observado: conforme previsto
Correção/reteste ou pendência: sem ajuste

T05 — Falha de escrita mantém o destino anterior e não anuncia sucesso.
Previsão: falha de escrita anuncia erro
Observado: tem tratamento, segue conforme previsto
Correção/reteste ou pendência: sem ajuste

T06 — Cancelar seletor não altera tela nem arquivo.
Previsão: cancelar seletor não influencia o temporario nem o arquivo salvo
Observado: conforme previsto
Correção/reteste ou pendência: sem ajuste

T07 — Navegar entre abas conserva pedido e estado.
Previsão: Sim, preserva por não ser alteração, apenas navegação
Observado: conforme previsto
Correção/reteste ou pendência: sem ajuste

T08 — Exercício JSON não modifica automaticamente o catálogo em memória.
Previsão: só vai alterar ao ser salva a alteração no json
Observado: ao modificar o catalago.json na aba dentro do app a alteração é observada
Correção/reteste ou pendência: sem ajustes

## Explicação individual
Uma decisão que consigo justificar:
Uma dificuldade, apoio e próxima tentativa:

## Arquivos
Versão executada e arquivos baixados:
Caminho de dados fictícios usado (se houver):
Entrega pelo fluxo combinado conferida por mim:

## Teoria e transferência
Consigo distinguir caminho, texto, codificação e dados decodificados.
Minha explicação:
Consigo explicar por que validar JSON exige mais que aceitar a sintaxe.
Minha explicação:
Consigo prever pedido e edição depois de navegar, cancelar ou falhar na leitura.
Minha explicação:
Ligação entre o ensaio e meus arquivos da atividade:
Minha previsão antes da alteração guiada e o resultado observado:

## Continuação em casa
Arquivos/versão executados:
Pasta e comando usados:
Justificativa de 5–8 linhas ou nome do áudio de cerca de 60 segundos:
Decisão do meu código sobre leitura/escrita UTF-8, estrutura JSON, validação integral e navegação sem recriar o modelo:
Minha explicação / anexo:

## Checklist da interface
Controles e rótulos que conferi:
Percurso por Tab/Shift+Tab e acionamento:
Mensagem após erro e possibilidade de corrigir:
Redimensionamento e comportamento que observei:

## Pendências
O que não executei e por quê, incluindo falta de ambiente:
Caso para nova tentativa em sala:
