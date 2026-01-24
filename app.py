import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

# 2. CSS DE LIMPEZA (Sutil para não esconder erros)
st.markdown("""
    <style>
    [data-testid="stHeader"], header, footer, .stAppDeployButton { display: none !important; }
    #MainMenu {visibility: hidden !important;}
    </style>
    """, unsafe_allow_html=True)

# 3. TENTATIVA DE CONEXÃO REFORÇADA
try:
    # Criando a conexão
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Tentando ler a aba "Louvores"
    # Adicionamos o parâmental 'ttl=0' para garantir que ele pegue os dados MAIS RECENTES agora
    df_m = conn.read(worksheet="Louvores", ttl=0)
    
    st.sidebar.success("✅ Conectado ao Google Sheets!")
except Exception as e:
    st.error("❌ Erro Crítico de Conexão")
    st.warning("Verifique se o nome da aba é 'Louvores' e se o link nos Secrets está correto.")
    # Mostra o erro técnico real para diagnóstico
    st.exception(e) 
    st.stop()

# 4. SIDEBAR E BRANDING
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
    st.title("🔑 Acesso Restrito")
    senha = st.text_input("Digite a Senha da Equipe:", type="password")
    if st.button("Entrar no Sistema"):
        if senha in ["igreja2026", "shekina123"]:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 6. CONTEÚDO PRINCIPAL (Exibição dos Louvores da Planilha)
st.subheader("🎵 Catálogo Atualizado (Nuvem)")

if df_m is not None and not df_m.empty:
    # Cria coluna de busca na memória
    df_m['Busca'] = df_m['Musica'].fillna('').astype(str).str.lower()
    
    busca = st.text_input("Pesquisar louvor no catálogo:").lower()
    
    if busca:
        df_filtrado = df_m[df_m['Busca'].str.contains(busca)]
    else:
        df_filtrado = df_m

    # Exibe a tabela sem a coluna de busca técnica
    colunas_visiveis = [c for c in df_filtrado.columns if c != 'Busca']
    st.dataframe(df_filtrado[colunas_visiveis], use_container_width=True, hide_index=True)
else:
    st.info("A planilha está conectada, mas não encontramos dados. Adicione louvores no Google Sheets!")
