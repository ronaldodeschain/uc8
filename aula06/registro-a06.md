# Meu registro A06 — objetos e módulos

Nome/código individual:
Turma e data:

## Hipóteses sem consulta
O que fica confirmado após erro na quinta nota?
Qual a diferença entre editar, confirmar e limpar?
O que aconteceria se dois nomes apontassem para o mesmo objeto?

## Arquitetura antes do código
Pasta com aluno.py, verificar_modelo.py e main.py:
Qual arquivo contém regras? Qual cria widgets? Quem importa quem?

Main importa os demais módulos, cria o app. As regras estão em aluno para validaço e main possui algumas regras também.

O que __init__ cria em cada nova instância?
Por que duas chamadas Aluno() diferem de rui = lia?
O que self identifica em uma chamada de método?

init cria os atributos do objeto em cada instância criada. O self é o atributo do objeto criado, self referindo a ele mesmo, o objeto instanciado

## Testes executados
Preencha para cada caso: previsão | resultado observado | correção e nova tentativa.
Não marque como executado um teste ainda pendente.
- T01: Importar aluno sem Tk, sem janela e sem leitura de teclado.
  Previsão: ok
  Observado: ok
  Correção/reteste:  python -c "from aluno import Aluno; print('ok')"

- T02: Criar dois objetos; listas distintas; ambos sem média antes de confirmar.
  Previsão: False, True, None, none
  Observado: conforme previsto
  Correção/reteste: sem ajustes
- T03: Lia/T1/[6,7,8,9,10] e Rui/T2/[5,5,5,5,5]; médias 8.0 e 5.0.
  Previsão: exibe o ultimo registro com os dados conforme esperado
  Observado: conforme previsto
  Correção/reteste: poderia utilizar uma listagem de todos os resultados cadastrados como feito anteriormente
- T04: Atualizar só Lia; Rui mantém identificação, notas e média.
  Previsão: exibe os registros separados por turma, mas não há atualização possivel nesse cenário
  Observado: exibe os dois objetos separados por turma
  Correção/reteste: poderia permitir a selação de um dos objetos da lista e trazer para o formulário para edição
- T05: Após válido, tentar nome/turma vazios; preservar todo o registro.
  Previsão: as validações impedem registro de dados incompletos
  Observado: conforme previsto
  Correção/reteste: sem ajuste
- T06: Após válido, erro na quinta nota; preservar os três atributos e resumo.
  Previsão: erro na nota não valida e não registra
  Observado: conforme esperado
  Correção/reteste: 
- T07: Testar 0 e 10, vírgula/ponto, negativos, >10, nan, inf, vazio e texto.
  Previsão: negativos, fora do range, nan, inf, vazio e texto não passam na validação, não registra
  Observado: conforme previsto
  Correção/reteste: sem ajuste
- T08: Recusar quantidade diferente de cinco notas, sem alterar o válido.
  Previsão: não registra, não altera os validos
  Observado: conforme previsto
  Correção/reteste: sem ajuste
- T09: Alterar a lista de textos original após atualizar; notas confirmadas não mudam.
  Previsão: alterar a lista vai gerar um novo registro, sem alterar as anteriores, sujeito a validação da nova entrada
  Observado: conforme previsto
  Correção/reteste: sem ajustes
- T10: Executar verificar_modelo.py sem abrir GUI; cada assert corresponde a um caso. 
  Previsão: aparece mensagem informando se passou ou não passou os testes 
  Observado: conforme esperado
  Correção/reteste: poderia separar a mensagem por teste feito
- T11: Consultar antes do primeiro válido: orientação e nenhuma janela vazia.
  Previsão: não abre a janela
  Observado: não exibe nenhum registro
  Correção/reteste: sem ajuste
- T12: Confirmar Lia e abrir C1; editar Rui e errar a última nota: C1 e confirmado permanecem.
  Previsão: Não há edição de registros nesse momento do projeto, modificar cria uma nova entrada e errar a ultima nota não registra por erro de validação
  Observado: conforme previsto 
  Correção/reteste: 
- T13: Corrigir e confirmar Rui; C2 mostra Rui e C1 conserva Lia.
  Previsão: Corrigindo Rui ele registra corretamente e mostra os registros separados por turma
  Observado: conforme previsto
  Correção/reteste: sem ajustes
- T14: Limpar os sete campos; último registro e consultas continuam disponíveis.
  Previsão: Continuam disponíveis os registros confirmados 
  Observado: conforme previsto
  Correção/reteste: sem ajustes
- T15: Fechar consultas por botão, X e Escape; principal e outra consulta continuam funcionando.
  Previsão: Sim, tudo funcionando como esperado
  Observado: conforme previsto
  Correção/reteste: poderia colocar o focus() para abrir a consulta com o foco nela como feito em outros pontos dos exercícios.
- T16: Conferir grupos, rótulos, expansão e percurso Tab; funcionar sem PNG.
  Previsão: Funciona e fica o texto no lugar da imagem
  Observado: conforme previsto
  Correção/reteste: sem ajustes
- T17: Encerrar a principal e reabrir: começar sem registro; nenhum arquivo de dados gravado.
  Previsão: Nenhum dado é salvo no momento.
  Observado: Conforme previsto
  Correção/reteste: sem ajuste

## Explicação individual
Mostre dois objetos independentes e uma tentativa inválida após um válido.

Nome | turma1 | 7,8,9,8,7
Nome2 | turma2 | 10,9,6,5,4
Falho1 | turma2 | abc,10,5,-6,4

Indique a linha que confirma o conjunto e por que a interface não repete a regra.

o preenchimento dos atributos do objeto. A interface chama o método de aluno que faz as validações

O que um assert verifica? Qual caso ainda falta?

Ele faz afirmações de comparação entre duas hipóteses, não fiz verificação para um cenário em que há menos de 4 notas porque a validação impede que seja criada, mas poderia fazer um assert notas =1,2,3,4 

Minha dificuldade e próximo teste:

Penso se o editar seria para acessar os dados já cadastrados ou apenas alterar os campos ainda não validados.

Entrega: aluno.py, verificar_modelo.py, main.py e este registro.
Somente dados fictícios. A página não executa Python nem envia arquivos automaticamente.

## Teoria e transferência
Consigo apontar classe, instância, __init__ e self no exemplo.
Minha explicação:
Consigo provar que dois objetos mantêm dados independentes.
Minha explicação:
Consigo explicar a direção dos imports entre modelo, verificador e interface.
Minha explicação:
Ligação entre o ensaio e meus arquivos da atividade:
Minha previsão antes da alteração guiada e o resultado observado:

## Continuação em casa
Arquivos/versão executados:
Pasta e comando usados:
Justificativa de 5–8 linhas ou nome do áudio de cerca de 60 segundos:
Decisão do meu código sobre classe, instância, listas próprias, confirmação integral e separação aluno/verificador/GUI:
Minha explicação / anexo:

## Checklist da interface
Controles e rótulos que conferi:
Percurso por Tab/Shift+Tab e acionamento:
Mensagem após erro e possibilidade de corrigir:
Redimensionamento e comportamento que observei:

## Pendências
O que não executei e por quê, incluindo falta de ambiente:
Caso para nova tentativa em sala:
