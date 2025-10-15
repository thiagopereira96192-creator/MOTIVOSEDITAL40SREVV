

from pathlib import Path
from io import BytesIO
import os
import pandas as pd
import streamlit as st

# (A) OPÇÃO AUTOMÁTICA: cole aqui o CSV público do Google Sheets
# Exemplo: https://docs.google.com/spreadsheets/d/<ID>/export?format=csv&gid=<GID>
GSHEET_CSV_URL = st.secrets.get("GSHEET_CSV_URL", os.getenv("GSHEET_CSV_URL", ""))

# (B) POSSÍVEIS LOCAIS DO ARQUIVO NO DISCO
CANDIDATE_PATHS = [
    Path(__file__).parent / "data" / "MOTIVOSEDITAL40SREVV.xlsx",
    Path.cwd() / "data" / "MOTIVOSEDITAL40SREVV.xlsx",
    Path("data") / "MOTIVOSEDITAL40SREVV.xlsx",
]

@st.cache_data(show_spinner="Lendo arquivo local…")
def _read_local_any(path: str, sheet=0):
    p = Path(path)
    suf = p.suffix.lower()
    if suf in (".xlsx", ".xls"):
        return pd.read_excel(p, sheet_name=sheet)
    elif suf == ".csv":
        return pd.read_csv(p)
    raise ValueError(f"Extensão não suportada: {suf}")

@st.cache_data(show_spinner="Baixando planilha da web…")
def _read_from_url(url: str):
    # Se for Google Sheets CSV, read_csv direto; outros links CSV também funcionam
    return pd.read_csv(url)

def _clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    for c in df.columns:
        if df[c].dtype == "object":
            df[c] = df[c].astype(str).str.strip()
    return df

def try_load_default():
    # 1) Tenta arquivo local em vários caminhos
    for p in CANDIDATE_PATHS:
        if p.exists():
            try:
                df = _read_local_any(str(p), sheet=0)
                st.info(f"✅ Base carregada do arquivo local: `{p}`")
                return _clean_columns(df)
            except Exception as e:
                st.warning(f"Tentei ler `{p.name}` e falhei: {e}")

    # 2) Tenta URL (Google Sheets CSV) se informada
    if GSHEET_CSV_URL:
        try:
            df = _read_from_url(GSHEET_CSV_URL)
            st.info("✅ Base carregada automaticamente da URL (GSHEET_CSV_URL).")
            return _clean_columns(df)
        except Exception as e:
            st.warning(f"URL informada, mas falhou ao ler: {e}")

    # 3) Nada deu certo
    st.caption("Debug: nenhum caminho local encontrado. CWD: " + str(Path.cwd()))
    st.caption("Debug: arquivos no diretório atual: " + ", ".join([p.name for p in Path.cwd().iterdir() if p.is_file()]))
    return None
