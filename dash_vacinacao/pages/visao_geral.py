"""Página principal: visão geral da vacinação por sexo e período."""

import datetime as dt

import pandas as pd
import streamlit as st

from src import charts, config, data


def filtro_periodo(df: pd.DataFrame) -> tuple[dt.date, dt.date]:
    """Slider de datas na sidebar, limitado ao intervalo presente nos dados."""
    data_minima, data_maxima = data.limites_de_data(df)
    with st.sidebar:
        inicio, fim = st.slider(
            "Selecione o período:",
            min_value=data_minima,
            max_value=data_maxima,
            value=(data_minima, data_maxima),
            format="DD/MM/YYYY",
        )
    return inicio, fim


def filtro_fabricante() -> list[str]:
    """Multiselect de fabricantes na sidebar; todos vêm selecionados por padrão."""
    with st.sidebar:
        return st.multiselect(
            "Fabricante da vacina:",
            options=list(config.FABRICANTES),
            default=list(config.FABRICANTES),
        )
    

def secao_doses_por_sexo(df: pd.DataFrame) -> None:
    st.subheader("Doses aplicadas por sexo")

    contagem = data.contagem_por_sexo(df)
    col1, col2 = st.columns(2)
    col1.metric("Feminino", f"{contagem['FEMININO']:,}")
    col2.metric("Masculino", f"{contagem['MASCULINO']:,}")

    st.plotly_chart(charts.grafico_doses_por_sexo(contagem), width="stretch")

    st.write("**Distribuição percentual**")
    st.dataframe(data.percentual_por_sexo(df))


def secao_analise_temporal(df: pd.DataFrame) -> None:
    st.header("Análise temporal da vacinação")

    dados = data.preparar_por_sexo(df)
    if dados.empty:
        st.warning("Não há registros válidos para esta análise.")
        return

    distribuicao = data.distribuicao_por_periodo(dados)
    total_mulheres = int((dados["sexo"] == "Mulheres").sum())
    pct_mulheres = distribuicao.loc["Mulheres", config.PERIODO_TRI]
    pct_homens = distribuicao.loc["Homens", config.PERIODO_TRI]

    col1, col2, col3 = st.columns(3)
    col1.metric("Doses/registros em mulheres", f"{total_mulheres:,}")
    col2.metric("Mulheres no 1º trimestre", f"{pct_mulheres:.1f}%")
    col3.metric("Homens no 1º trimestre", f"{pct_homens:.1f}%")

    st.subheader("Evolução mensal por sexo")
    st.plotly_chart(charts.grafico_evolucao_mensal(data.doses_mensais(dados)), width="stretch")

    st.subheader("Participação das doses no 1º trimestre")
    st.plotly_chart(charts.grafico_primeiro_trimestre(distribuicao), width="stretch")

    st.subheader("Distribuição percentual por período")
    st.dataframe(
        distribuicao.rename(columns={
            config.PERIODO_TRI: "1º trimestre (%)",
            config.PERIODO_RESTO: "Abril a dezembro (%)",
        }),
        width="stretch",
    )

    st.subheader("Resumo dos resultados")
    if total_mulheres == 0:
        st.info("Não há registros de mulheres para comparar.")
    elif pct_mulheres > 50:
        st.success(
            f"Mais de 50% dos registros de mulheres ocorreram no 1º trimestre ({pct_mulheres:.1f}%)."
        )
    else:
        st.info(
            f"{pct_mulheres:.1f}% dos registros de mulheres ocorreram no 1º trimestre; "
            "portanto, não representam a maioria."
        )
def secao_amostra(df: pd.DataFrame) -> None:
    with st.expander("Inspeção das 5 primeiras linhas"):
        st.dataframe(df.head(5), hide_index=True)

# ---------- PÁGINA -------------------------------------------
st.title("Bem-vindo ao Dashboard de Vacinação")
st.image(str(config.BANNER_IMAGE))

df = data.carregar_dados()
inicio, fim = filtro_periodo(df)
fabricantes = filtro_fabricante()
if not fabricantes:
    st.info("Selecione ao menos um fabricante na barra lateral.")
    st.stop()

df_filtrado = data.filtrar_por_fabricante(data.filtrar_por_periodo(df, inicio, fim), fabricantes)

st.caption(
    f"Período: {inicio:%d/%m/%Y} a {fim:%d/%m/%Y} · Fabricantes: {', '.join(fabricantes)} · "
    f"{len(df_filtrado):,} registros"
)

secao_amostra(df_filtrado)
secao_doses_por_sexo(df_filtrado)
secao_analise_temporal(df_filtrado)
