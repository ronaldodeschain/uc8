# Meu registro A20 — Vínculos, recuperação e entrega final

Nome/código individual, turma e data:

## Retomada sem consulta
Minha hipótese inicial para cada item:

## Arquitetura antes do código
Desenho dos módulos, dependências e duração dos dados:

## Matriz de execução
Para cada caso, registre previsão, observado, correção e nova execução.

T01 — Vínculos válidos não apontam para IDs inexistentes.
Previsão: A previsão é de que a logica funcione conforme a RN
Observado: observa-se que a lógica está ok
Correção/reteste ou pendência: testes passam, tudo ok

T02 — Aluno/plano ausente é identificado sem alterar dados.
Previsão: Aluno/cliente ausente não altera dados pela RN
Observado: conforme previsto
Correção/reteste ou pendência: testado, sem pendencia

T03 — IDs duplicados/booleanos/negativos são recusados.
Previsão: Sim, ID chave unica, auto incrementável 
Observado: conforme previsto
Correção/reteste ou pendência: sem pendencia

T04 — Aluno com matrícula não pode ser excluído pelo contrato.
Previsão: CLiente com compra registrada não pode ser excluido 
Observado: conforme a RN
Correção/reteste ou pendência: sem ajuste, podria mudar para Aluno, mas resolvi deixar assim

T05 — SQLite bloqueia exclusão vinculada com foreign_keys habilitado.
Previsão: FK tem delete cascade restraint que impede exclusão de dados em uso
Observado: conforme previsto
Correção/reteste ou pendência: sem ajustes

T06 — Erro de integridade não apaga aluno/matrícula.
Previsão: Os dados persistem e são tratadas as entradas para evitar que interfira nos dados salvos
Observado: conforme previsto, não são apagados os dados
Correção/reteste ou pendência: sem ajustes

T07 — Recuperação liga dificuldade, apoio, nova tentativa e evidência individual.
Previsão:
Observado:
Correção/reteste ou pendência:

T08 — Entrega executa em outra pasta por README.
Previsão: Readme demonstra como executar a partir de outra pasta via terminal
Observado: observado o comportamento descrito no readme
Correção/reteste ou pendência: sem ajustes

T09 — Pendência não é registrada como sucesso nem gera nota inventada.
Previsão: pendencias foram tratadas antes de documentação dos testes
Observado: a previsão aponta o cenário atual do desenvolvimento
Correção/reteste ou pendência: sem ajustes

T10 — Arquivos executados/exportados conferidos e cópia local preservada.
Previsão: dados geram corretamente a partir dos comandos do usuário
Observado: observado o comportamento esperado
Correção/reteste ou pendência: sem ajustes

## Explicação individual
Uma decisão que consigo justificar: Segui mantendo o padrão de mercado/loja e adaptando as Fk conforme solicitado. Não havia muitos dados sobre a implementação de uma academia e traria uma complexidade que não agregaria aos exercicios propostos, os comportamentos necessários foram implementados mantendo o padrão anterior
Uma dificuldade, apoio e próxima tentativa:

## Arquivos
Versão executada e arquivos baixados:
Caminho de dados fictícios usado (se houver):
Entrega pelo fluxo combinado conferida por mim:

## Teoria e transferência
Consigo explicar quais IDs ligam aluno, plano e matrícula.
Minha explicação:
Consigo prever o efeito de referência ausente e exclusão de cadastro vinculado.
Minha explicação:
Consigo relacionar uma correção a evidência nova e a um limite da entrega.
Minha explicação:
Ligação entre o ensaio e meus arquivos da atividade:
Minha previsão antes da alteração guiada e o resultado observado:

## Continuação em casa
Arquivos/versão executados:
Pasta e comando usados:
Justificativa de 5–8 linhas ou nome do áudio de cerca de 60 segundos:
Decisão do meu código sobre vínculos por ID, referências órfãs, chave estrangeira/RESTRICT e revalidação da entrega:
Minha explicação / anexo:

## Checklist da interface
Controles e rótulos que conferi:
Percurso por Tab/Shift+Tab e acionamento:
Mensagem após erro e possibilidade de corrigir:
Redimensionamento e comportamento que observei:

## Pendências
O que não executei e por quê, incluindo falta de ambiente:
Caso para nova tentativa em sala:

## Da demonstração à entrega
Versão demonstrada na A19 e versão entregue:
O que foi alterado:
Evidência nova da recuperação:
Limite que precisa constar no README:
