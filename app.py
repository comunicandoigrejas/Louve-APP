import streamlit as st
from streamlit_gsheets import GSheetsConnection
from openai import OpenAI
import pandas as pd

# 1. CONFIGURAÇÃO DA PÁGINA E OCULTAR BOTÕES DO STREAMLIT
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

st.markdown("""
    <style>
    [data-testid="stHeader"], header, footer, .stAppDeployButton { display: none !important; }
    #MainMenu {visibility: hidden !important;}
    .block-container { padding-top: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. BRANDING NA SIDEBAR
st.sidebar.markdown("# 🛡️ Grupo Shekiná")
st.sidebar.markdown('''
    <a href="https://www.instagram.com/comunicandoigrejas/" target="_blank">
        <button style="width: 100%; background-color: #333333; color: white; border: 1px solid #555555; padding: 12px; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 20px;">
            🔧 By Comunicando Igrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

# 3. INICIALIZAÇÃO DE CONEXÕES (Compartilhadas via session_state se necessário)
try:
    if "openai_client" not in st.session_state:
        openai_key = st.secrets.get("OPENAI_API_KEY")
        st.session_state.openai_client = OpenAI(api_key=openai_key) if openai_key else None
    if "conn" not in st.session_state:
        st.session_state.conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    st.error("Erro nos Secrets: Verifique as chaves OpenAI e as credenciais do Google Sheets.")
    st.stop()

# 4. FUNÇÃO DE CARREGAMENTO DE USUÁRIOS PARA O LOGIN
def carregar_usuarios():
    try:
        df = st.session_state.conn.read(worksheet="Usuarios", ttl=0)
        df.columns = [c.strip() for c in df.columns]
        return df
    except: return pd.DataFrame(columns=["Nome", "WhatsApp", "Funcao", "Senha", "Status"])

# 5. LOGIN DO SISTEMA
if 'auth' not in st.session_state: st.session_state.auth = False
if 'user_funcao' not in st.session_state: st.session_state.user_funcao = "Integrante"
if 'user_nome' not in st.session_state: st.session_state.user_nome = ""

if not st.session_state.auth:
    st.title("🔑 Acesso ao Sistema")
    st.markdown("Seja bem-vindo! Insira sua senha para acessar o aplicativo do ministério.")
    acesso = st.text_input("Senha de acesso:", type="password")
    
    if st.button("Entrar no Sistema"):
        df_user = carregar_usuarios()
        usuario_valido = df_user[(df_user['Senha'] == acesso) & (df_user['Status'] == 'Ativo')]
        
        if not usuario_valido.empty:
            st.session_state.auth = True
            st.session_state.user_funcao = usuario_valido.iloc[0]['Funcao']
            st.session_state.user_nome = usuario_valido.iloc[0]['Nome']
            st.rerun()
        elif acesso in ["igreja2026", "shekina123"]:
            st.session_state.auth = True
            st.session_state.user_funcao = "Líder" if acesso == "shekina123" else "Integrante"
            st.session_state.user_nome = "Administrador"
            st.rerun()
        else: 
            st.error("Senha incorreta ou usuário inativo!")
    st.stop()

# --- GERENCIAMENTO DE PÁGINAS SEPARADAS (NATIVO DO STREAMLIT) ---
st.sidebar.write(f"👤 **Usuário:** {st.session_state.user_nome} ({st.session_state.user_funcao})")
st.sidebar.write("---")

# Definindo as páginas públicas
paginas_disponiveis = [
    st.Page("paginas/inicial.py", title="Página Inicial", icon="🏠"),
    st.Page("paginas/programacao.py", title="Programação", icon="📅"),
    st.Page("paginas/lista_musicas.py", title="Lista de Músicas", icon="🎵"),
    st.Page("paginas/cifras.py", title="Cifras", icon="📜"),
]

# Adicionando a página do Líder dinamicamente apenas se ele tiver a permissão
if st.session_state.user_funcao == "Líder":
    paginas_disponiveis.append(st.Page("paginas/lider.py", title="Painel do Líder", icon="🛠️"))

# Executa o sistema de navegação baseado nos arquivos criados
pg = st.navigation(paginas_disponiveis)
pg.run()
