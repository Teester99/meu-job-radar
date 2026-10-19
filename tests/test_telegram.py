"""Feedback e inscrição no Telegram, com a API simulada e banco temporário."""

import pytest
import requests

from notifier.telegram import _parsear_callback_data, _teclado_feedback
from database import database as db
from notifier import telegram

_ID_EXEMPLO = "d41d8cd98f00b204e9800998ecf8427e"  # md5 de exemplo, 32 chars

CASOS_PARSE_CALLBACK = [
    ("positivo-formato-valido", f"fb|1|{_ID_EXEMPLO}", (_ID_EXEMPLO, "positivo")),
    ("negativo-formato-valido", f"fb|0|{_ID_EXEMPLO}", (_ID_EXEMPLO, "negativo")),
    # Botão de confirmação (substitui o teclado original depois de
    # registrado) não deve ser reprocessado como voto novo.
    ("botao-confirmacao-nao-e-voto", "fb|ok|-", None),
    # Direção fora de 1/0.
    ("direcao-invalida", f"fb|2|{_ID_EXEMPLO}", None),
    # Prefixo errado (callback_data de outro bot/projeto, teoricamente).
    ("prefixo-errado", f"xx|1|{_ID_EXEMPLO}", None),
    # Formato sem as 3 partes esperadas.
    ("sem_partes_suficientes", "fb|1", None),
    ("partes_demais", f"fb|1|{_ID_EXEMPLO}|extra", None),
    ("string_vazia", "", None),
]


@pytest.mark.parametrize(
    "nome,data,esperado",
    CASOS_PARSE_CALLBACK,
    ids=[c[0] for c in CASOS_PARSE_CALLBACK],
)
def test_parsear_callback_data(nome, data, esperado):
    assert _parsear_callback_data(data) == esperado


def test_teclado_feedback_estrutura():
    teclado = _teclado_feedback(_ID_EXEMPLO)
    linha = teclado["inline_keyboard"][0]
    assert len(linha) == 2
    assert linha[0]["callback_data"] == f"fb|1|{_ID_EXEMPLO}"
    assert linha[1]["callback_data"] == f"fb|0|{_ID_EXEMPLO}"


def test_teclado_feedback_callback_data_dentro_do_limite_do_telegram():
    # Limite real da API: callback_data <= 64 bytes.
    teclado = _teclado_feedback(_ID_EXEMPLO)
    for botao in teclado["inline_keyboard"][0]:
        assert len(botao["callback_data"].encode("utf-8")) <= 64


def test_ida_e_volta_teclado_para_parser():
    # O que _teclado_feedback gera, _parsear_callback_data tem que
    # entender de volta — as duas funções são as duas pontas do mesmo
    # contrato (callback_data), então uma mudar sem a outra é exatamente o
    # tipo de bug que só aparece em produção sem esse teste.
    teclado = _teclado_feedback(_ID_EXEMPLO)
    botao_positivo, botao_negativo = teclado["inline_keyboard"][0]

    assert _parsear_callback_data(botao_positivo["callback_data"]) == (_ID_EXEMPLO, "positivo")
    assert _parsear_callback_data(botao_negativo["callback_data"]) == (_ID_EXEMPLO, "negativo")


def test_inscricao_e_cancelamento_recebem_apenas_vagas_futuras(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "jobs.db"))
    monkeypatch.setattr(telegram, "TELEGRAM_BOT_TOKEN", "token-de-teste")
    monkeypatch.setattr(telegram, "TELEGRAM_CHAT_ID", "100")
    db.iniciar_db()
    enviados = []
    monkeypatch.setattr(telegram, "_enviar_para_chat", lambda chat, texto, markup=None: enviados.append((chat, texto, markup)) or True)

    updates = [
        {"update_id": 1, "message": {"chat": {"id": 200, "type": "private"}, "text": "/start"}},
        {"update_id": 2, "message": {"chat": {"id": -300, "type": "supergroup"}, "text": "/start"}},
    ]
    def get_updates(_metodo, payload):
        offset = int(payload.get("offset", 0))
        return {"ok": True, "result": [u for u in updates if u["update_id"] >= offset]}

    monkeypatch.setattr(telegram, "_chamar_api_telegram", get_updates)
    telegram.processar_feedback_pendente()
    assert db.obter_assinantes_telegram() == ["200"]
    assert db.obter_metadado("telegram_update_offset") == "2"
    enviados.clear()
    assert telegram.enviar_mensagem("vaga", reply_markup={"inline_keyboard": []})
    assert [chat for chat, _, _ in enviados] == ["100", "200"]
    assert enviados[0][2] == {"inline_keyboard": []}
    assert enviados[1][2] is None

    updates.append({"update_id": 3, "message": {"chat": {"id": 200, "type": "private"}, "text": "/stop"}})
    telegram.processar_feedback_pendente()
    assert db.obter_assinantes_telegram() == []
    enviados.clear()
    assert telegram.enviar_mensagem("outra vaga")
    assert [chat for chat, _, _ in enviados] == ["100"]


def test_falha_de_um_assinante_nao_pula_os_outros(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "jobs.db"))
    monkeypatch.setattr(telegram, "TELEGRAM_BOT_TOKEN", "token-de-teste")
    monkeypatch.setattr(telegram, "TELEGRAM_CHAT_ID", "100")
    db.iniciar_db()
    db.definir_assinatura_telegram("200", True)
    db.definir_assinatura_telegram("300", True)
    enviados = []
    def enviar(chat, _texto, _markup=None):
        enviados.append(chat)
        return chat != "200"

    monkeypatch.setattr(telegram, "_enviar_para_chat", enviar)
    assert not telegram.enviar_mensagem("vaga")
    assert enviados == ["100", "200", "300"]


def test_chat_que_bloqueou_o_bot_sai_da_lista(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "jobs.db"))
    monkeypatch.setattr(telegram, "TELEGRAM_BOT_TOKEN", "token-de-teste")
    monkeypatch.setattr(telegram, "TELEGRAM_CHAT_ID", "100")
    db.iniciar_db()
    db.definir_assinatura_telegram("200", True)

    def post(_url, data, timeout):
        resposta = requests.Response()
        resposta.status_code = 403 if data["chat_id"] == "200" else 200
        resposta.reason = "Forbidden" if resposta.status_code == 403 else "OK"
        return resposta

    monkeypatch.setattr(telegram._sessao_telegram, "post", post)
    assert telegram.enviar_mensagem("vaga")
    assert db.obter_assinantes_telegram() == []
