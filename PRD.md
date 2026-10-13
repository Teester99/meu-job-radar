# PRD — JobRadar

**Documento de Requisitos de Produto**
**Versão:** 1.3
**Status:** Estágios de qualquer área em São Paulo ou Guarulhos
**Autora:** Liliam Kezia Oliveira Souza
**Última atualização:** 13 de outubro de 2026

## 1. Resumo

O JobRadar consulta fontes públicas de vagas a cada três horas, seleciona anúncios cujo título indica estágio e cujo local é São Paulo ou Guarulhos (SP), evita duplicatas e envia cada vaga nova imediatamente pelo Telegram. Qualquer área e modalidade de trabalho é aceita.

## 2. Busca e seleção

- O perfil `brasil` continua como chave interna para preservar o histórico do SQLite; somente as cidades de São Paulo e Guarulhos são aceitas.
- As consultas usam variações de estágio, estagiário, estagiária, intern e internship, inclusive formas sem acento e plurais. Dez termos são pesquisados por ciclo em rodízio.
- Gupy, LinkedIn, Sólides e Indeed são consultados em todos os ciclos. Catho, GeekHunter e 99Jobs são consultados uma vez por dia. Até quatro fontes rodam em paralelo.
- LinkedIn e Indeed pesquisam as duas cidades separadamente, sem restringir modalidade. Nas demais fontes, o local de cada anúncio é validado depois da busca.
- O título precisa indicar estágio. Cargos efetivos, trainee isolado e aprendiz sem indicação de estágio são descartados.
- Área e modalidade presencial, híbrida ou remota não influenciam a aprovação. O local precisa indicar uma das duas cidades; região metropolitana, estado ou país sem cidade específica não bastam.
- Divergências conhecidas entre o título e o local do card, como Várzea Paulista rotulada como São Paulo, devem ser rejeitadas.
- A classificação de estágio deve reconhecer formas masculinas, femininas, plurais e equivalentes em inglês sem aceitar palavras como `internal` por engano.

## 3. Notificação e histórico

- Cada estágio novo aprovado recebe relevância 7 e motivo `Estágio`, sem preferência por área ou modalidade.
- Toda vaga nova aprovada é enviada imediatamente, inclusive anúncios com data de publicação antiga.
- O envio precede o registro da vaga como vista; uma falha no Telegram permite nova tentativa no próximo ciclo.
- Vagas já vistas são deduplicadas por URL sem parâmetros e por empresa mais título normalizados.
- A fila histórica de digest é revalidada com as regras atuais antes de qualquer envio às 21h de Brasília.
- Feedback 👍/👎, histórico e metadados continuam no banco existente.

## 4. Operação

O GitHub Actions executa `python main.py --perfil brasil --once` a cada três horas, com timeout de 150 minutos, e persiste `data/jobs.db`. O bot envia heartbeat diário e alerta de saúde quando as fontes falham ou retornam vazias. Token e chat ID ficam em variáveis de ambiente ou GitHub Secrets.

## 5. Limitações

- Algumas fontes não oferecem filtro de cidade na URL; a paginação pode deixar de fora vagas das duas cidades que não apareçam entre os primeiros resultados.
- O endpoint público do LinkedIn pode limitar acessos ou ignorar parâmetros de busca. A validação do local em cada anúncio continua obrigatória.
- Bloqueios e mudanças nos sites podem reduzir a cobertura; o funil por fonte ajuda a detectar falhas.
- Títulos que não indicam estágio ficam de fora, mesmo que a descrição mencione um programa de estágio.
- O rodízio de termos evita consultar todas as variações em cada ciclo.

## 6. Critérios de aceite

1. Aprovar estágios de qualquer área e modalidade quando o título indica estágio e o local é São Paulo ou Guarulhos.
2. Rejeitar cargos sem indicação de estágio no título e anúncios de outras cidades ou com local incerto.
3. Pesquisar termos genéricos e consultar São Paulo e Guarulhos separadamente no LinkedIn e Indeed, sem parâmetro de modalidade.
4. Enviar alerta imediato para toda vaga nova aprovada, preservando a deduplicação e a repetição após falha de envio.
5. Revalidar a fila histórica de digest e preservar o banco e o feedback existentes.
6. Passar a suíte automatizada em `tests/`.
