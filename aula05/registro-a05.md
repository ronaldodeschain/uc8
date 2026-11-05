# A05 — organização e consultas do sistema escolar

Código do estudante:
Arquivos e interpretador executados:

## Retomada sem consulta
Quais dados devem ficar juntos no último registro válido?

Por que uma quinta nota inválida não pode alterar o nome confirmado?

O que o botão recebe em command e quando essa função é executada?

Minhas respostas iniciais: Os dados validos no ultimo registro. O que já foi confirmado é salvo em um conjunto registrado e não é afetado por um novo registro, command chama uma função e então a executa ao ser clicado

## Antes de programar
Desenho dos pais: Tk → Frame base → grupos → campos e botões:
Onde cada grid organiza seus filhos? 

Na janela, com os espaços determinados na criação da janela

Diferença entre edição, registro confirmado e retrato da consulta: Os botões estão claros em suas funções

## Preveja e depois execute
Dados sempre fictícios. C1/C2 identificam janelas de consulta diferentes.
| Caso | Sequência/verificação | Previsão | Observação | Ajuste |
|---|---|---|---|---|
| T01 | Confirmar que nome/turma, cinco notas e ações possuem os grupos/pais planejados |sim, estão separados na criação | conforme previsto| sem ajustes |
| T02 | Lia / T1 / 6,7,8,9,10; calcular e conferir média 8.0 |Conforme esperado| sim | sem ajustes |
| T03 | Antes do primeiro válido, usar Consultar |Exibe msg de nenhum registro | exibe msg de nenhum registro | sem ajustes |
| T04 | Confirmar T02 e abrir consulta C1 | abre janelas com os registros separados por turma | conforme previsto | sem ajustes |
| T05 | Editar Rui / T2 / cinco notas 5, sem calcular; observar C1 | Sem calculo, sem registro, exibe os registros anteriores | conforme previsto | sem ajuste |
| T06 | Após T02, tentar outra identificação com quinta nota abc; consultar novamente | Erro de inserção por dado invalido | conforme esperado, exibe msg de erro | sem ajuste |
| T07 | Corrigir e confirmar Rui / T2 / cinco notas 5; observar C1 e abrir C2 | Grava Rui em nova turma | grava Rui e exibe separado por turmas | sem ajuste |
| T08 | Limpar as sete entradas; observar o registro principal e as consultas | Limpa, exibe msg e as consultas exibem os salvos anteriormente| conforme previsto | sem ajustes |
| T09 | Fechar C1 pelo botão; continuar usando a principal e C2 | fecha a janela, permite a consulta, e pode fechar novamente apos exibir os registros atualizados| conforme previsto | sem ajuste |
| T10 | Abrir outra consulta e fechá-la por Escape | abre a janela da consulta dos registros e fecha com escape | a janela abre mas nao fica marcada como ativa, é necessário seleciona-la para poder fechar com escape | colocar a janela em foco ao ser aberta (edit) Feita a mudança usando focus_set|
| T11 | Abrir outra consulta e fechá-la pelo X da própria janela | a consulta traz o registro de todos os dados salvos e funciona como esperado | fecha a janela das consultas registradas | sem ajustes |
| T12 | Repetir 0/10, fora de faixa, vazios, vírgula/ponto e identificação da A04 | são feitas as validações e registra apenas se tudo estiver ok | conforme previsto | sem ajustes |
| T13 | Percorrer grupos e botões por Tab/Shift+Tab; ampliar a janela e observar campos | percorre sem problemas, tab navega, ampliar expande e ajuste o espaço do formulario | ao reduzir o tamanho está escondendo os campos do formulario | necessário verificar como redimensionar em casos que o formulario é exibido em telas menores |
| T14 | Executar sem marca-a05.png; observar o cabeçalho textual | exibe texto alternativo| conforme previsto | sem ajustes |
| T15 | Se usar PNG próprio, conferir imagem e testar arquivo inválido/ausente com fallback | imagem ok, em caso de erro exibe mensagem alternativa | conforme esperado | sem ajuste |
| T16 | Executar o script a partir de outra pasta; conferir busca ao lado do script | funciona igual por causa do (__file__) | conforme previsto | sem ajustes |
| T17 | Fechar a principal com consultas abertas; reabrir e tentar Consultar | Não permite fechar a principal com consultas abertas | conforme esperado, ao reabir as consultas não haverá registro apos fechar a principal | sem ajustes |

## Imagem local (opcional)
O programa funcionou sem imagem: sim

Se criei PNG próprio, nome/origem do arquivo e teste realizado: crab.png na origem da pasta aula05

Qual objeto conserva a referência da imagem: caso a imagem quebre tem um texto alternativo

## Fechamento sem consulta
Por que criar outra Tk/mainloop não é o contrato desta aula? Não entendi, mas o mainloop é relativo a janela em execução principal, as demais janelas são ligadas a chamada inicial do programa.

Por que C1 pode manter o registro antigo depois de um novo válido? Os registros validos e salvos ficam em uma lista salva de registros, por isso elle mantém

Qual janela cada fechamento destrói? a janela ativa

Minha dificuldade, correção e próxima tentativa:

Entregas: escolar_grupos.py, escolar_janelas.py e este registro.
Não há imagem obrigatória no pacote; use apenas arquivo próprio autorizado se optar por esse teste.

## Teoria e transferência
Consigo identificar o pai e a grade de um campo.
Minha explicação:
Consigo explicar sticky e peso de coluna no redimensionamento.
Minha explicação:
Consigo distinguir edição, confirmado e retrato da consulta.
Minha explicação:
Ligação entre o ensaio e meus arquivos da atividade:
Minha previsão antes da alteração guiada e o resultado observado:

## Continuação em casa
Arquivos/versão executados:
Pasta e comando usados:
Justificativa de 5–8 linhas ou nome do áudio de cerca de 60 segundos:
Decisão do meu código sobre hierarquia de pais, expansão dos grupos, retratos e fechamento das Toplevel:
Minha explicação / anexo:

## Checklist da interface
Controles e rótulos que conferi:
Percurso por Tab/Shift+Tab e acionamento:
Mensagem após erro e possibilidade de corrigir:
Redimensionamento e comportamento que observei:

## Pendências
O que não executei e por quê, incluindo falta de ambiente:
Caso para nova tentativa em sala:
