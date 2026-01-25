import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

# 2. CONEXÃO
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. CSS DE LIMPEZA
st.markdown("""
    <style>
    [data-testid="stHeader"], header, footer, .stAppDeployButton { display: none !important; }
    #MainMenu {visibility: hidden !important;}
    .block-container { padding-top: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE CARREGAMENTO COM DIAGNÓSTICO ---
def carregar_louvores():
    try:
        # ttl=0 força a leitura em tempo real
        df = conn.read(worksheet="Louvores", ttl=0)
        
        if df is not None and not df.empty:
            # Limpa nomes de colunas (remove espaços e acentos básicos para evitar erros)
            df.columns = [c.strip() for c in df.columns]
            
            # Cria a busca na memória
            if 'Musica' in df.columns:
                df['Musica_Busca'] = df['Musica'].fillna('').astype(str).str.lower().str.strip()
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao acessar aba Louvores: {e}")
        return pd.DataFrame()

# 4. SIDEBAR E BRANDING
st.sidebar.markdown("# 🛡️ Grupo Shekiná")
st.sidebar.markdown(f'''
    <a href="https://www.instagram.com/comunicandoigrejas/" target="_blank">
        <button style="width: 100%; border: 1px solid #555555; padding: 10px; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 20px;">
            🔧 By Comunicando Igrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

# 5. TELA DE LOGIN (Simplificada)
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔑 Login")
    senha = st.text_input("Senha da Equipe:", type="password")
    if st.button("Entrar"):
        if senha in ["igreja2026", "shekina123"]:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 6. INTERFACE PRINCIPAL
df_l = carregar_louvores()

# DIAGNÓSTICO PARA VOCÊ:
if df_l.empty:
    st.warning("⚠️ O sistema conectou, mas a lista de louvores está vazia ou as colunas não foram reconhecidas.")
    st.info("Verifique se a primeira linha da sua planilha tem: Musica, Artista, Tom, Andamento, Categoria")
    
    # Botão para criar uma linha de teste se estiver tudo vazio
    if st.button("📝 Criar Música de Teste na Planilha"):
        teste = pd.DataFrame([["Música de Teste", "Cantor Teste", "G", "Médio", "Adoração"]], 
                             columns=["Musica", "Artista", "Tom", "Andamento", "Categoria"])
        conn.update(worksheet="Louvores", data=teste)
        st.success("Música de teste enviada! Atualize a página.")
else:
    st.subheader(f"🎵 Catálogo Online ({len(df_l)} louvores encontrados)")
    
    busca = st.text_input("Pesquisar louvor:").lower()
    df_exibir = df_l.copy()
    
    if busca and 'Musica_Busca' in df_exibir.columns:
        df_exibir = df_exibir[df_exibir['Musica_Busca'].str.contains(busca)]
    
    # Mostra apenas as colunas que existem de fato
    cols_reais = [c for c in ["Musica", "Artista", "Tom", "Andamento", "Categoria"] if c in df_exibir.columns]
    st.dataframe(df_exibir[cols_reais], use_container_width=True, hide_index=True)
