# Meu registro A08 — Sorveteria: pagamentos e arredondamento

Nome/código individual, turma e data:

## Retomada sem consulta
Minha hipótese inicial para cada item:

## Arquitetura antes do código
Desenho dos módulos, dependências e duração dos dados:

## Matriz de execução
Para cada caso, registre previsão, observado, correção e nova execução.

T01 — R$100,00 → 87,00 dinheiro/PIX; 92,00 débito; 100,00 crédito1x.
Previsão: calculos sendo efetivados por meio de pagamento
Observado: conforme previsto
Correção/reteste ou pendência: não há pagamento segmentado, apenas exibe o calculo sem tratar o restante

T02 — R$0,50 no PIX → R$0,44 com HALF_UP.
Previsão: calculo funcionado como previsto
Observado: calculo feito sem erros
Correção/reteste ou pendência: sem ajustes

T03 — Duas chamadas iguais produzem resultados iguais e não alteram os itens.
Previsão: modifiquei para que ele aceite adição de produtos e subtração 
Observado: se adicionar/subtrair altera a quantidade total do item
Correção/reteste ou pendência: Sem mais ajustes

T04 — Trocar PIX/crédito/PIX recalcula do subtotal original.
Previsão: Sim, troca o calculo ao calcular a previa
Observado: conforme previsto
Correção/reteste ou pendência: sem ajuste

T05 — Forma vazia ou desconhecida: erro orientado.
Previsão: forma não fica vazia, sempre mantem uma seleção, o valor vazio aponta erro de valor
Observado: conforme previsto
Correção/reteste ou pendência: sem ajustes

T06 — Valor com letras, NaN/inf, negativo, milhares ou mais de duas casas: recusar. 
Previsão: tratamento de erro por entrada inválida funciona
Observado: conforme previsto
Correção/reteste ou pendência: sem ajuste

T07 — Subtotal = desconto +total após arredondamento.
Previsão: Aplica o valor corretamente ao clicar em calcular previa
Observado: conforme previsto
Correção/reteste ou pendência: foi modificada a janela pra fazer mais sentido, agora há apenas o botão para selecionar o valor e calcular a previa

T08 — Validações de quantidade e catálogo da A07 preservadas.
Previsão: sim, código reutilizado
Observado: conforme previsto
Correção/reteste ou pendência: sem ajustes

## Explicação individual
Uma decisão que consigo justificar: adicionei o botão de subtrair para ter maior controle da quantidade, sem ter esse controle uma entrada errada faria que o programa tivesse que ser reiniciado para fazer um novo input
Uma dificuldade, apoio e próxima tentativa:

## Arquivos
Versão executada e arquivos baixados:
Caminho de dados fictícios usado (se houver):
Entrega pelo fluxo combinado conferida por mim:

## Teoria e transferência
Consigo distinguir subtotal, desconto e total.
Minha explicação:
Consigo explicar por que Decimal recebe texto e onde ocorre o arredondamento.
Minha explicação:
Consigo prever o efeito de repetir uma conferência sem mudar os itens.
Minha explicação:
Ligação entre o ensaio e meus arquivos da atividade:
Minha previsão antes da alteração guiada e o resultado observado:

## Continuação em casa
Arquivos/versão executados:
Pasta e comando usados:
Justificativa de 5–8 linhas ou nome do áudio de cerca de 60 segundos:
Decisão do meu código sobre funções puras de pagamento, Decimal de texto, ROUND_HALF_UP e subtotal preservado:
Minha explicação / anexo:

## Checklist da interface
Controles e rótulos que conferi:
Percurso por Tab/Shift+Tab e acionamento:
Mensagem após erro e possibilidade de corrigir:
Redimensionamento e comportamento que observei:

## Pendências
O que não executei e por quê, incluindo falta de ambiente:
Caso para nova tentativa em sala:
