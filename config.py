import os

from dotenv import load_dotenv

load_dotenv()

# Estágios de qualquer área, nas cidades de São Paulo e Guarulhos.
CIDADES_ALVO = ["São Paulo", "Guarulhos"]
LOCALIDADES_BUSCA = ["São Paulo, SP, Brasil", "Guarulhos, SP, Brasil"]
# Cidade explícita no título que já apareceu com o card incorretamente marcado como São Paulo.
CIDADES_TITULO_CONFLITANTE = ["Várzea Paulista"]
MARCADORES_ESTAGIO = [
    "estágio", "estágios", "estagiário", "estagiária",
    "estagiários", "estagiárias", "intern", "interns", "internship", "internships",
]
TERMOS_BUSCA = [
    "estágio", "estagiário", "estagiária", "estágios", "estagiários", "estagiárias",
    "estagio", "estagiario", "estagiaria", "intern", "internship", "interns", "internships",
]
TERMOS_POR_CICLO = 10

INTERVALO_MINUTOS = int(os.getenv("INTERVALO_MINUTOS", 180))
LIMIAR_DIGEST_IMEDIATO = 7
DIGEST_HORA_UTC = 0  # 21h em Brasília.
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "jobs.db")
