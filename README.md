# 📡 JobRadar

Monitor automatizado de **estágios de qualquer área nas cidades de São Paulo e Guarulhos (SP)**.

Consulta sete fontes públicas a cada três horas, filtra as vagas, deduplica e envia oportunidades pelo Telegram. Usa Python, Playwright, SQLite e GitHub Actions.

## O que busca

- Títulos que indiquem estágio, estagiário ou estagiária, com ou sem acento, ou os equivalentes em inglês `intern` e `internship`.
- Qualquer área e modalidade de trabalho, desde que o local do anúncio indique a cidade de São Paulo ou Guarulhos, no Brasil.

Cargos efetivos, trainee isolado e aprendiz sem indicação de estágio no título são rejeitados.

O escopo completo e os critérios de aceite estão em [PRD.md](PRD.md).

## Fontes

| Fonte | Frequência |
|---|---|
| Gupy | Todo ciclo |
| LinkedIn | Todo ciclo |
| Sólides | Todo ciclo |
| Indeed | Todo ciclo |
| Catho | Uma vez por dia |
| GeekHunter | Uma vez por dia |
| 99Jobs | Uma vez por dia |

LinkedIn e Indeed são consultados separadamente para São Paulo e Guarulhos. Nas demais fontes, o filtro valida a cidade informada em cada vaga. Anúncios com local ausente ou apenas "Brasil" não são enviados.

## Como funciona

1. Seleciona até dez termos de estágio por ciclo, em rodízio.
2. Consulta as fontes com até quatro scrapers concorrentes.
3. Exige indicação de estágio no título e local em São Paulo ou Guarulhos, sem filtrar área ou modalidade.
4. Atribui pontuação 7 e deduplica por URL e empresa+título.
5. Envia imediatamente cada estágio novo, mesmo quando a publicação é antiga.
6. Revalida a fila histórica do digest diário das 21h de Brasília.
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

`brasil` é a chave histórica do perfil, mantida para preservar o banco de vagas vistas. O perfil atual aceita somente São Paulo e Guarulhos. `python main.py --once` também executa um ciclo. Para execução contínua, use `python main.py`.

Para inspecionar uma fonte sem gravar no banco nem notificar:

```powershell
python teste_manual.py --perfil brasil --fonte LinkedInScraper --termos "estágio" "estagiaria"
```

## GitHub Actions

Cadastre `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` em **Settings → Secrets and variables → Actions**.

O [workflow de produção](.github/workflows/jobradar.yml) executa `python main.py --perfil brasil --once` a cada três horas, com timeout de 150 minutos, e persiste `data/jobs.db`.

## Configuração

| Arquivo | Responsabilidade |
|---|---|
| `config.py` | Marcadores de estágio e termos de busca |
| `perfis.py` | Perfil de estágios, regras, fontes e cadências |
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

O CI executa os testes a cada push. A suíte cobre títulos de estágio, aceitação das duas cidades em qualquer modalidade, proteção da fila histórica de digest, feedback e relatório de precisão.
