import sqlite3

import pytest

from database import database as db
from job import Job


def _vaga(numero: int) -> Job:
    return Job(
        titulo=f"Estágio {numero}", empresa="Empresa", local="São Paulo, SP",
        link=f"https://example.com/vaga/{numero}", site="Exemplo",
    )


def test_reinicio_preserva_assinantes_e_reabilita_protecao(tmp_path, monkeypatch):
    caminho = tmp_path / "jobs.db"
    monkeypatch.setattr(db, "DB_PATH", str(caminho))
    db.iniciar_db()
    db.salvar_vaga(_vaga(1), perfil_chave="brasil")
    db.salvar_vaga(_vaga(2), perfil_chave="brasil")
    db.definir_assinatura_telegram("123", True)
    db.definir_metadado("telegram_update_offset", "42")

    assert db.reiniciar_historico_vagas() == 2
    db.iniciar_db()  # Banco vazio intencional não deve interromper o próximo ciclo.
    assert db.obter_assinantes_telegram() == ["123"]
    assert db.obter_metadado("telegram_update_offset") == "42"
    with sqlite3.connect(caminho) as conn:
        assert conn.execute("SELECT COUNT(*) FROM vagas_vistas").fetchone()[0] == 0

    db.salvar_vaga(_vaga(3), perfil_chave="brasil")
    assert db.obter_metadado(db._CHAVE_REINICIO_VAGAS) is None
    with sqlite3.connect(caminho) as conn:
        conn.execute("DELETE FROM vagas_vistas")
    with pytest.raises(db.BancoVazioSuspeito):
        db.iniciar_db()
