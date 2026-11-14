# Meu registro A17 — Sorveteria integrada e comparação visual

Nome/código individual, turma e data:

## Retomada sem consulta
Minha hipótese inicial para cada item:

## Arquitetura antes do código
Desenho dos módulos, dependências e duração dos dados:

## Matriz de execução
Para cada caso, registre previsão, observado, correção e nova execução.

T01 — Catálogo/clientes vêm do banco por ID, inclusive após reabrir.
Previsão: catalogo vem do banco, mas tem um json para popular inicialmente se estiver vazio
Observado: tudo testado, conforme previsto
Correção/reteste ou pendência: testes e tratamentos

T02 — Cadastro novo aparece após atualização explícita.
Previsão: Sim, apos validação, mensagem informa novo cadastro e atualiza lista
Observado: conforme previsto
Correção/reteste ou pendência: sem ajustes

T03 — Preço mudou ou produto sumiu: recusar confirmação sem venda parcial.
Previsão: confirmação depende de parcial
Observado: Sim, foi tratado anteriormente
Correção/reteste ou pendência: sem ajustes

T04 — Cliente inexistente ou não selecionado: orientar.
Previsão: Informa cliente não selecionado na previa, adiciona mesmo sem cliente definido
Observado: salva no banco mesmo sem um Id de cliente definido
Correção/reteste ou pendência: poderia validar para garantir que um cliente seja selecionado, mas acho que depende da regra de negócio então não teve essa alteração

T05 — Venda de duas unidades a 6,50 no PIX: 13,00 →11,31.
Previsão: Sim, faz o calculo da venda corretamente
Observado: conforme previsto
Correção/reteste ou pendência: sem ajuste

T06 — Falha na segunda inserção desfaz venda e itens.
Previsão: por ter tratamento, não ocorre uma falha de inserção, aparecem apenas itens validos. Só são apagados ao clicar em novo
Observado: conforme previsto, venda não é desfeita pois só é confirmada apos todas as confirmações no sistema
Correção/reteste ou pendência: sem ajuste

T07 — Sucesso grava uma venda e bloqueia nova finalização.
Previsão: Sim, precisa clicar em nova venda para reiniciar o canvas da aplicação
Observado: venda inserida no banco, necessita que seja criada nova venda para poder finalizar
Correção/reteste ou pendência: conforme teste de colega poderia limpar a tela apos confirmar a venda, mas a logica que preferi foi manter os dados aparecendo em tela até clicar em novo

T08 — Excluir cadastro vinculado é bloqueado.
Previsão: Nada impede a exclusão do cadastro, mantem exibindo o ID relacionado
Observado: testado conforme a previsão e verificado que segue esse comportamento
Correção/reteste ou pendência: Logica deveria impedir a remoção completa do sistema, o correto seria manter uma cópia de um usuário "inativo" sem exibir na lista, mas precisaria de uma lógica mais complexa

T09 — CSV usa o comprovante confirmado e mantém totais.
Previsão: CSV mantem copia dos registros mesmo apos salvar no db
Observado: conforme esperado
Correção/reteste ou pendência: sem ajustes

T10 — Comparação ttk/CTk documenta teclado/foco; ausência da dependência não bloqueia núcleo.
Previsão: Como era opcional, não fiz essa comparação com ctk
Observado: conforme previsto, não há comparação
Correção/reteste ou pendência: sem ajuste

## Explicação individual
Uma decisão que consigo justificar:
Uma dificuldade, apoio e próxima tentativa:

## Arquivos
Versão executada e arquivos baixados:
Caminho de dados fictícios usado (se houver):
Entrega pelo fluxo combinado conferida por mim:

## Teoria e transferência
Consigo explicar por que venda e itens precisam da mesma transação.
Minha explicação:
Consigo prever banco e montagem após uma falha no item.
Minha explicação:
Consigo distinguir o núcleo integrado da comparação visual opcional.
Minha explicação:
Ligação entre o ensaio e meus arquivos da atividade:
Minha previsão antes da alteração guiada e o resultado observado:

## Continuação em casa
Arquivos/versão executados:
Pasta e comando usados:
Justificativa de 5–8 linhas ou nome do áudio de cerca de 60 segundos:
Decisão do meu código sobre transação venda/itens, rollback, IDs vinculados e coerência com o catálogo:
Minha explicação / anexo:

## Checklist da interface
Controles e rótulos que conferi:
Percurso por Tab/Shift+Tab e acionamento:
Mensagem após erro e possibilidade de corrigir:
Redimensionamento e comportamento que observei:

## Pendências
O que não executei e por quê, incluindo falta de ambiente:
Caso para nova tentativa em sala:
