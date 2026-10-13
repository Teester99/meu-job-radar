import os

from dotenv import load_dotenv

load_dotenv()

# Todo cargo precisa indicar estágio; a área é confirmada separadamente.
MARCADORES_ESTAGIO = [
    "estágio", "estágios", "estagiário", "estagiária",
    "estagiários", "estagiárias", "intern", "interns", "internship", "internships",
]
AREAS_ESTAGIO = [
    # Tecnologia, desenvolvimento e qualidade de software.
    "tecnologia", "tech", "ti", "technology", "information technology",
    "informática", "computação", "computer science", "sistemas", "systems",
    "software", "desenvolvimento", "developer", "development", "programação",
    "programmer", "backend", "back-end", "frontend", "front-end", "fullstack",
    "full-stack", "mobile", "web", "qa", "quality assurance", "testes", "testing",
    "automação", "automation", "devops", "cloud", "infraestrutura", "infrastructure",
    "redes", "networks", "segurança da informação", "cibersegurança", "cybersecurity",
    "suporte técnico", "suporte de ti", "produto digital", "product management",
    # Dados e ciências exatas.
    "dados", "data", "analytics", "análise de dados", "bi", "business intelligence",
    "inteligência artificial", "artificial intelligence", "machine learning",
    "exatas", "matemática", "mathematics", "estatística", "statistics",
    "física", "physics", "química", "chemistry", "engenharia", "engineering",
    "pesquisa operacional", "modelagem", "atuária", "actuarial",
    # Fintech e funções financeiras/quantitativas correlatas.
    "fintech", "banco digital", "digital bank", "mercado financeiro", "finanças",
    "finance", "financeiro", "financeira", "crédito", "credit", "risco", "risk",
    "pagamentos", "payments", "investimentos", "investments", "quantitativo",
    "quantitativa", "quantitative", "fraude", "fraud", "open finance", "open banking",
]

KEYWORDS_CARGO_FORTE = [
    "Estágio em Tecnologia", "Estágio em TI", "Estágio em Desenvolvimento",
    "Estágio em Dados", "Estágio em QA", "Estágio em Engenharia",
    "Estágio em Estatística", "Estágio em Matemática", "Estágio em Fintech",
    "Software Engineering Intern", "Data Science Intern", "QA Intern",
]
KEYWORDS_CARGO_AMBIGUO = MARCADORES_ESTAGIO
# Nome mantido para compatibilidade com o motor de filtro e score.
QUALIFICADORES_DADOS = AREAS_ESTAGIO
FERRAMENTAS_TITULO = [
    "Python", "SQL", "Power BI", "Excel", "Java", "JavaScript", "TypeScript",
    "React", "C#", "C++", "Selenium", "Cypress", "Playwright", "Appium", "AWS",
]
QUALIFICADORES_CARGO = MARCADORES_ESTAGIO
KEYWORDS = KEYWORDS_CARGO_FORTE + KEYWORDS_CARGO_AMBIGUO

# Termos genéricos capturam programas com área no título; os específicos
# ampliam a cobertura sem pesquisar cargos efetivos ou ferramentas soltas.
TERMOS_CARGO_EXTRA = [
    "estágio", "estagiário", "estagiária", "programa de estágio",
    "estágio tecnologia", "estágio ti", "estágio informática", "estágio computação",
    "estágio sistemas", "estágio desenvolvimento", "estágio software",
    "estágio backend", "estágio frontend", "estágio full stack", "estágio mobile",
    "estágio qa", "estágio testes", "estágio automação", "estágio devops",
    "estágio cloud", "estágio infraestrutura", "estágio redes",
    "estágio segurança da informação", "estágio suporte técnico",
    "estágio dados", "estágio análise de dados", "estágio ciência de dados",
    "estágio bi", "estágio inteligência artificial", "estágio machine learning",
    "estágio exatas", "estágio matemática", "estágio estatística", "estágio física",
    "estágio química", "estágio engenharia", "estágio atuária",
    "estágio fintech", "estágio banco digital", "estágio finanças",
    "estágio mercado financeiro", "estágio crédito", "estágio risco",
    "estágio pagamentos", "estágio investimentos", "estágio produto digital",
    "software engineering intern", "data science intern", "technology internship",
    "engineering internship", "fintech internship",
]
TERMOS_CARGO = list(dict.fromkeys(TERMOS_CARGO_EXTRA + [k.lower() for k in KEYWORDS]))
TERMOS_FERRAMENTA = ["estágio python", "estágio sql", "estágio power bi", "estágio java"]
TERMOS_BUSCA = list(dict.fromkeys(TERMOS_CARGO + TERMOS_FERRAMENTA))
TERMOS_POR_CICLO = 10

# A cobertura nacional é validada por país/UF em Job._avaliar.
# Estas cidades também reconhecem anúncios que omitem país e UF.
CIDADES = [
    "Remoto", "São Paulo", "Guarulhos", "Santo André", "São Bernardo do Campo",
    "São Caetano do Sul", "Osasco", "Barueri", "Mauá", "Diadema", "Campinas",
]
LOCATIONS_LINKEDIN = ["Brasil"]
LOCATIONS_LINKEDIN_REMOTO_APENAS = []
MERCADOS_REMOTO_ACEITOS = ["Brasil"]

INTERVALO_MINUTOS = int(os.getenv("INTERVALO_MINUTOS", 180))
LIMIAR_DIGEST_IMEDIATO = 7
DIGEST_HORA_UTC = 0  # 21h em Brasília.
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "jobs.db")
