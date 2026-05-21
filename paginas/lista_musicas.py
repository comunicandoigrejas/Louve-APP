import streamlit as st
import pandas as pd

st.title("🎵 Consulta de Repertório Geral")

conn = st.session_state.conn

try:
    df_l = conn.read(worksheet="Louvores", ttl=0)
    df_l.columns = [c.strip() for c in df_l.columns]
    df_l['Musica_Busca'] = df_l['Musica'].fillna('').astype(str).str.lower().str.strip()
except: df_l = pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento", "Categoria", "Musica_Busca"])

busca = st.text_input("🔍 Digite o nome da música ou artista:").lower()
df_f = df_l[df_l['Musica_Busca'].str.contains(busca)] if busca else df_l

st.dataframe(df_f[["Musica", "Artista", "Tom", "Andamento", "Categoria"]], use_container_width=True, hide_index=True)
