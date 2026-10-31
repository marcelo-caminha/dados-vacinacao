"""Construção das figuras Plotly usadas no dashboard."""

import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure

from src import config


def grafico_doses_por_sexo(contagem: pd.Series) -> Figure:
    """Barras com o total de registros por sexo."""
    return px.bar(
        x=contagem.index,
        y=contagem.values,
        title="Doses aplicadas por sexo",
        labels={"x": "", "y": "Quantidade de registros"},
        color_discrete_sequence=[config.COR_PRIMARIA],
    )


def grafico_evolucao_mensal(mensal: pd.DataFrame) -> Figure:
    """Linhas com as doses por mês e sexo, destacando o 1º trimestre."""
    fig = px.line(
        mensal,
        x="mes",
        y="doses",
        color="sexo",
        category_orders={"sexo": config.ORDEM_SEXO},
        color_discrete_map=config.CORES_SEXO,
        markers=True,
        title="Doses por mês e sexo",
        labels={"mes": "", "doses": "Quantidade de registros", "sexo": ""},
    )
    fig.add_vrect(x0=1, x1=3, fillcolor="gray", opacity=0.12, line_width=0)
    fig.update_xaxes(tickvals=list(range(1, 13)), ticktext=config.MESES)
    fig.update_yaxes(rangemode="tozero")
    fig.update_layout(hovermode="x unified", legend_title_text="")
    return fig


def grafico_primeiro_trimestre(distribuicao: pd.DataFrame) -> Figure:
    """Barras com o percentual de registros de cada sexo no 1º trimestre."""
    coluna = config.PERIODO_TRI
    fig = px.bar(
        distribuicao.reset_index(),
        x="sexo",
        y=coluna,
        color="sexo",
        color_discrete_map=config.CORES_SEXO,
        text=coluna,
        title="% dos registros no 1º trimestre",
        labels={"sexo": "", coluna: "Percentual (%)"},
    )
    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        width=0.5,
        hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
    )
    fig.add_hline(y=50, line_dash="dash", line_color="gray", line_width=1)
    fig.update_layout(showlegend=False, yaxis_range=[0, 100])
    return fig
