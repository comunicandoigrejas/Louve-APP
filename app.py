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

# 3. INICIALIZAÇÃO DE CONEXÕES
try:
    if "openai_client" not in st.session_state:
        openai_key = st.secrets.get("OPENAI_API_KEY")
        st.session_state.openai_client = OpenAI(api_key=openai_key) if openai_key else None
    if "conn" not in st.session_state:
        st.session_state.conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    st.error("Erro nos Secrets: Verifique as chaves OpenAI e as credenciais do Google Sheets.")
    st.stop()

# 4. FUNÇÃO DE CARREGAMENTO DE USUÁRIOS
def carregar_usuarios():
    try:
        df = st.session_state.conn.read(worksheet="Usuarios", ttl=0)
        df.columns = [c.strip() for c in df.columns]
        return df
    except: 
        return pd.DataFrame(columns=["Nome", "WhatsApp", "Funcao", "Senha", "Status"])

# 5. LOGIN DO SISTEMA (AGORA COM USUÁRIO E SENHA)
if 'auth' not in st.session_state: st.session_state.auth = False
if 'user_funcao' not in st.session_state: st.session_state.user_funcao = "Integrante"
if 'user_nome' not in st.session_state: st.session_state.user_nome = ""

if not st.session_state.auth:
    st.title("🔑 Acesso ao Sistema")
    st.markdown("Seja bem-vindo, abençoado! Insira suas credenciais para acessar o painel.") [cite: 2025-08-14]
    
    # Campos de Entrada de Texto para o Login Duplo
    usuario_input = st.text_input("Nome de Usuário (Ex: Willian):")
    senha_input = st.text_input("Senha de acesso:", type="password")
    
    if st.button("Entrar no Sistema", use_container_width=True):
        if usuario_input and senha_input:
            df_user = carregar_usuarios()
            
            # Procura na planilha se existe um usuário com esse Nome, Senha e se está Ativo
            usuario_valido = df_user[
                (df_user['Nome'].str.lower().str.strip() == usuario_input.lower().str.strip()) & 
                (df_user['Senha'].astype(str) == senha_input.strip()) & 
                (df_user['Status'] == 'Ativo')
            ]
            
            if not usuario_valido.empty:
                st.session_state.auth = True
                # Pega a função exata salva na planilha (Líder ou Integrante)
                st.session_state.user_funcao = usuario_valido.iloc[0]['Funcao']
                st.session_state.user_nome = usuario_valido.iloc[0]['Nome']
                st.success(f"Paz do Senhor, irmão {st.session_state.user_nome}! Entrando...") [cite: 2025-08-14]
                st.rerun()
            else: 
                st.error("Usuário ou senha incorretos, ou cadastro inativo! Verifique com o seu Líder.")
        else:
            st.warning("Por favor, preencha o Usuário e a Senha.")
            
    st.stop()

# --- MENU DE NAVEGAÇÃO APÓS LOGIN BEM-SUCEDIDO ---
st.sidebar.write(f"👤 **Usuário:** {st.session_state.user_nome}")
st.sidebar.write(f"🛡️ **Perfil:** {st.session_state.user_funcao}")
st.sidebar.write("---")

# Definição das páginas visíveis a todos
paginas_disponiveis = [
    st.Page("paginas/inicial.py", title="Página Inicial", icon="🏠"),
    st.Page("paginas/programacao.py", title="Programação", icon="📅"),
    st.Page("paginas/lista_musicas.py", title="Lista de Músicas", icon="🎵"),
    st.Page("paginas/cifras.py", title="Cifras", icon="📜"),
]

# Separação: Se na planilha o usuário estiver como "Líder", ele ganha acesso à página restrita
if st.session_state.user_funcao == "Líder":
    paginas_disponiveis.append(st.Page("paginas/lider.py", title="Painel do Líder", icon="🛠️"))

# Inicia e roda a navegação do Streamlit
pg = st.navigation(paginas_disponiveis)
pg.run()
