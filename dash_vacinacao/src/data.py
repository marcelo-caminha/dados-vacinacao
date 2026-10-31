"""Leitura, preparação e agregação dos dados de vacinação.

As funções de agregação são puras (não chamam a API do Streamlit),
o que facilita testá-las e reaproveitá-las em outras páginas.
"""

import datetime as dt
import io
import logging
import os
from pathlib import Path
from typing import BinaryIO

import pandas as pd
import streamlit as st

from src import config

logger = logging.getLogger(__name__)


# ---------- LEITURA ------------------------------------------
class _LeitorLimitado(io.RawIOBase):
    """Expõe apenas os primeiros `limite` bytes de um arquivo binário."""

    def __init__(self, arquivo: BinaryIO, limite: int):
        self._arquivo = arquivo
        self._restante = limite

    def readable(self) -> bool:
        return True

    def readinto(self, buffer) -> int:
        n = min(len(buffer), self._restante)
        if n <= 0:
            return 0
        lidos = self._arquivo.readinto(memoryview(buffer)[:n])
        self._restante -= lidos
        return lidos


def _bytes_ate_ultima_linha_completa(arquivo: BinaryIO, bloco: int = 64 * 1024) -> int:
    """Tamanho do arquivo descartando uma eventual última linha sem quebra de linha."""
    tamanho = arquivo.seek(0, os.SEEK_END)
    inicio = max(tamanho - bloco, 0)
    arquivo.seek(inicio)
    final = arquivo.read()
    arquivo.seek(0)
    if final.endswith(b"\n"):
        return tamanho
    return inicio + final.rfind(b"\n") + 1


def _fabricante(vacinas: pd.Series) -> pd.Series:
    """Nome curto do fabricante (config.FABRICANTES) de cada vacina; NaN se não reconhecido."""
    mapa = {
        vacina: nome
        for vacina in vacinas.cat.categories
        for nome, trecho in config.FABRICANTES.items()
        if trecho in str(vacina).upper()
    }
    return vacinas.map(mapa).astype(pd.CategoricalDtype(list(config.FABRICANTES)))


# cache_resource compartilha o mesmo objeto entre execuções sem copiá-lo
# (cache_data desserializa uma cópia de ~1M de linhas a cada rerun);
# por isso o dataframe retornado deve ser tratado como somente leitura
def carregar_csv_original(caminho: Path = config.CSV_PATH) -> pd.DataFrame:
    """Lê o CSV original, sem conversões, ignorando a última linha se estiver truncada."""
    with open(caminho, "rb") as arquivo:
        # o arquivo baixado está truncado: a leitura é feita em streaming
        # e para antes da última linha se ela estiver incompleta
        limite = _bytes_ate_ultima_linha_completa(arquivo)
        leitor = io.BufferedReader(_LeitorLimitado(arquivo, limite))
        # as colunas têm poucos valores distintos: ler como category reduz
        # bastante o pico de memória em relação a strings (object)
        return pd.read_csv(
            leitor, sep=config.CSV_SEP, encoding="utf-8", dtype="category",
            usecols=config.COLUNAS_USADAS,
        )


@st.cache_resource(show_spinner="Carregando dados de vacinação...")
def carregar_dados() -> pd.DataFrame:
    """Lê o dataset e converte as colunas usadas no dashboard para os tipos corretos.

    Usa a versão reduzida (versionada no GitHub, usada no deploy) quando ela
    existe; senão, lê o CSV original.
    """
    if config.CSV_REDUZIDO_PATH.exists():
        df = pd.read_csv(
            config.CSV_REDUZIDO_PATH, sep=config.CSV_SEP, encoding="utf-8", dtype="category"
        )
    else:
        df = carregar_csv_original()

    df["data_vacinacao"] = pd.to_datetime(
        df["data_vacinacao"].astype(str).str[:10], errors="coerce"
    )
    df["idade"] = pd.to_numeric(df["idade"].astype(str), errors="coerce")
    df["fabricante"] = _fabricante(df["vacina_fabricante"])

    logger.info("Dataset carregado com sucesso: %d linhas.", len(df))
    return df


# ---------- FILTROS ------------------------------------------
def limites_de_data(df: pd.DataFrame) -> tuple[dt.date, dt.date]:
    """Retorna a menor e a maior data de vacinação válidas do dataset."""
    datas = df["data_vacinacao"].dropna()
    return datas.min().date(), datas.max().date()


def filtrar_por_periodo(df: pd.DataFrame, inicio: dt.date, fim: dt.date) -> pd.DataFrame:
    """Mantém apenas os registros vacinados entre `inicio` e `fim` (inclusive)."""
    datas = df["data_vacinacao"].dt.date
    return df[datas.between(inicio, fim)]


def filtrar_por_fabricante(df: pd.DataFrame, fabricantes: list[str]) -> pd.DataFrame:
    """Mantém apenas os registros dos fabricantes informados (nomes de config.FABRICANTES)."""
    return df[df["fabricante"].isin(fabricantes)]


def preparar_por_sexo(df: pd.DataFrame) -> pd.DataFrame:
    """Mantém mulheres e homens e adiciona as colunas de mês e período do ano."""
    dados = df.loc[df["sexo"].isin(config.SEXO_LABELS), ["sexo", "data_vacinacao"]].copy()
    dados["sexo"] = dados["sexo"].astype(str).map(config.SEXO_LABELS)
    dados["mes"] = dados["data_vacinacao"].dt.month
    dados["periodo"] = dados["mes"].le(3).map({True: config.PERIODO_TRI, False: config.PERIODO_RESTO})
    return dados


# ---------- AGREGAÇÕES ---------------------------------------
def contagem_por_sexo(df: pd.DataFrame) -> pd.Series:
    """Quantidade de registros por sexo, sempre com FEMININO e MASCULINO."""
    return df["sexo"].value_counts().reindex(list(config.SEXO_LABELS), fill_value=0)


def percentual_por_sexo(df: pd.DataFrame) -> pd.Series:
    """Distribuição percentual de todos os valores da coluna sexo."""
    return df["sexo"].value_counts(normalize=True).mul(100).round(1)


def distribuicao_por_periodo(dados: pd.DataFrame) -> pd.DataFrame:
    """Percentual de registros de cada sexo no 1º trimestre e no resto do ano."""
    tabela = pd.crosstab(dados["sexo"], dados["periodo"], normalize="index") * 100
    return (
        tabela.reindex(index=config.ORDEM_SEXO, columns=config.ORDEM_PERIODO)
        .fillna(0.0)
        .round(1)
    )


def doses_mensais(dados: pd.DataFrame) -> pd.DataFrame:
    """Quantidade de registros por mês e sexo, incluindo meses sem doses."""
    todos_meses = pd.MultiIndex.from_product(
        [range(1, 13), config.ORDEM_SEXO], names=["mes", "sexo"]
    )
    return (
        dados.groupby(["mes", "sexo"])
        .size()
        .reindex(todos_meses, fill_value=0)
        .reset_index(name="doses")
    )
