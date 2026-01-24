import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

# 2. CONEXÃO COM GOOGLE SHEETS (CORRIGIDA)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # ATENÇÃO: Mudamos para "Louvores" para evitar o erro do 'á'
    df_m = conn.read(worksheet="Louvores", ttl="1m")
    
    # Criar coluna de busca na memória (para evitar o KeyError anterior)
    if not df_m.empty:
        df_m['Musica_Busca'] = df_m['Musica'].fillna('').astype(str).str.lower().str.strip()
        
    st.sidebar.success("✅ Conectado à Nuvem!")
except Exception as e:
    st.error("❌ Erro de Codificação ou Conexão!")
    st.write("Dica: Renomeie a aba da sua planilha para 'Louvores' (sem acento).")
    st.stop()

# 3. CSS DE LIMPEZA (OPCIONAL NESTA FASE DE TESTE)
st.markdown("""
    <style>
    [data-testid="stHeader"], header, footer, .stAppDeployButton { display: none !important; }
    #MainMenu {visibility: hidden !important;}
    </style>
    """, unsafe_allow_html=True)

# 4. SIDEBAR E ASSINATURA
st.sidebar.markdown("# 🛡️ Grupo Shekiná")
st.sidebar.markdown(f'''
    <a href="https://www.instagram.com/comunicandoigrejas/" target="_blank">
        <button style="width: 100%; background-color: #333333; color: white; border: 1px solid #555555; padding: 10px; border-radius: 8px; cursor: pointer; font-weight: bold;">
            🔧 By Comunicando Igrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

# 5. TELA DE LOGIN
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔑 Acesso ao Sistema")
    senha = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        if senha in ["igreja2026", "shekina123"]:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 6. EXIBIÇÃO DE TESTE
st.subheader("🎵 Catálogo de Louvores (Google Sheets)")
if df_m.empty:
    st.warning("A planilha está conectada, mas parece vazia.")
else:
    st.dataframe(df_m[['Musica', 'Artista', 'Tom', 'Andamento', 'Categoria']], use_container_width=True, hide_index=True)
