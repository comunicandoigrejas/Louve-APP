import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# 1. CONFIGURAÇÃO DA PÁGINA (DEVE SER SEMPRE O PRIMEIRO COMANDO)
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

# 2. CONEXÃO COM GOOGLE SHEETS
# O Streamlit vai procurar nos 'Secrets' pela seção [connections.gsheets]
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Teste de leitura imediata para ver se a conexão funciona
    # Se a tua aba não se chamar "Página1", muda o nome abaixo:
    df_teste = conn.read(worksheet="Página1", ttl="1m")
    st.sidebar.success("✅ Conectado ao Google Sheets!")
except Exception as e:
    st.error("❌ Erro de Conexão!")
    st.write(f"Detalhes do erro: {e}")
    st.info("Verifica se o teu requirements.txt tem: st-gsheets-connection")
    st.stop()

# 3. CSS SUAVE (Não esconde erros agora)
st.markdown("""
    <style>
    .stAppDeployButton { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. SIDEBAR E BRANDING
st.sidebar.markdown("# 🛡️ Grupo Shekiná")
st.sidebar.markdown('''
    <a href="https://www.instagram.com/comunicandoigrejas/" target="_blank">
        <button style="width: 100%; background-color: #333333; color: white; border: 1px solid #555555; padding: 10px; border-radius: 8px; cursor: pointer; font-weight: bold;">
            🔧 By Comunicando Igrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

# 5. TELA DE LOGIN
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ Acesso ao Sistema")
    senha = st.text_input("Senha da Equipe:", type="password")
    if st.button("Entrar"):
        if senha in ["igreja2026", "shekina123"]:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# Se chegou aqui, o login funcionou
st.write("### 🎉 Bem-vindo ao sistema conectado à Nuvem!")
st.write("Dados carregados da planilha:")
st.dataframe(df_teste)
