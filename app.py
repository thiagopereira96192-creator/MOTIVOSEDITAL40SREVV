

from pathlib import Path
from io import BytesIO
import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).parent / "data" / "MOTIVOSEDITAL40SREVV.xlsx"

# ---------- Funções de leitura com cache estável ----------
@st.cache_data(show_spinner="Lendo arquivo do disco…")
def _read_from_path(path_str: str, sheet=0):
    p = Path(path_str)
    suf = p.suffix.lower()
    if suf in (".xlsx", ".xls"):
        return pd.read_excel(p, sheet_name=sheet)
    elif suf == ".csv":
        return pd.read_csv(p)
    else:
        raise ValueError(f"Extensão não suportada: {suf}")

@st.cache_data(show_spinner="Lendo arquivo enviado…")
def _read_from_bytes(data: bytes, ext: str, sheet=0):
    ext = ext.lower()
    bio = BytesIO(data)
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(bio, sheet_name=sheet)
    elif ext == ".csv":
        return pd.read_csv(bio)
    else:
        raise ValueError(f"Extensão não suportada: {ext}")

def _clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    for c in df.columns:
        if df[c].dtype == "object":
            df[c] = df[c].astype(str).str.strip()
    return df

def try_load_default():
    try:
        if DATA_PATH.exists():
            df = _read_from_path(str(DATA_PATH), sheet=0)
            df = _clean_columns(df)
            st.success(f"Base carregada automaticamente de: {DATA_PATH.name}")
            return df
    except Exception as e:
        st.warning(f"Falha ao carregar o arquivo padrão: {e}")
    return None

# ============== Persistência na sessão ==============
if "df" not in st.session_state:
    st.session_state.df = try_load_default()

st.subheader("📂 Upload (opcional)")
up = st.file_uploader("Envie um .xlsx/.xls ou .csv", type=["xlsx","xls","csv"])

# Se o usuário enviar arquivo, lê uma única vez e guarda em session_state
if up is not None:
    try:
        file_bytes = up.getvalue()  # bytes estáveis para cache
        file_ext = Path(up.name).suffix
        df_up = _read_from_bytes(file_bytes, file_ext, sheet=0)
        st.session_state.df = _clean_columns(df_up)
        st.success(f"Arquivo '{up.name}' carregado e mantido na sessão.")
    except Exception as e:
        st.error(f"Não consegui ler o arquivo enviado: {e}")

df = st.session_state.df

if df is None:
    st.info("Nenhuma base carregada ainda. Coloque o arquivo em `data/MOTIVOSEDITAL40SREVV.xlsx` ou faça upload acima.")
    st.stop()

# ----------------- Prévia -----------------
st.subheader("🔎 Prévia da base")
st.write(f"**Registros:** {len(df)}  •  **Colunas:** {', '.join(map(str, df.columns))}")
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
    x_col = st.selectbox("Eixo X (categórica)", options=cat_cols if cat_cols else list(df.columns), index=0, key="bar_x")
    group_by = st.selectbox("Quebrar por (opcional)", options=["(sem quebra)"] + cat_cols, index=0, key="bar_group")

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
