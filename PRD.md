# PRD — JobRadar

**Documento de Requisitos de Produto**
**Versão:** 1.1
**Status:** Escopo atualizado para estágios no Brasil
**Autora:** Liliam Kezia Oliveira Souza
**Última atualização:** 13 de outubro de 2026

## 1. Resumo executivo

JobRadar monitora **estágios em exatas, fintech e tecnologia, exclusivamente no Brasil**. Consulta sete fontes públicas a cada três horas, valida estágio, área e localização, pontua a relevância, deduplica e notifica pelo Telegram. A execução usa GitHub Actions e SQLite versionado no Git.

Esta demanda substitui os cargos efetivos de Dados/BI e QA pelo foco em estágios. O perfil internacional, as consultas a outros países, WeWorkRemotely e o eixo Ibéria foram removidos da configuração ativa.

## 2. Contexto e público-alvo

A checagem manual de vários portais é demorada, repetitiva e sujeita a perder oportunidades recentes. O público-alvo passa a ser estudante buscando estágio nas áreas de exatas, tecnologia ou fintech no Brasil.

A proposta de valor é receber oportunidades compatíveis com o nível de estágio, com empresa, localização, modalidade, relevância e link de candidatura.

## 3. Objetivos e métricas

| Objetivo | Métrica |
|---|---|
| Encontrar estágios compatíveis | Aprovação e feedback por fonte |
| Entregar apenas vagas brasileiras | Nenhuma vaga de mercado exclusivamente estrangeiro aprovada |
| Evitar cargos fora do nível | Nenhum cargo efetivo, trainee ou aprendiz sem indicação de estágio aprovado |
| Evitar repetição | Deduplicação por URL e empresa+título |
| Reduzir excesso de mensagens | Imediatas para relevância ≥ 7; demais em digest diário |
| Manter a operação observável | Funil por fonte, alerta de saúde e heartbeat diário |
| Manter o custo de infraestrutura | GitHub Actions e SQLite, sem servidor próprio |

As métricas do escopo anterior são referências históricas; não representam a precisão do novo radar de estágios.

## 4. Escopo

### 4.1 No escopo

- Estágios presenciais, híbridos e remotos no Brasil.
- Tecnologia: TI, informática, computação, sistemas, desenvolvimento, software, web, mobile, QA/testes, automação, DevOps, cloud, infraestrutura, redes, segurança, suporte técnico e produto digital.
- Dados: análise de dados, BI, analytics, ciência de dados, inteligência artificial e machine learning.
- Exatas: matemática, estatística, física, química, engenharia, pesquisa operacional, modelagem e atuária.
- Fintech e funções correlatas: bancos digitais, finanças, mercado financeiro, crédito, risco, pagamentos, investimentos, fraude, análise quantitativa, open finance e open banking.
- Títulos em português e inglês, incluindo estágio, estagiário, estagiária, intern e internship.
- Sete fontes: Gupy, LinkedIn Brasil, Sólides, Indeed Brasil, Catho, GeekHunter e 99Jobs.
- Rodízio de termos, score, deduplicação, Telegram, feedback, digest e monitoramento de saúde.

### 4.2 Fora do escopo

- Busca internacional, portais internacionais, consultas a países estrangeiros e eixo Ibéria.
- Remoto exclusivamente para outros países, LATAM sem Brasil declarado e anúncios de escopo mundial.
- Cargos efetivos de qualquer senioridade, trainee e jovem aprendiz sem indicação explícita de estágio.
- Estágios de outras áreas ou programas genéricos sem área identificável no título.
- Classificação por currículo com IA, candidatura automática, dashboard e multiusuário.
- Scraping que exige login e normalização completa de datas relativas.

## 5. Jornada

1. O sistema consulta as fontes a cada três horas com um bloco de termos de estágio.
2. Valida indicação de estágio, área compatível e localização brasileira.
3. Deduplica e pontua as vagas aprovadas.
4. Envia vagas recentes de relevância alta imediatamente; agrupa o restante no resumo das 21h de Brasília.
5. O usuário abre o link e registra feedback 👍/👎.
6. O relatório de precisão orienta ajustes nas fontes e termos.

## 6. Requisitos funcionais

### 6.1 Busca — RF-01

- **RF-01.1:** Executar somente o perfil `brasil`, padrão da CLI.
- **RF-01.2:** Consultar sete fontes com até quatro scrapers concorrentes, cada um com browser próprio.
- **RF-01.3:** Usar rodízio de dez termos por ciclo, persistindo o offset em metadados.
- **RF-01.4:** Gupy, LinkedIn, Sólides e Indeed rodam a cada ciclo; Catho, GeekHunter e 99Jobs, uma vez por dia.
- **RF-01.5:** Todos os termos devem buscar estágio; ferramentas também devem estar associadas a estágio.
- **RF-01.6:** LinkedIn consulta somente Brasil. Não executar scrapers nem consultas internacionais.
- **RF-01.7:** Timeout ou falha de uma fonte não deve derrubar o ciclo.

### 6.2 Filtro — RF-02

