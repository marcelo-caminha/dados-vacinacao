"""Ponto de entrada do dashboard: configuração global e navegação entre páginas.

Execute com: streamlit run app.py
"""

import logging

import streamlit as st

from src import config

# set_page_config precisa ser o primeiro comando Streamlit da execução
st.set_page_config(page_title=config.APP_TITLE, page_icon="💉", layout="wide")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

with st.sidebar:
    st.write(config.APP_TITLE)
    st.image(config.SIDEBAR_IMAGE_URL)

pagina = st.navigation([
    st.Page("pages/visao_geral.py", title="Visão geral", icon=":material/dashboard:", default=True),
])
pagina.run()
