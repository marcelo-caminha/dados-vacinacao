"""Constantes e configurações centrais do dashboard."""

from pathlib import Path

# ---------- CAMINHOS ----------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

CSV_PATH = DATA_DIR / "2022-perfil-das-pessoas-vacinadas-covid-19 (1).csv"
CSV_SEP = ";"
BANNER_IMAGE = ASSETS_DIR / "banner.png"

# ---------- APP ---------------------------------------------
APP_TITLE = "Dashboard de Vacinação"
SIDEBAR_IMAGE_URL = (
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ7tTknWGbEH5LjUvtNN259ayVFNi_VxfpE0ugsw9YZiA&s=10"
)

# ---------- DOMÍNIO -----------------------------------------
# fabricante exibido -> trecho que identifica a vacina em vacina_fabricante
# (agrupa as versões adulta, pediátrica e "baby" do mesmo fabricante)
FABRICANTES = {
    "CoronaVac": "CORONAVAC",
    "Pfizer": "PFIZER",
    "AstraZeneca": "ASTRAZENECA",
    "Janssen": "JANSSEN",
}

# rótulos exibidos para os sexos considerados nas análises
SEXO_LABELS = {"FEMININO": "Mulheres", "MASCULINO": "Homens"}
ORDEM_SEXO = list(SEXO_LABELS.values())

PERIODO_TRI = "1º trimestre (jan-mar)"
PERIODO_RESTO = "Resto do ano (abr-dez)"
ORDEM_PERIODO = [PERIODO_TRI, PERIODO_RESTO]

MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

# ---------- CORES -------------------------------------------
COR_PRIMARIA = "#0096D2"
CORES_SEXO = {"Mulheres": "#eb6834", "Homens": "#2a78d6"}
