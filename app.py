

import os
import pandas as pd
import streamlit as st
from pathlib import Path

# === Fonte automática da base (Google Sheets CSV) ===
GSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1EzkHvoDCjm2H_m6m-RYmvhk5TYbWPeIM/export?format=csv&gid=1431763071"
# (Opcional) priorize secrets/variável de ambiente no deploy:
GSHEET_CSV_URL = st.secrets.get("GSHEET_CSV_URL", os.getenv("GSHEET_CSV_URL", GSHEET_CSV_URL))

@st.cache_data(show_spinner="Baixando planilha (Google Sheets)…")
def _read_from_url(url: str) -> pd.DataFrame:
    # Se a planilha usa ; como separador, troque sep=',' para sep=';'
    # Se tiver problemas de acento, defina encoding='utf-8' (já é o padrão)
    return pd.read_csv(url)

def _clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    for c in df.columns:
        if df[c].dtype == "object":
            df[c] = df[c].astype(str).str.strip()
    return df

def try_load_default():
    # 1) Tenta o arquivo local (se existir)
    local_candidates = [
        Path(__file__).parent / "data" / "MOTIVOSEDITAL40SREVV.xlsx",
        Path.cwd() / "data" / "MOTIVOSEDITAL40SREVV.xlsx",
        Path("data") / "MOTIVOSEDITAL40SREVV.xlsx",
    ]
    for p in local_candidates:
        if p.exists():
            try:
                return _clean_columns(pd.read_excel(p, sheet_name=0))
            except Exception as e:
                st.warning(f"Falha ao ler arquivo local `{p}`: {e}")

    # 2) Tenta a URL do Google Sheets (CSV)
    if GSHEET_CSV_URL:
        try:
            df = _read_from_url(GSHEET_CSV_URL)
            st.success("✅ Base carregada automaticamente do Google Sheets (CSV).")
            return _clean_columns(df)
        except Exception as e:
            st.error(f"Não consegui ler o Google Sheets (CSV): {e}")

    # 3) Nada deu certo
    return None

