"""Perfil ativo do JobRadar: estágios no Brasil."""

from dataclasses import dataclass, field

from config import (
    KEYWORDS, KEYWORDS_CARGO_FORTE, KEYWORDS_CARGO_AMBIGUO,
    QUALIFICADORES_DADOS, FERRAMENTAS_TITULO, QUALIFICADORES_CARGO,
    CIDADES, MERCADOS_REMOTO_ACEITOS, TERMOS_BUSCA, TERMOS_POR_CICLO,
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
    chave="brasil",
    nome="Brasil",
    palavras_monitoradas=KEYWORDS,
    paises_pesquisados=["Brasil"],
    regras=RegrasFiltro(
        keywords_forte=KEYWORDS_CARGO_FORTE,
        keywords_ambiguo=KEYWORDS_CARGO_AMBIGUO,
        qualificadores_dados=QUALIFICADORES_DADOS,
        ferramentas_titulo=FERRAMENTAS_TITULO,
        qualificadores_cargo=QUALIFICADORES_CARGO,
        cidades=CIDADES,
        mercados_remoto_aceitos=MERCADOS_REMOTO_ACEITOS,
        exigir_estagio=True,
        aceitar_todo_brasil=True,
    ),
    regras_eixo_secundario=None,
    eixo_secundario_ativo=False,
    eixo_secundario_rotulo="",
    termos_busca=TERMOS_BUSCA,
    termos_por_ciclo=TERMOS_POR_CICLO,
    definicao_scrapers=[
        DefinicaoScraper(GupyScraper, FREQUENCIA_ALTA),
        DefinicaoScraper(LinkedInScraper, FREQUENCIA_ALTA),
        DefinicaoScraper(SolidesScraper, FREQUENCIA_ALTA),
        DefinicaoScraper(IndeedScraper, FREQUENCIA_ALTA),
        DefinicaoScraper(CathoScraper, FREQUENCIA_BAIXA),
        DefinicaoScraper(GeekHunterScraper, FREQUENCIA_BAIXA),
        DefinicaoScraper(Jobs99Scraper, FREQUENCIA_BAIXA),
    ],
)

PERFIS = {PERFIL_BR.chave: PERFIL_BR}
