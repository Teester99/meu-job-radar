
import time
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright

from job import Job, _e_remoto, _normalizar, extrair_data_publicacao
from logger import get_logger
from scrapers.base import BaseScraper

logger = get_logger()

# O LinkedIn pagina via &start= (10 vagas por página). Cada cidade é
# consultada separadamente para não perder Guarulhos entre os resultados
# de uma busca centrada em São Paulo.
MAX_PAGINAS = 3

def _url_busca(termo: str, start: int, localidade: str = "") -> str:
    parametros = {"keywords": termo, "start": start}
    if localidade:
        parametros["location"] = localidade
    return (
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
        + urlencode(parametros)
    )


class LinkedInScraper(BaseScraper):
    """Busca vagas usando o endpoint público ("guest") de busca de vagas do
    LinkedIn, o mesmo usado para carregar mais resultados sem estar logado.

    Aviso importante: esse endpoint não é oficial/documentado pelo LinkedIn.
    Ele costuma funcionar sem login, mas o LinkedIn pode bloquear ou
    rate-limitar acessos automatizados repetidos a qualquer momento —
    principalmente vindos de IPs de nuvem/datacenter, como os do GitHub
    Actions. Não é possível garantir estabilidade a longo prazo.

    Consulta cada cidade configurada, sem restringir a modalidade. O endpoint
    guest pode ignorar filtros ou limitar acessos; o filtro de Job valida o
    local de cada card antes de enviar qualquer alerta.
    """

    def __init__(
        self,
        termos_busca: list[str],
        localidades: list[str] | None = None,
    ):
        self.termos_busca = termos_busca
        self.localidades = localidades or [""]

    def buscar_vagas(self) -> list[Job]:
        vagas: list[Job] = []
        for termo in self.termos_busca:
            for localidade in self.localidades:
                vagas.extend(self._buscar_termo(termo, localidade))

        logger.info(f"[LinkedIn] {len(vagas)} vaga(s) encontrada(s) no total")
        return vagas

    def _buscar_termo(self, termo: str, localidade: str) -> list[Job]:
        logger.info(f"[LinkedIn] Buscando '{termo}' em {localidade or 'todos os locais'}")
        vagas: list[Job] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                )
            )

            try:
                for pagina in range(MAX_PAGINAS):
                    start = pagina * 10
                    url = _url_busca(termo, start, localidade)
                    page.goto(url, timeout=60000)
                    time.sleep(2)

                    cards = page.query_selector_all("li")
                    if not cards:
                        if pagina == 0:
                            logger.warning(
                                f"[LinkedIn] Nenhum resultado retornado para '{termo}' — provável "
                                "bloqueio/rate-limit do LinkedIn nesse endpoint, ou 0 vaga real."
                            )
                        break

                    for card in cards:
                        try:
                            titulo_el = card.query_selector("h3.base-search-card__title")
                            if not titulo_el:
                                continue
                            titulo = titulo_el.inner_text().strip()

                            empresa_el = card.query_selector("h4.base-search-card__subtitle a")
                            empresa = empresa_el.inner_text().strip() if empresa_el else "Não informado"

                            local_el = card.query_selector(".job-search-card__location")
                            local = local_el.inner_text().strip() if local_el else "Não informado"

                            modalidade = "Remoto" if _e_remoto(_normalizar(local)) else ""

                            link_el = card.query_selector("a.base-card__full-link")
                            link = link_el.get_attribute("href") if link_el else None
                            if not link:
                                continue
                            link = link.split("?")[0]

                            publicado_em = extrair_data_publicacao(card.inner_text())

                            vagas.append(Job(
                                titulo=titulo,
                                empresa=empresa,
                                local=local,
                                link=link,
                                site="LinkedIn",
                                publicado_em=publicado_em,
                                modalidade=modalidade,
                            ))
                        except Exception as e:
                            logger.warning(f"[LinkedIn] Erro ao processar card: {e}")
                            continue

            except Exception as e:
                logger.error(f"[LinkedIn] Erro ao buscar '{termo}': {e}")
            finally:
                browser.close()

        return vagas
