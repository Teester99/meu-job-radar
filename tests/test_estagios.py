"""Escopo de estágios brasileiros e proteção da fila histórica de digest."""

import pytest

from config import LOCATIONS_LINKEDIN, LOCATIONS_LINKEDIN_REMOTO_APENAS
from database import database as db
from job import Job
from perfis import PERFIL_BR, PERFIS
from utils.filtro import filtrar_vagas


def vaga(titulo, local="Brasil", modalidade="Presencial", site="Gupy"):
    return Job(
        titulo=titulo, empresa="Empresa", local=local, modalidade=modalidade,
        link=f"https://teste.invalido/{titulo}/{local}", site=site,
    )


@pytest.mark.parametrize("titulo", [
    "Estágio em Tecnologia", "Estágio em TI", "Estagiário de Desenvolvimento",
    "Estagiária de Dados", "ESTAGIARIO DE QA", "Estágio em Engenharia Civil",
    "Estágio em Matemática", "Estágio em Estatística", "Estágio em Física",
    "Estágio em Química", "Estágio em Fintech", "Estágio em Crédito e Risco",
    "Estágio em Pagamentos", "Estágio em Banco Digital", "Estágio em DevOps",
    "Estágio em Python", "Estágio em SQL", "Software Engineering Intern",
    "Data Science Internship", "Estagiários de Tecnologia", "Estágio em C++",
])
def test_aceita_estagios_das_areas_alvo(titulo):
    assert vaga(titulo).combina_com(PERFIL_BR.regras)


@pytest.mark.parametrize("titulo", [
    "QA Engineer Pleno", "Analista de Dados Júnior", "Desenvolvedor Python",
    "Engenheiro de Software Sênior", "Trainee em Tecnologia", "Jovem Aprendiz TI",
    "Estágio em Direito", "Estágio em Enfermagem", "Estágio em Marketing",
    "Programa de Estágio", "Internal Auditor", "Analista internacional de Dados",
    "Estágio em Biologia", "Estágio em Terapia", "Estágio em Recrutamento",
])
def test_rejeita_outros_niveis_e_areas(titulo):
    assert not vaga(titulo).combina_com(PERFIL_BR.regras)


@pytest.mark.parametrize("local,modalidade", [
    ("Recife, PE", "Presencial"), ("Belo Horizonte - MG", "Híbrido"),
    ("Curitiba/PR", "Presencial"), ("Porto Alegre, RS", "Híbrido"),
    ("São Paulo", "Remoto"), ("Campinas", "Presencial"),
    ("Remoto - Brazil only", "Remoto"), ("Remoto", "Remoto"),
    ("Home Office", ""), ("Remoto (São Paulo - SP)", "Remoto"),
])
def test_cobertura_brasileira(local, modalidade):
    assert vaga("Estágio em Dados", local, modalidade).combina_com(PERFIL_BR.regras)


@pytest.mark.parametrize("local,modalidade", [
    ("Portugal", "Remoto"), ("Remote - Argentina", "Remoto"),
    ("Remote - LATAM", "Remoto"), ("Remote - Worldwide", "Remoto"),
    ("Seattle, WA", "Remoto"), ("São Paulo, Portugal", "Remoto"),
    ("São Paulo, SP, Portugal", "Remoto"), ("São Paulo, Portugal", "Presencial"),
    ("São Paulo, SP, França", "Remoto"),
    ("Lisboa", "Híbrido"), ("Remote - India", ""),
    ("Cidade desconhecida", "Presencial"),
])
def test_rejeita_escopo_estrangeiro_ou_local_sem_confirmacao(local, modalidade):
    assert not vaga("Estágio em Dados", local, modalidade).combina_com(PERFIL_BR.regras)


def test_titulo_hibrido_nao_vira_remoto_sem_local_brasileiro():
    assert not vaga("Estágio em Tecnologia - Híbrido", "Remoto", "Remoto").combina_com(PERFIL_BR.regras)


def test_score_prioriza_estagio_e_exibe_motivo():
    aprovadas, descartes = filtrar_vagas([vaga("Estágio em Dados")], PERFIL_BR.regras)
    assert len(aprovadas) == 1
    assert aprovadas[0].senioridade == "Estágio"
    assert aprovadas[0].relevancia >= 6
    assert aprovadas[0].motivo == "Estágio · área compatível"
    assert not descartes


def test_fontes_e_mercados_somente_brasil():
    assert set(PERFIS) == {"brasil"}
    assert LOCATIONS_LINKEDIN == ["Brasil"]
    assert LOCATIONS_LINKEDIN_REMOTO_APENAS == []
    assert not PERFIL_BR.eixo_secundario_ativo
    assert all("Intl" not in d.classe.__name__ for d in PERFIL_BR.definicao_scrapers)


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
    assert [linha[0] for linha in pendentes] == ["Estágio em Dados"]
    assert pendentes[0][3] >= 6
    assert len(db.obter_vagas_pendentes_digest("brasil")) == 4
    assert len(db.obter_vagas_pendentes_digest("internacional")) == 1
