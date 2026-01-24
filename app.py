import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

# 2. CONEXÃO COM GOOGLE SHEETS
# No seu arquivo 'secrets.toml' ou no painel do Streamlit, você deve colocar:
# [connections.gsheets]
# spreadsheet = "https://drive.google.com/file/d/1AQGBesvRWlZJOGkNjKRbWRGczuTYIos7/view?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Erro ao conectar com o Google Sheets. Verifique os Secrets.")
    st.stop()

# --- FUNÇÕES DE DADOS (AGORA VIA NUVEM) ---
def carregar_louvores():
    # Lê a aba de Louvores (Página 1)
    return conn.read(worksheet="Página1", ttl="1m")

def carregar_cultos():
    # Lê a aba de Cultos (Página 2)
    return conn.read(worksheet="Cultos", ttl="1m")

# 3. CSS E VISUAL (BY COMUNICANDO IGREJAS)
st.markdown("""
    <style>
    [data-testid="stHeader"], header, footer, .stAppDeployButton { display: none !important; }
    #MainMenu {visibility: hidden !important;}
    .block-container { padding-top: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. SIDEBAR E BRANDING
st.sidebar.markdown("# 🛡️ Grupo Shekiná")
st.sidebar.markdown(f'''
    <a href="https://www.instagram.com/comunicandoigrejas/" target="_blank">
        <button style="width: 100%; background-color: #333333; color: white; border: 1px solid #555555; padding: 10px; border-radius: 8px; cursor: pointer; font-weight: bold;">
            🔧 By Comunicando Igrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

# --- LOGIN E NÍVEIS DE ACESSO (Omitido para brevidade, manter igual às versões anteriores) ---

# 5. EXEMPLO DE COMO CADASTRAR NO GOOGLE SHEETS
def salvar_novo_louvor(nome, artista, tom, andamento, categoria):
    df_atual = carregar_louvores()
    nova_linha = pd.DataFrame([[nome, artista, tom, andamento, categoria]], 
                              columns=["Musica", "Artista", "Tom", "Andamento", "Categoria"])
    df_final = pd.concat([df_atual, nova_linha], ignore_index=True)
    
    # ATUALIZA A PLANILHA NA NUVEM
    conn.update(worksheet="Página1", data=df_final)
    st.success("Música salva diretamente no Google Sheets!")

# ... O restante da interface de tabs segue a mesma lógica, 
# mas trocando o 'to_csv' por 'conn.update'
