

# app.py
import os
from pathlib import Path
import pandas as pd
import streamlit as st

# ============ Config ============
st.set_page_config(page_title="MVP Indeferimentos", page_icon="🔍", layout="wide")

# === Fonte automática da base (Google Sheets CSV) ===
GSHEET_CSV_URL_DEFAULT = "https://docs.google.com/spreadsheets/d/1EzkHvoDCjm2H_m6m-RYmvhk5TYbWPeIM/export?format=csv&gid=1431763071"
GSHEET_CSV_URL = st.secrets.get("GSHEET_CSV_URL", os.getenv("GSHEET_CSV_URL", GSHEET_CSV_URL_DEFAULT))

LOCAL_CANDIDATES = [
    Path(__file__).parent / "data" / "MOTIVOSEDITAL40SREVV.xlsx",
    Path.cwd() / "data" / "MOTIVOSEDITAL40SREVV.xlsx",
    Path("data") / "MOTIVOSEDITAL40SREVV.xlsx",
]

# ============ Funções ============
@st.cache_data(show_spinner="Baixando planilha (Google Sheets)…")
def _read_from_url(url: str) -> pd.DataFrame:
    try:
        return pd.read_csv(url)
    except Exception:
        # fallback para planilhas com separador ';'
        return pd.read_csv(url, sep=';')

@st.cache_data(show_spinner="Lendo arquivo local…")
def _read_local_any(path: str, sheet=0) -> pd.DataFrame:
    p = Path(path)
    ext = p.suffix.lower()
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(p, sheet_name=sheet)
    if ext == ".csv":
        return pd.read_csv(p)
    raise ValueError(f"Extensão não suportada: {ext}")

def _clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    for c in df.columns:
        if df[c].dtype == "object":
            df[c] = df[c].astype(str).str.strip()
    return df

def try_load_default() -> pd.DataFrame | None:
    # 1) tenta arquivos locais
    for p in LOCAL_CANDIDATES:
        if p.exists():
            try:
                df = _read_local_any(str(p), sheet=0)
                st.success(f"✅ Base carregada do arquivo local: `{p}`")
                return _clean_columns(df)
            except Exception as e:
                st.warning(f"Falha ao ler `{p}`: {e}")

    # 2) tenta Google Sheets CSV
    if GSHEET_CSV_URL:
        try:
            df = _read_from_url(GSHEET_CSV_URL)
            st.success("✅ Base carregada automaticamente do Google Sheets (CSV).")
            return _clean_columns(df)
        except Exception as e:
            st.error(f"Não consegui ler o Google Sheets (CSV): {e}")

    return None

# ============ Carregamento (com persistência) ============
st.title("🔍 MVP — Indeferimentos (Edital 40/2024 SREVV)")
st.caption("Fonte padrão: Google Sheets CSV + upload opcional. Cache + session_state ativados.")
st.markdown(
    """
    Este painel apresenta uma visão dos dados referentes ao Edital 40/2024 da SREVV, 
    permitindo identificar padrões, categorias com maior incidência de indeferimentos e distribuição 
    das informações por variáveis como **Situação**, **Motivo**, **Disciplina** e **Município**.  
    """
)

# Inicializa sessão
if "df" not in st.session_state:
    st.session_state.df = try_load_default()

# Upload opcional
st.subheader("📂 Upload (opcional)")
up = st.file_uploader("Envie um .xlsx/.xls ou .csv", type=["xlsx","xls","csv"])
if up is not None:
    try:
        if up.name.lower().endswith((".xlsx",".xls")):
            df_up = pd.read_excel(up, sheet_name=0)
        else:
            # tenta ',' e fallback ';'
            try:
                df_up = pd.read_csv(up)
            except Exception:
                df_up = pd.read_csv(up, sep=';')
        st.session_state.df = _clean_columns(df_up)
        st.success(f"Arquivo '{up.name}' carregado e mantido na sessão.")
    except Exception as e:
        st.error(f"Não consegui ler o arquivo enviado: {e}")

df = st.session_state.df

# ============ Painel de Debug ============
with st.expander("🛠️ Debug (clique para abrir)"):
    st.write("**GSHEET_CSV_URL em uso:**")
    st.code(GSHEET_CSV_URL or "(vazio)")
    st.write("**Caminhos locais verificados:**")
    st.code("\n".join(map(str, LOCAL_CANDIDATES)))
    st.write("**CWD:**", str(Path.cwd()))
    try:
        files_here = [p.name for p in Path.cwd().iterdir() if p.is_file()]
        st.write("**Arquivos no diretório atual:**", ", ".join(files_here) if files_here else "(nenhum)")
    except Exception as e:
        st.write(f"(Não consegui listar arquivos: {e})")

# ============ Interface principal ============
if df is None:
    st.warning("Nenhuma base carregada ainda. Verifique a URL do Google Sheets ou envie um arquivo.")
    st.stop()

st.subheader("🔎 base de dados")
st.write(f"**Registros:** {len(df)} • **Colunas:** {', '.join(map(str, df.columns))}")
st.dataframe(df.head(30), use_container_width=True)

st.subheader("📈 📊 Dados gerais do Edital 40/2024 da SREVV")
try:
    desc = df.describe(include="all", datetime_is_numeric=True).transpose()
except TypeError:
    desc = df.describe(include="all").transpose()
st.dataframe(desc, use_container_width=True)

st.subheader("📊 Total de Eliminados e Reclassificados do Edital 40/2024 da SREVV")
st.markdown(
    """
    ℹ️ **Contexto da visualização:**  
    Este gráfico permite analisar a distribuição dos registros do Edital 40/2024 da SREVV com base em diferentes categorias da base de dados, 
    como **Situação**, **Motivo**, **Disciplina** ou **Município**.  
    """
)
cat_cols = [c for c in df.columns if df[c].dtype == "object" or str(df[c].dtype).startswith("category")]
with st.sidebar:
    st.header("⚙️ Selecione as opções desejadas para gerar o gráfico")
    x_col = st.selectbox("Categoria", options=cat_cols if cat_cols else list(df.columns), index=0, key="bar_x")
    group_by = st.selectbox("Opção", options=["(sem quebra)"] + cat_cols, index=0, key="bar_group")

if group_by != "(sem quebra)":
    grouped = df.groupby([x_col, group_by], dropna=False).size().reset_index(name="contagem")
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
