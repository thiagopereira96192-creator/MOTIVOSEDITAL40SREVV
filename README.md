
# MVP — Motivos Edital 40/2024 (SREVV)

Este MVP entrega **dois requisitos obrigatórios**:
1) **Tabela descritiva** da base de dados usada (`pandas.DataFrame.describe()`).
2) **Um gráfico** a sua escolha (implementado como gráfico de **barras** interativo).

## Como rodar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

> O app tenta ler `./data/MOTIVOSEDITAL40SREVV.xlsx`. Se o arquivo não existir, ele permite **upload** de `.xlsx/.xls` ou `.csv`.

## Publicar no Streamlit Community Cloud
1. Suba para um repositório no GitHub os arquivos:
   - `app.py`
   - `requirements.txt`
   - `data/MOTIVOSEDITAL40SREVV.xlsx` (opcional; se não subir, faça upload no app)
2. Em https://share.streamlit.io → **New app** → selecione o repositório, a branch e `app.py`.
3. Clique em **Deploy**.
