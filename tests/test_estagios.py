"""Estágios sem preferências de área, local ou modalidade."""

from urllib.parse import parse_qs, urlsplit

import pytest

from config import TERMOS_BUSCA
from database import database as db
from job import Job
from main import _notificar_na_hora
from perfis import PERFIL_BR, PERFIS
from scrapers.linkedin import LinkedInScraper, _url_busca
from utils.filtro import filtrar_vagas


def vaga(titulo, local="Brasil", modalidade="Presencial", site="Gupy"):
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
    ("Recife, PE", "Presencial"), ("Lisboa", "Híbrido"),
    ("Seattle, WA", "Remoto"), ("Remote - India", "Remoto"),
    ("Remote - Worldwide", "Remoto"), ("Cidade desconhecida", ""),
    ("Não informado", ""), ("São Paulo, Portugal", "Presencial"),
])
def test_aceita_qualquer_local_e_modalidade(local, modalidade):
    assert vaga("Estágio em Direito", local, modalidade).combina_com(PERFIL_BR.regras)


def test_score_igual_para_qualquer_area_local_e_modalidade():
    aprovadas, descartes = filtrar_vagas([
        vaga("Estágio em Dados", "São Paulo", "Presencial"),
        vaga("Estágio em Direito", "Lisboa", "Híbrido"),
        vaga("Internship in Education", "Remote - Worldwide", "Remoto"),
    ], PERFIL_BR.regras)
    assert len(aprovadas) == 3
    assert {v.relevancia for v in aprovadas} == {7}
    assert {v.motivo for v in aprovadas} == {"Estágio"}
    assert not descartes


def test_todo_estagio_novo_tem_alerta_imediato_mesmo_com_publicacao_antiga():
    candidata = vaga("Estágio em Direito", "Lisboa", "Híbrido")
    candidata.publicado_em = "há 8 meses"
    candidata.relevancia = candidata.pontuar_relevancia(PERFIL_BR.regras)
    assert candidata.publicacao_antiga
    assert _notificar_na_hora(candidata, PERFIL_BR)


def test_perfil_de_estagios_sem_restricoes():
    assert set(PERFIS) == {"brasil"}
    assert PERFIL_BR.paises_pesquisados is None
    assert PERFIL_BR.regras.apenas_estagio
    assert PERFIL_BR.regras.mercados_remoto_aceitos is None
    assert not PERFIL_BR.eixo_secundario_ativo
    assert all("Intl" not in d.classe.__name__ for d in PERFIL_BR.definicao_scrapers)


def test_linkedin_sem_filtro_de_local_ou_modalidade(monkeypatch):
    parametros = parse_qs(urlsplit(_url_busca("estágio", 10)).query)
    assert parametros == {"keywords": ["estágio"], "start": ["10"]}

    chamadas = []
    scraper = LinkedInScraper(["estágio", "estagiário", "estagiária"])
    monkeypatch.setattr(scraper, "_buscar_termo", lambda termo: chamadas.append(termo) or [])
    assert scraper.buscar_vagas() == []
    assert chamadas == ["estágio", "estagiário", "estagiária"]
    assert {"estágio", "estagiário", "estagiária", "estagio", "estagiario", "estagiaria"} <= set(TERMOS_BUSCA)


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
    assert [linha[0] for linha in pendentes] == [
        "Estágio em Direito", "Estágio em Dados", "Estágio em Dados",
    ]
    assert {linha[3] for linha in pendentes} == {7}
    assert len(db.obter_vagas_pendentes_digest("brasil")) == 4
    assert len(db.obter_vagas_pendentes_digest("internacional")) == 1