- **RF-02.1:** Exigir indicação explícita de estágio no título. Reconhecer formas masculinas, femininas, plurais, sem acentos e equivalentes em inglês.
- **RF-02.2:** Exigir área compatível no título, por cargo específico, área qualificadora ou ferramenta associada a estágio.
- **RF-02.3:** Usar bordas de palavra para evitar falsos positivos como “internal”, “biologia” ou “terapia”.
- **RF-02.4:** Aceitar localização brasileira por país, cidade reconhecida ou UF, em todo o território nacional. Normalizar os formatos “Cidade, UF”, “Cidade - UF” e “Cidade/UF”.
- **RF-02.5:** Remoto com mercado declarado exige Brasil entre os mercados informados. Rejeitar outros países, LATAM sem Brasil e escopo mundial.
- **RF-02.6:** Remoto sem mercado declarado pode passar quando encontrado nas fontes nacionais. Local presencial/híbrido não reconhecido deve ser rejeitado.
- **RF-02.7:** Preservar a desambiguação das UFs que colidem com estados estrangeiros. Localização ambígua sem confirmação brasileira deve ser rejeitada.
- **RF-02.8:** País declarado por extenso deve prevalecer sobre inferência por UF. Uma cidade brasileira não pode contornar uma restrição estrangeira.
- **RF-02.9:** Título indicando híbrido ou presencial prevalece sobre modalidade remota atribuída pela fonte.
- **RF-02.10:** Revalidar vagas já pendentes no digest pelas regras atuais, impedindo envio de cargos e mercados do escopo anterior.

### 6.3 Relevância — RF-03

- **RF-03.1:** Pontuar vagas aprovadas por sinais conhecidos, sem ML.
- **RF-03.2:** Estágio recebe o bônus de senioridade alvo. Trainee tem classificação separada e não satisfaz a exigência de estágio.
- **RF-03.3:** Exibir relevância e motivo de aprovação na notificação.
- **RF-03.4:** Recalcular relevância das vagas históricas aprovadas antes do digest.

### 6.4 Deduplicação — RF-04

- Identificador por hash da URL sem query string.
- Chave secundária por empresa+título normalizados.
- Migrações idempotentes preservam histórico e feedback.

### 6.5 Notificação — RF-05

- Relevância ≥ `LIMIAR_DIGEST_IMEDIATO` (7) e publicação não antiga: envio imediato.
- Publicações com meses/anos ou relevância menor: digest diário ranqueado às 21h BRT.
- Notificar antes de salvar no caminho imediato; falha permite nova tentativa.
- Limpar fila de digest somente após confirmação de todas as mensagens.
- Não enviar notificações exploratórias internacionais.
- Manter histórico anterior no banco; revalidá-lo antes de qualquer envio pelo digest.

### 6.6 Feedback e métricas — RF-06

- Botões 👍/👎 gravam feedback no banco.
- Consumir callbacks por polling com offset persistido.
- Relatório de precisão por fonte e semana.
- Situação de candidatura permanece independente da métrica de feedback.

### 6.7 Resiliência e observabilidade — RF-07

- Heartbeat diário e alerta quando pelo menos metade das fontes falhar ou retornar vazia.
- Abortar quando banco existente vier suspeitamente vazio.
- Logs não expõem token do Telegram.
- Workflow com timeout de 150 minutos, abaixo do intervalo de três horas.
- Persistir banco com retry de push, preservando o mecanismo atual.

### 6.8 Configuração — RF-08

- Apenas `brasil` disponível na CLI e em `PERFIS`.
- Cargos, áreas, ferramentas, termos e mercados definidos em `config.py`.
- Fontes e regras declaradas em `perfis.py`.
- Workflow executa `python main.py --perfil brasil --once`.
- Metadados mantêm o sufixo `brasil` para preservar a continuidade operacional.

## 7. Requisitos não funcionais

| Categoria | Requisito |
|---|---|
| Custo | Sem servidor próprio; GitHub Actions e SQLite |
| Performance | Até quatro scrapers paralelos; dez termos por ciclo |
| Confiabilidade | Sem marcar vaga vista antes de envio ou enfileiramento |
| Segurança | Token e chat ID via ambiente/GitHub Secrets |
| Qualidade | Testes de estágio, área, localização e fila histórica no CI |
| Transparência | Motivo de aprovação e funil por fonte disponíveis |

## 8. Arquitetura

```text
GitHub Actions (a cada 3h)
  → main.py --perfil brasil --once
  → bloco de termos de estágio em rodízio
  → 7 fontes nacionais (até 4 em paralelo)
  → estágio + área + Brasil
  → score e deduplicação
  → Telegram imediato / digest revalidado
  → heartbeat e alertas
  → persistência de data/jobs.db
```

## 9. Riscos e limitações

- Mudanças de layout ou bloqueios podem reduzir cobertura; o funil e os alertas evidenciam falhas.
- Programas genéricos sem área no título não podem ser classificados pelos cards atuais e são rejeitados.
- Localizações desconhecidas e UFs ambíguas sem confirmação brasileira podem gerar falsos negativos.
- O rodízio controla custo: ampliar os termos aumenta o tempo até a lista inteira ser pesquisada novamente.
- A precisão e os rendimentos das fontes precisam ser medidos novamente para o foco em estágio.

## 10. Roadmap

- Ampliar cobertura de programas de estágio por dados da descrição.
- Melhorar reconhecimento de municípios brasileiros e localizações ambíguas.
- Medir latência anúncio → notificação e normalizar datas relativas.
- Adicionar fontes públicas de estágios conforme rendimento medido.

## 11. Critérios de aceite

1. Aprovar estágios brasileiros de tecnologia, dados, exatas e fintech.
2. Rejeitar vagas efetivas, trainee isolado, aprendiz e estágios de áreas incompatíveis.
3. Consultar somente Brasil e não disponibilizar perfil internacional.
4. Rejeitar mercado exclusivamente estrangeiro, LATAM sem Brasil e remoto mundial.
5. Aceitar presencial/híbrido de cidades brasileiras fora da lista regional quando país/UF for reconhecido.
6. Não enviar pendências históricas fora do escopo atual.
7. Preservar deduplicação, histórico, feedback e tentativas após falha de envio.
8. Passar a suíte automatizada em `tests/`.
