"""Estágios de qualquer área e modalidade em São Paulo ou Guarulhos."""

from urllib.parse import parse_qs, urlsplit

import pytest

from config import CIDADES_ALVO, LOCALIDADES_BUSCA, TERMOS_BUSCA
from database import database as db
from job import Job
from main import _notificar_na_hora
from perfis import PERFIL_BR, PERFIS
from scrapers.indeed import IndeedScraper, _url_busca as _url_indeed
from scrapers.linkedin import LinkedInScraper, _url_busca
from utils.filtro import filtrar_vagas


def vaga(titulo, local="São Paulo, SP", modalidade="Presencial", site="Gupy"):
    return Job(
        titulo=titulo, empresa="Empresa", local=local, modalidade=modalidade,
        link=f"https://teste.invalido/{titulo}/{local}", site=site,
    )


@pytest.mark.parametrize("titulo", [
    "Estágio em Tecnologia", "Estágio em Direito", "Estagiária de Enfermagem",
    "Estagiario de Marketing", "Programa de Estágio", "Estágio",
    "Estagiários de Tecnologia", "Intern de Design", "Internship in Education",
])
def test_aceita_estagios_de_qualquer_area(titulo):
    assert vaga(titulo).combina_com(PERFIL_BR.regras)


@pytest.mark.parametrize("titulo", [
    "QA Engineer Pleno", "Analista de Dados Júnior", "Desenvolvedor Python",
    "Engenheiro de Software Sênior", "Trainee em Tecnologia", "Jovem Aprendiz TI",
    "Internal Auditor", "Analista internacional de Dados", "Intermediário de Vendas",
    "Pessoa Monitora Estágio", "Coordenador de Estágios", "Internship Program Coordinator",
])
def test_rejeita_titulo_sem_estagio(titulo):
    assert not vaga(titulo).combina_com(PERFIL_BR.regras)


@pytest.mark.parametrize("local,modalidade", [
    ("São Paulo, SP", "Presencial"), ("Guarulhos, SP", "Híbrido"),
    ("São Paulo, São Paulo, Brasil", "Remoto"),
    ("Guarulhos - SP - Brasil", "Presencial"),
    ("Remoto - São Paulo, SP", "Remoto"),
    ("São Paulo", ""), ("Guarulhos", ""),
])
def test_aceita_cidades_alvo_em_qualquer_modalidade(local, modalidade):
    assert vaga("Estágio em Direito", local, modalidade).combina_com(PERFIL_BR.regras)


@pytest.mark.parametrize("local", [
    "Recife, PE", "Campinas, SP", "Osasco, SP", "Lisboa", "Seattle, WA",
    "Remote - India", "Remote - Worldwide", "Remoto - Brasil",
    "Brasil", "Não informado", "São Paulo, Portugal", "Guarulhos, EUA",
    "Grande São Paulo", "Greater São Paulo Area", "Estado de São Paulo",
    "São Paulo e Região",
])
def test_rejeita_outros_locais_ou_local_ambiguo(local):
    assert not vaga("Estágio em Direito", local).combina_com(PERFIL_BR.regras)


def test_score_igual_para_qualquer_area_local_e_modalidade():
    aprovadas, descartes = filtrar_vagas([
        vaga("Estágio em Dados", "São Paulo", "Presencial"),
        vaga("Estágio em Direito", "Guarulhos", "Híbrido"),
        vaga("Internship in Education", "Remoto - São Paulo, SP", "Remoto"),
    ], PERFIL_BR.regras)
    assert len(aprovadas) == 3
    assert {v.relevancia for v in aprovadas} == {7}
    assert {v.motivo for v in aprovadas} == {"Estágio"}
    assert not descartes


def test_todo_estagio_novo_tem_alerta_imediato_mesmo_com_publicacao_antiga():
    candidata = vaga("Estágio em Direito", "Guarulhos", "Híbrido")
    candidata.publicado_em = "há 8 meses"
    candidata.relevancia = candidata.pontuar_relevancia(PERFIL_BR.regras)
    assert candidata.publicacao_antiga
    assert _notificar_na_hora(candidata, PERFIL_BR)


def test_perfil_de_estagios_nas_duas_cidades():
    assert set(PERFIS) == {"brasil"}
    assert PERFIL_BR.paises_pesquisados == ["Brasil"]
    assert PERFIL_BR.regras.apenas_estagio
    assert PERFIL_BR.regras.cidades == CIDADES_ALVO
    assert LOCALIDADES_BUSCA == ["São Paulo, SP, Brasil", "Guarulhos, SP, Brasil"]
    assert PERFIL_BR.regras.mercados_remoto_aceitos is None
    assert not PERFIL_BR.eixo_secundario_ativo
    assert all("Intl" not in d.classe.__name__ for d in PERFIL_BR.definicao_scrapers)


def test_linkedin_consulta_as_duas_cidades_sem_filtro_de_modalidade(monkeypatch):
    parametros = parse_qs(urlsplit(_url_busca("estágio", 10, LOCALIDADES_BUSCA[1])).query)
    assert parametros == {
        "keywords": ["estágio"], "start": ["10"],
        "location": ["Guarulhos, SP, Brasil"],
    }

    chamadas = []
    scraper = LinkedInScraper(["estágio", "estagiário", "estagiária"], LOCALIDADES_BUSCA)
    monkeypatch.setattr(scraper, "_buscar_termo", lambda termo, local: chamadas.append((termo, local)) or [])
    assert scraper.buscar_vagas() == []
    assert chamadas == [(termo, local) for termo in scraper.termos_busca for local in LOCALIDADES_BUSCA]
    assert {"estágio", "estagiário", "estagiária", "estagio", "estagiario", "estagiaria"} <= set(TERMOS_BUSCA)


def test_indeed_consulta_as_duas_cidades_sem_filtro_de_modalidade(monkeypatch):
    parametros = parse_qs(urlsplit(_url_indeed("estagiária", LOCALIDADES_BUSCA[0], 10)).query)
    assert parametros == {
        "q": ["estagiária"], "l": ["São Paulo, SP, Brasil"], "start": ["10"],
    }
    chamadas = []
    scraper = IndeedScraper(["estágio"], LOCALIDADES_BUSCA)
    monkeypatch.setattr(scraper, "_buscar_termo", lambda termo, local: chamadas.append((termo, local)) or [])
    assert scraper.buscar_vagas() == []
    assert chamadas == [("estágio", local) for local in LOCALIDADES_BUSCA]


def test_digest_revalida_historico_sem_apagar_vagas(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "jobs.db"))
    db.iniciar_db()
    for v in [
        vaga("QA Engineer Pleno"), vaga("Estágio em Direito"),
        vaga("Estágio em Dados", "Portugal", "Remoto"), vaga("Estágio em Dados"),
    ]:
        db.salvar_vaga(v, perfil_chave="brasil", digest_pendente=True)
    db.salvar_vaga(vaga("Estágio em TI"), perfil_chave="internacional", digest_pendente=True)

    pendentes = db.obter_vagas_pendentes_digest("brasil", regras=PERFIL_BR.regras)
    assert [linha[0] for linha in pendentes] == ["Estágio em Direito", "Estágio em Dados"]
    assert {linha[3] for linha in pendentes} == {7}
    assert len(db.obter_vagas_pendentes_digest("brasil")) == 4
    assert len(db.obter_vagas_pendentes_digest("internacional")) == 1
