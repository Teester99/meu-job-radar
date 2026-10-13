# 📡 JobRadar

Monitor automatizado de **estágios em exatas, fintech e tecnologia, somente no Brasil**.

Consulta sete fontes públicas a cada três horas, filtra as vagas, deduplica e envia oportunidades pelo Telegram. Usa Python, Playwright, SQLite e GitHub Actions.

## O que busca

- **Tecnologia:** TI, desenvolvimento, software, QA/testes, automação, infraestrutura, cloud, segurança e produto digital.
- **Dados:** análise de dados, BI, ciência de dados, inteligência artificial e machine learning.
- **Exatas:** engenharia, matemática, estatística, física, química, modelagem e atuária.
- **Fintech:** bancos digitais, finanças, crédito, risco, pagamentos, investimentos e funções quantitativas.

O título precisa indicar estágio (estágio, estagiário, estagiária, intern ou internship) e uma área compatível. Cargos efetivos, trainee isolado, aprendiz e estágios de outras áreas são rejeitados.

A cobertura inclui presencial, híbrido e remoto no Brasil. País/UF e cidades reconhecidas validam a localização nacional. Remoto sem mercado declarado pode passar nas fontes nacionais; restrições estrangeiras, LATAM sem Brasil declarado e remoto mundial são rejeitados. Programas sem área no título e localizações ambíguas sem confirmação brasileira podem ser descartados.

O escopo completo e os critérios de aceite estão em [PRD.md](PRD.md).

## Fontes

| Fonte | Frequência |
|---|---|
| Gupy | Todo ciclo |
| LinkedIn Brasil | Todo ciclo |
| Sólides | Todo ciclo |
| Indeed Brasil | Todo ciclo |
| Catho | Uma vez por dia |
| GeekHunter | Uma vez por dia |
| 99Jobs | Uma vez por dia |

O perfil internacional, as consultas do LinkedIn a outros países, os scrapers internacionais e o eixo Ibéria foram removidos.

## Como funciona

1. Seleciona até dez termos de estágio por ciclo, em rodízio.
2. Consulta as fontes com até quatro scrapers concorrentes.
3. Valida estágio, área e localização brasileira.
4. Pontua a relevância e deduplica por URL e empresa+título.
5. Envia imediatamente vagas de relevância ≥ 7 com publicação não antiga.
6. Agrupa as demais no digest diário das 21h de Brasília.
7. Registra feedback 👍/👎 e envia heartbeat/alertas de saúde.

As vagas antigas pendentes no digest são revalidadas antes do envio. O histórico e o feedback continuam no banco.

## Rodar localmente

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install chromium
```

Copie `.env.example` para `.env` na raiz e preencha os dois valores:

```env
TELEGRAM_BOT_TOKEN=<token do BotFather>
TELEGRAM_CHAT_ID=<id do chat que receberá as mensagens>
```

Um ciclo:

```powershell
python main.py --perfil brasil --once
```

Brasil é o perfil padrão; `python main.py --once` também executa um ciclo. Para execução contínua, use `python main.py`.

Para inspecionar uma fonte sem gravar no banco nem notificar:

```powershell
python teste_manual.py --perfil brasil --fonte LinkedInScraper --termos "estágio dados" "estágio fintech"
```

## GitHub Actions

Cadastre `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` em **Settings → Secrets and variables → Actions**.

O [workflow de produção](.github/workflows/jobradar.yml) executa `python main.py --perfil brasil --once` a cada três horas, com timeout de 150 minutos, e persiste `data/jobs.db`.

## Configuração

| Arquivo | Responsabilidade |
|---|---|
| `config.py` | Marcadores de estágio, áreas, ferramentas, termos e mercado Brasil |
| `perfis.py` | Perfil Brasil, regras, fontes e cadências |
| `job.py` | Filtro, classificação e score |
| `main.py` | Busca, deduplicação, envio e observabilidade |
| `database/database.py` | Histórico, fila de digest, metadados e feedback |
| `notifier/telegram.py` | Telegram, digest e callbacks |
| `relatorio_precisao.py` | Métricas por fonte e semana |
| `teste_manual.py` | Inspeção de scraping sem notificações |

## Testes

```powershell
python -m pytest tests/ -q
```

O CI executa os testes a cada push. A suíte cobre parsing geográfico, estágio e áreas, bloqueio de vagas estrangeiras, proteção da fila histórica de digest, feedback e relatório de precisão.
