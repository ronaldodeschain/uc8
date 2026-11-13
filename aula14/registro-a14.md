# Meu registro A14 — SQLite: produtos que permanecem após reabrir

Nome/código individual, turma e data:

## Retomada sem consulta
Minha hipótese inicial para cada item:

## Arquitetura antes do código
Desenho dos módulos, dependências e duração dos dados:

## Matriz de execução
Para cada caso, registre previsão, observado, correção e nova execução.

T01 — Tabela criada sem apagar linhas existentes.
Previsão: A tabela tem tratamento que evita que apague o que já existe. Caso não exista dados no banco ele copia o catalogo.json para popular inicialmente
Observado: segue a previsão
Correção/reteste ou pendência: Tudo de acordo com o esperado

T02 — Preço 7,50 gravado como 750 inteiro.
Previsão: tem tratamento para gravar corretamente
Observado: segue de acordo com a logica do sistema
Correção/reteste ou pendência: sem ajuste

T03 — Nome com apóstrofo tratado como parâmetro literal.
Previsão: Sim, gravado em string sem problemas
Observado: já testado e funcionando como previsto
Correção/reteste ou pendência: tudo ok

T04 — Nome vazio/preço inválido não insere registro.
Previsão: Não insere e notifica o problema relativo a falha
Observado: A mensagem aparece corretamente
Correção/reteste ou pendência: sem ajustes

T05 — IDs positivos únicos, independentes da posição visual.
Previsão: Sim, tem tratamento para evitar ID duplicado
Observado: mensagem aparece conforme previsto
Correção/reteste ou pendência: tudo de acordo com o plano

T06 — Reabrir o mesmo arquivo conserva produtos.
Previsão: sim, eles persistem então conserva sem problemas
Observado: segue conforme previsto
Correção/reteste ou pendência: sem ajustes nessa etapa

T07 — Falha de conexão/gravação não deve aparecer como sucesso.
Previsão: Sim, se falhou tem tratamento para evitar que seja gravado 
Observado: os tratamentos para erros funcionam conforme esperado
Correção/reteste ou pendência: sem ajustes

T08 — Conexões fechadas; importar não cria banco.
Previsão: Sim, conn.close() garante que não sejam feitas operações posteriores no banco
Observado: a lógica faz a sua parte e protege a conexão 
Correção/reteste ou pendência: sem ajustes, a lógica por hora está ok

T09 — Pedido em memória continua separado dos produtos persistidos.
Previsão: Quando o pedido é salvo ele persiste no arquivo csv. Sem a confirmação ele segue em memória apenas.
Observado: tudo liso, conforme previsto e tratado
Correção/reteste ou pendência: sem ajustes, fiquei em duvida se deveria manter ele salvo temporariamente em memoria esperando ser adicionado com um segundo botão, mas acho que salvar apos exibir a prévia faz mais sentido

## Explicação individual
Uma decisão que consigo justificar:
Uma dificuldade, apoio e próxima tentativa:

## Arquivos
Versão executada e arquivos baixados:
Caminho de dados fictícios usado (se houver):
Entrega pelo fluxo combinado conferida por mim:

## Teoria e transferência
Consigo explicar persistência e a diferença para memória.
Minha explicação:
Consigo localizar comando, parâmetros e confirmação da gravação.
Minha explicação:
Consigo indicar quando usar JSON, CSV ou SQLite nas atividades do curso.
Minha explicação:
Ligação entre o ensaio e meus arquivos da atividade:
Minha previsão antes da alteração guiada e o resultado observado:

## Continuação em casa
Arquivos/versão executados:
Pasta e comando usados:
Justificativa de 5–8 linhas ou nome do áudio de cerca de 60 segundos:
Decisão do meu código sobre repositório, SQL parametrizado, confirmação, conexão e persistência de produtos:
Minha explicação / anexo:

## Checklist da interface
Controles e rótulos que conferi:
Percurso por Tab/Shift+Tab e acionamento:
Mensagem após erro e possibilidade de corrigir:
Redimensionamento e comportamento que observei:

## Pendências
O que não executei e por quê, incluindo falta de ambiente:
Caso para nova tentativa em sala:
