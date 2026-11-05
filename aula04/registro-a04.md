# A04 — testes do sistema escolar fictício

Código do estudante:
Arquivo e interpretador executados:

## Retomada sem consulta
O que deve acontecer ao último registro quando a última entrada é inválida?

Minha resposta inicial:  O último registro é preservado na lista


O que get devolve? Como vírgula decimal é normalizada na A03?



Minha resposta inicial: get devolve o valor da variavel associada,  virgula normalizada com replace

Digitar um novo nome confirma uma nova consulta? Por quê?

Minha resposta inicial: Só confirma quando ela é calculada, só modificar o nome no campo não faz alteração nenhuma.


## Antes de programar
Quais valores pertencem ao mesmo registro confirmado?

os que são calculados entrada junto com o calculo inicial

Quantidade de notas exigida e intervalo permitido:

5 notas em um intervalo de 0-10

Minha previsão para a média de 6, 7, 8, 9 e 10:

8.0

Por que validar a quantidade antes de dividir?

é importante sempre tratar as entradas antes de seguir para proximas etapas do desenvolvimento

## Preveja e depois execute
Use identificação e notas fictícias. Nos casos com sequência, refaça o válido indicado.
| Caso | Entrada/ação | Previsão | Observação | Ajuste |
|---|---|---|---|---|
| T01 | Abrir e Exibir antes de Calcular média | Exibir mostra msg de que não registros| ocorre o previsto  | sem ajustes |
| T02 | Lia / T1 / notas 6, 7, 8, 9, 10 | mostra o registro com os dados e o calculo correto | conforme previsão | sem ajustes |
| T03 | Cinco notas zero, com identificação preenchida | | | |
| T04 | Cinco notas 10, com identificação preenchida | registro feito com media 0 | conforme esperado | sem ajustes |
| T05 | Notas 7,5 / 8 / 6,5 / 9 / 7; repetir usando ponto decimal | não permite o , aponta erro| exibe mensagem de erro | poderia fazer o tratamento para aceitar ambos |
| T06 | Após registrar T02, editar para Rui / T2 / cinco notas 5; somente Exibir | Exibir não salva registro| exibir vai mostrar os dados registrados no programa | sem ajustes |
| T07 | Após T02, tentar Rui / T2 / 5, 5, 5, 5, abc | não permite registro por erro de validação | conforme esperado | sem ajustes |
| T08 | Corrigir a última nota de T07 para 5 e Calcular média | aceita e registra Rui| conforme esperado  | sem ajustes |
| T09 | Nome vazio ou só espaços; repetir com turma vazia ou só espaços | msg de erro por nome vazio| conforme esperado | sem ajustes |
| T10 | Cada nota vazia, só espaços ou letras; uma alteração por vez | msg de nota invalida | conforme esperado | sem ajustes |
| T11 | Cada nota -0,1 ou 10,1; uma alteração por vez |  erro de nota fora do intervalo| conforme esperado | sem ajustes |
| T12 | Nome/turma/notas com espaços nas pontas; nome composto e acentos | Strip remove espaços extras | conforme esperado | sem ajuste |
| T13 | Após um válido, Limpar campos e depois Exibir | Vai exibir os registros registrados, com redundancia, na lista| conforme esperado | sem ajustes |
| T14 | Notas 6 / 6 / 6 / 6 / 6,4; comparar média guardada e exibida | só aceita . e não , vai mostrar erro| com os dados utilizando . vai ter o retorno 6.1 | poderia tratar para aceitar ,  |
| T15 | No terminal, lista com quatro notas e depois seis; uma tentativa por vez | 4 não é aceito e aponta erro, mesma coisa com 6| Nenhum registro confirmado, são necessárias 5 notas | sem ajuste |
| T16 | Fechar, reabrir e Exibir | não mantém os dados persistidos| exibe mensagem de que não hé registros | sem ajuste |

## Uso da interface
Percorri nome, turma, cinco notas e botões com Tab/Shift+Tab:

Ele navega como esperado

Acionei um botão usando o teclado:

acionar botões não funciona via teclado

Conferi rótulos e redimensionamento:

funcionando conforme esperado

Mensagem que precisei melhorar:

as de tratamento de erro

Colega que testou (código combinado):

## Fechamento sem consulta
Qual a diferença entre sum(notas) e len(notas)?

sum é função para somar os valores, len devolve o tamanho de notas

Por que uma lista nova de números ajuda a preservar a confirmação?

A lista salva os dados validos e ao inserir novos dados eles também serão validados antes de salva-los

Qual dado o painel deve mostrar se eu editar a quinta nota sem calcular?

se for clicado o exibir, mostra todos os registros salvos anteriormente.

Formatar com uma casa muda a média guardada?

O que é salvo não é alterado posteriormente, será salvo um novo calculo

Minha dificuldade, ajuste e próxima tentativa:

Ainda me refamiliarizando

Entregas: medias.py, sistema_escolar.py e este registro preenchido.

## Teoria e transferência
Consigo explicar o que sum e len calculam.
Minha explicação:

sim, foi explicado anteriormente, sum é soma, len busca o total de itens

Consigo distinguir uma lista de widgets de uma lista de textos/números.
Minha explicação:

Consigo prever o registro após erro na quinta nota.
Minha explicação: Sim, ele devolve um erro de validação e não salva

Ligação entre o ensaio e meus arquivos da atividade:
Minha previsão antes da alteração guiada e o resultado observado:

## Continuação em casa
Arquivos/versão executados:
Pasta e comando usados:
Justificativa de 5–8 linhas ou nome do áudio de cerca de 60 segundos:
Decisão do meu código sobre lista, laço, sum/len, cinco notas e confirmação integral:
Minha explicação / anexo:

## Checklist da interface
Controles e rótulos que conferi:
Percurso por Tab/Shift+Tab e acionamento:
Mensagem após erro e possibilidade de corrigir:
Redimensionamento e comportamento que observei:

## Pendências
O que não executei e por quê, incluindo falta de ambiente:
Caso para nova tentativa em sala:
