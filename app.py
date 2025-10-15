
# -*- coding: utf-8 -*-
"""
MVP • Estatística descritiva + Gráfico (MOTIVOSEDITAL40SREVV.xlsx)
- Obrigatório 1: Tabela descritiva da base usada (pandas describe)
- Obrigatório 2: Um gráfico (barras) a sua escolha
"""
from pathlib import Path
import pandas as pd
import streamlit as st


import os
import requests

DATA_PATH = "data/MOTIVOSEDITAL40SREVV.xlsx"
URL = "COLE_AQUI_O_LINK_DIRETO_DO_ARQUIVO"

def baixar_base():
    # Só cria a pasta se ela não existir como diretório
    if not os.path.isdir("data"):
        os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_PATH):
        r = requests.get(URL)
        with open(DATA_PATH, "wb") as f:
            f.write(r.content)

baixar_base()


st.set_page_config(page_title="MVP SREVV 40/2024 • Motivos", page_icon="📊", layout="wide")
st.title("📊 MVP — Motivos Edital 40/2024 (SREVV)")
st.caption("Base padrão: data/MOTIVOSEDITAL40SREVV.xlsx • Se não existir, faça upload abaixo.")

DATA_PATH = Path(__file__).parent / "data" / "MOTIVOSEDITAL40SREVV.xlsx"

@st.cache_data
def _read_any(file, sheet=0):
    name = getattr(file, "name", None)
    if isinstance(file, (str, Path)):
        p = Path(file)
        if p.suffix.lower() in [".xlsx", ".xls"]:
            return pd.read_excel(p, sheet_name=sheet)
        elif p.suffix.lower() == ".csv":
            return pd.read_csv(p)
    # UploadedFile (buffer)
    if name and name.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(file, sheet_name=sheet)
    else:
        return pd.read_csv(file)

def try_load_default():
    try:
        if DATA_PATH.exists():
            df = _read_any(DATA_PATH, sheet=0)
            df.columns = [c.strip() for c in df.columns]
            for c in df.columns:
                if df[c].dtype == "object":
                    df[c] = df[c].astype(str).str.strip()
            st.success(f"Base carregada automaticamente de: {DATA_PATH.name}")
            return df
    except Exception as e:
        st.warning(f"Falha ao carregar o arquivo padrão: {e}")
    return None

with st.sidebar:
    st.header("ℹ️ Informações")
    st.write("Arquivo esperado: `data/MOTIVOSEDITAL40SREVV.xlsx`")
    st.write("Caso não exista, use o upload abaixo.")

df = try_load_default()

st.subheader("📂 Upload (opcional)")
up = st.file_uploader("Envie um .xlsx/.xls ou .csv", type=["xlsx","xls","csv"])
if df is None and up is not None:
    try:
        df = _read_any(up, sheet=0)
        st.success("Arquivo enviado carregado com sucesso.")
    except Exception as e:
        st.error(f"Não consegui ler o arquivo enviado: {e}")

if df is None:
    st.info("Nenhuma base carregada ainda. Coloque o arquivo em `data/MOTIVOSEDITAL40SREVV.xlsx` ou faça upload acima.")
    st.stop()

# ----------------- Prévia -----------------
st.subheader("🔎 Prévia da base")
st.write(f"**Registros:** {len(df)}  •  **Colunas:** {', '.join(df.columns)}")
st.dataframe(df.head(30), use_container_width=True)

# ----------------- Tabela Descritiva (Obrigatório 1) -----------------
st.subheader("📈 Tabela descritiva da base (pandas `describe`) — OBRIGATÓRIO")
try:
    desc = df.describe(include="all", datetime_is_numeric=True).transpose()
except TypeError:
    desc = df.describe(include="all").transpose()
st.dataframe(desc, use_container_width=True)

# ----------------- Gráfico (Obrigatório 2) -----------------
st.subheader("📊 Gráfico de barras — OBRIGATÓRIO")

# Identificar colunas categóricas
cat_cols = [c for c in df.columns if df[c].dtype == "object" or str(df[c].dtype).startswith("category")]

with st.sidebar:
    st.header("⚙️ Configurar gráfico")
    x_col = st.selectbox("Eixo X (categórica)", options=cat_cols if cat_cols else df.columns, index=0, key="bar_x")
    group_by = st.selectbox("Quebrar por (opcional)", options=["(sem quebra)"] + cat_cols, index=0, key="bar_group")

# Agrupar por contagem (base é categórica)
if group_by != "(sem quebra)":
    grouped = df.groupby([x_col, group_by], dropna=False).size().reset_index(name="contagem")
    # pivot para barras agrupadas
    pivot = grouped.pivot(index=x_col, columns=group_by, values="contagem").fillna(0)
    st.bar_chart(pivot, use_container_width=True)
    with st.expander("Ver dados agregados"):
        st.dataframe(grouped, use_container_width=True)
else:
    grouped = df.groupby(x_col, dropna=False).size().reset_index(name="contagem")
    st.bar_chart(grouped.set_index(x_col)["contagem"], use_container_width=True)
    with st.expander("Ver dados agregados"):
        st.dataframe(grouped, use_container_width=True)

st.markdown("---")
st.caption("Este MVP cumpre os requisitos: (1) tabela descritiva com pandas.describe(); (2) um gráfico de barras configurável.")
