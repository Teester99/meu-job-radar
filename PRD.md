# PRD — JobRadar

**Documento de Requisitos de Produto**
**Versão:** 1.2
**Status:** Escopo atualizado para estágios de qualquer área e localidade
**Autora:** Liliam Kezia Oliveira Souza
**Última atualização:** 13 de outubro de 2026

## 1. Resumo

O JobRadar consulta fontes públicas de vagas a cada três horas, seleciona anúncios cujo título indica estágio, evita duplicatas e envia cada vaga nova imediatamente pelo Telegram. Não há preferência por área, país, cidade ou modalidade de trabalho. A cobertura real depende dos anúncios que cada fonte disponibiliza.

## 2. Busca e seleção

- O perfil `brasil` continua como chave interna para preservar o histórico do SQLite, mas não restringe o local das vagas.
- As consultas usam variações de estágio, estagiário, estagiária, intern e internship, inclusive formas sem acento e plurais. Dez termos são pesquisados por ciclo em rodízio.
- Gupy, LinkedIn, Sólides e Indeed são consultados em todos os ciclos. Catho, GeekHunter e 99Jobs são consultados uma vez por dia. Até quatro fontes rodam em paralelo.
- A consulta do LinkedIn não envia parâmetros de cidade, país ou modalidade. Os demais portais podem ter cobertura geográfica própria.
- O título precisa indicar estágio. Cargos efetivos, trainee isolado e aprendiz sem indicação de estágio são descartados.
- Área, local informado, país e modalidade presencial, híbrida ou remota não influenciam a aprovação.
- A classificação de estágio deve reconhecer formas masculinas, femininas, plurais e equivalentes em inglês sem aceitar palavras como `internal` por engano.

## 3. Notificação e histórico

- Cada estágio novo aprovado recebe relevância 7 e motivo `Estágio`, sem preferência por área ou local.
- Toda vaga nova aprovada é enviada imediatamente, inclusive anúncios com data de publicação antiga.
- O envio precede o registro da vaga como vista; uma falha no Telegram permite nova tentativa no próximo ciclo.
- Vagas já vistas são deduplicadas por URL sem parâmetros e por empresa mais título normalizados.
- A fila histórica de digest é revalidada com as regras atuais antes de qualquer envio às 21h de Brasília.
- Feedback 👍/👎, histórico e metadados continuam no banco existente.

## 4. Operação

O GitHub Actions executa `python main.py --perfil brasil --once` a cada três horas, com timeout de 150 minutos, e persiste `data/jobs.db`. O bot envia heartbeat diário e alerta de saúde quando as fontes falham ou retornam vazias. Token e chat ID ficam em variáveis de ambiente ou GitHub Secrets.

## 5. Limitações

- Portais nacionais podem oferecer sobretudo vagas brasileiras. Remover filtros de local não torna essas fontes globais.
- Bloqueios e mudanças nos sites podem reduzir a cobertura; o funil por fonte ajuda a detectar falhas.
- Títulos que não indicam estágio ficam de fora, mesmo que a descrição mencione um programa de estágio.
- O rodízio de termos evita consultar todas as variações em cada ciclo.

## 6. Critérios de aceite

1. Aprovar estágios de qualquer área, local e modalidade quando o título indica estágio.
2. Rejeitar cargos sem indicação de estágio no título.
3. Pesquisar os termos genéricos e consultar o LinkedIn sem parâmetros geográficos ou de modalidade.
4. Enviar alerta imediato para toda vaga nova aprovada, preservando a deduplicação e a repetição após falha de envio.
5. Revalidar a fila histórica de digest e preservar o banco e o feedback existentes.
6. Passar a suíte automatizada em `tests/`.
