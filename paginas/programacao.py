import streamlit as st
import pandas as pd

# Botão de retorno no topo
if st.button("⬅️ Voltar para a Página Inicial"):
    st.switch_page("paginas/inicial.py")

st.title("📅 Programação de Cultos e Ensaios")

conn = st.session_state.conn

try:
    hist = conn.read(worksheet="Cultos", ttl=0)
    hist.columns = [c.strip() for c in hist.columns]
except: hist = pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Tema_Culto", "Musicas"])

try:
    df_full = conn.read(worksheet="Louvores", ttl=0)
    df_full.columns = [c.strip() for c in df_full.columns]
except: df_full = pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento"])

if not hist.empty:
    op = (hist['Data_Culto'].astype(str) + " | " + hist['Nome_Culto']).tolist()[::-1]
    escolha = st.selectbox("Selecione o Culto/Ensaio para ver os louvores:", op)
    
    if escolha:
        dt, nm = escolha.split(" | ")
        reg = hist[(hist['Data_Culto'].astype(str) == dt) & (hist['Nome_Culto'] == nm)].iloc[0]
        
        st.warning(f"⛪ **{nm}** |  📅 **Data:** {dt}  |  📖 **Tema:** {reg['Tema_Culto']}")
        
        m_list = reg['Musicas'].split(", ")
        st.markdown("### 🎶 Lista de Louvores Escalados")
        df_escala = df_full[df_full['Musica'].isin(m_list)][["Musica", "Artista", "Tom", "Andamento"]]
        st.dataframe(df_escala, use_container_width=True, hide_index=True)
else:
    st.info("Nenhuma programação cadastrada no momento.")
