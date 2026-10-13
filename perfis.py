"""Perfil ativo do JobRadar: estágios em São Paulo e Guarulhos."""

from dataclasses import dataclass, field

from config import (
    CIDADES_ALVO, LOCALIDADES_BUSCA, MARCADORES_ESTAGIO, TERMOS_BUSCA, TERMOS_POR_CICLO,
)
from job import RegrasFiltro
from scrapers.catho import CathoScraper
from scrapers.geekhunter import GeekHunterScraper
from scrapers.gupy import GupyScraper
from scrapers.indeed import IndeedScraper
from scrapers.jobs99 import Jobs99Scraper
from scrapers.linkedin import LinkedInScraper
from scrapers.solides import SolidesScraper

FREQUENCIA_ALTA = "alta"
FREQUENCIA_BAIXA = "baixa"


@dataclass
class DefinicaoScraper:
    classe: type
    frequencia: str
    kwargs_extras: dict = field(default_factory=dict)


@dataclass
class Perfil:
    chave: str
    nome: str
    palavras_monitoradas: list[str]
    paises_pesquisados: list[str] | None
    regras: RegrasFiltro
    regras_eixo_secundario: RegrasFiltro | None
    eixo_secundario_ativo: bool
    eixo_secundario_rotulo: str
    termos_busca: list[str]
    termos_por_ciclo: int
    definicao_scrapers: list[DefinicaoScraper]
    max_scrapers_concorrentes: int = 4


PERFIL_BR = Perfil(
    # Chave histórica mantida para preservar deduplicação e digest no jobs.db.
    chave="brasil",
    nome="Estágios SP e Guarulhos",
    palavras_monitoradas=MARCADORES_ESTAGIO,
    paises_pesquisados=["Brasil"],
    regras=RegrasFiltro(
        keywords_forte=[],
        keywords_ambiguo=[],
        qualificadores_dados=[],
        ferramentas_titulo=[],
        qualificadores_cargo=[],
        cidades=CIDADES_ALVO,
        mercados_remoto_aceitos=None,
        exigir_estagio=True,
        apenas_estagio=True,
    ),
    regras_eixo_secundario=None,
    eixo_secundario_ativo=False,
    eixo_secundario_rotulo="",
    termos_busca=TERMOS_BUSCA,
    termos_por_ciclo=TERMOS_POR_CICLO,
    definicao_scrapers=[
        DefinicaoScraper(GupyScraper, FREQUENCIA_ALTA),
        DefinicaoScraper(
            LinkedInScraper, FREQUENCIA_ALTA,
            kwargs_extras={"localidades": LOCALIDADES_BUSCA},
        ),
        DefinicaoScraper(SolidesScraper, FREQUENCIA_ALTA),
        DefinicaoScraper(
            IndeedScraper, FREQUENCIA_ALTA,
            kwargs_extras={"localidades": LOCALIDADES_BUSCA},
        ),
        DefinicaoScraper(CathoScraper, FREQUENCIA_BAIXA),
        DefinicaoScraper(GeekHunterScraper, FREQUENCIA_BAIXA),
        DefinicaoScraper(Jobs99Scraper, FREQUENCIA_BAIXA),
    ],
)

PERFIS = {PERFIL_BR.chave: PERFIL_BR}
