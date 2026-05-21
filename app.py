import streamlit as st
from streamlit_gsheets import GSheetsConnection
from openai import OpenAI
import pandas as pd

# 1. CONFIGURAÇÃO DA PÁGINA E IDENTIDADE VISUAL
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

st.markdown("""
    <style>
    /* Esconde elementos nativos do Streamlit */
    [data-testid="stHeader"], header, footer, .stAppDeployButton { display: none !important; }
    #MainMenu {visibility: hidden !important;}
    .block-container { padding-top: 1rem !important; }
    
    /* Customização de Cores Globais e Inputs */
    .stButton>button {
        background-color: #4a148c; /* Roxo Escuro */
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ff6d00; /* Laranja Vibrante no Hover */
        color: white;
    }
    
    /* Alertas e mensagens customizadas */
    .stSuccess, div[data-testid="stNotification"] {
        background-color: #1b5e20 !important; /* Verde Pentecostal */
        color: white !important;
    }
    .stWarning {
        background-color: #ffd600 !important; /* Amarelo */
        color: black !important;
    }
    .stError {
        background-color: #b71c1c !important; /* Vermelho padrão para erros */
        color: white !important;
    }
    
    /* Customização da Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0d47a1; /* Azul Real / Marinho */
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. BRANDING NA SIDEBAR
st.sidebar.markdown("# 🛡️ Grupo Shekiná")
st.sidebar.markdown('''
    <a href="https://www.instagram.com/comunicandoigrejas/" target="_blank">
        <button style="width: 100%; background-color: #ff6d00; color: white; border: none; padding: 12px; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 20px;">
            🔧 By Comunicando Igrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

# 3. INICIALIZAÇÃO DE CONEXÕES
if "openai_client" not in st.session_state:
    try:
        openai_key = st.secrets.get("OPENAI_API_KEY")
        st.session_state.openai_client = OpenAI(api_key=openai_key) if openai_key else None
    except:
        st.session_state.openai_client = None

if "conn" not in st.session_state:
    try:
        st.session_state.conn = st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error("Erro ao conectar com o Google Sheets. Verifique os Secrets.")
        st.stop()

# 4. FUNÇÃO DE CARREGAMENTO DE USUÁRIOS
def carregar_usuarios():
    try:
        df = st.session_state.conn.read(worksheet="Usuarios", ttl=0)
        df.columns = [c.strip() for c in df.columns]
        return df
    except: 
        return pd.DataFrame(columns=["Nome", "WhatsApp", "Funcao", "Senha", "Status"])

# 5. GERENCIAMENTO DE ESTADO DO LOGIN
if 'auth' not in st.session_state: 
    st.session_state.auth = False
if 'user_funcao' not in st.session_state: 
    st.session_state.user_funcao = "Integrante"
if 'user_nome' not in st.session_state: 
    st.session_state.user_nome = ""

# --- TELA DE LOGIN ---
if not st.session_state.auth:
    st.title("🔑 Acesso ao Sistema")
    st.markdown("Seja bem-vindo, abençoado! Insira suas credenciais para acessar o painel.")
    
    usuario_input = st.text_input("Nome de Usuário (Ex: Willian):")
    senha_input = st.text_input("Senha de acesso:", type="password")
    
    if st.button("Entrar no Sistema", use_container_width=True):
        if usuario_input and senha_input:
            df_user = carregar_usuarios()
            
            if not df_user.empty:
                # Padronização de colunas para busca segura
                df_user['Nome_Limpo'] = df_user['Nome'].astype(str).str.lower().str.strip()
                df_user['Senha_Limpa'] = df_user['Senha'].astype(str).str.strip()
                df_user['Status_Limpo'] = df_user['Status'].astype(str).str.lower().str.strip()
                
                usuario_valido = df_user[
                    (df_user['Nome_Limpo'] == usuario_input.lower().strip()) & 
                    (df_user['Senha_Limpa'] == senha_input.strip()) & 
                    (df_user['Status_Limpo'] == 'ativo')
                ]
                
                if not usuario_valido.empty:
                    st.session_state.auth = True
                    st.session_state.user_funcao = str(usuario_valido.iloc[0]['Funcao']).strip()
                    st.session_state.user_nome = str(usuario_valido.iloc[0]['Nome']).strip()
                    st.success(f"Paz do Senhor, irmão {st.session_state.user_nome}! Entrando...")
                    st.rerun()
                else: 
                    st.error("Usuário ou senha incorretos, ou cadastro inativo! Verifique com o seu Líder.")
            else:
                st.error("Não foi possível ler a tabela de usuários. Verifique as abas da planilha.")
        else:
            st.warning("Por favor, preencha o Usuário e a Senha.")
    
    # Interrompe a execução aqui para não mostrar o menu sem logar
    st.stop()

# --- MENU DE NAVEGAÇÃO (SÓ EXECUTA SE AUTH FOR TRUE) ---
st.sidebar.write(f"👤 **Usuário:** {st.session_state.user_nome}")
st.sidebar.write(f"🛡️ **Perfil:** {st.session_state.user_funcao}")
st.sidebar.write("---")

# Definição das páginas padrão para todos
paginas_disponiveis = [
    st.Page("paginas/inicial.py", title="Página Inicial", icon="🏠"),
    st.Page("paginas/programacao.py", title="Programação", icon="📅"),
    st.Page("paginas/lista_musicas.py", title="Lista de Músicas", icon="🎵"),
    st.Page("paginas/cifras.py", title="Cifras", icon="📜"),
]

# Liberação blindada do Painel do Líder
funcao_teste = st.session_state.user_funcao.lower().strip()
if funcao_teste in ["líder", "lider"]:
    paginas_disponiveis.append(st.Page("paginas/lider.py", title="Painel do Líder", icon="🛠️"))

# Executa o sistema de navegação multi-páginas do Streamlit
pg = st.navigation(paginas_disponiveis)
pg.run()
