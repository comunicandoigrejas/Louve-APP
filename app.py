import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

# 2. CONEXÃO SIMPLIFICADA (TESTE)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Tentativa de leitura sem especificar worksheet (ele pega a primeira aba por padrão)
    # Isso ajuda a diagnosticar se o erro 400 é no link ou no nome da aba
    df_m = conn.read(ttl=0)
    
    st.sidebar.success("✅ Conexão estabelecida com a Nuvem!")
except Exception as e:
    st.error("❌ Erro de Conexão (400 - Bad Request)")
    st.info("Dica: Verifique se o link no Secrets termina em '/edit?usp=sharing' e se a planilha é pública.")
    st.exception(e)
    st.stop()

# 3. SIDEBAR E ASSINATURA
st.sidebar.markdown("# 🛡️ Grupo Shekiná")
st.sidebar.markdown(f'''
    <a href="https://www.instagram.com/comunicandoigrejas/" target="_blank">
        <button style="width: 100%; background-color: #333333; color: white; border: 1px solid #555555; padding: 10px; border-radius: 8px; cursor: pointer; font-weight: bold;">
            🔧 By Comunicando Igrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

# 4. TELA DE LOGIN
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔑 Acesso Restrito")
    senha = st.text_input("Senha da Equipe:", type="password")
    if st.button("Entrar"):
        if senha in ["igreja2026", "shekina123"]:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 5. EXIBIÇÃO DOS DADOS
st.subheader("🎵 Catálogo do Google Sheets")
if df_m is not None:
    st.dataframe(df_m, use_container_width=True, hide_index=True)
else:
    st.warning("Conectado, mas a planilha parece não ter dados.")
