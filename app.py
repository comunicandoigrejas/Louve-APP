import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date
import urllib.parse

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

# 2. CSS DE LIMPEZA E BRANDING (BY COMUNICANDO IGREJAS)
st.markdown("""
    <style>
    [data-testid="stHeader"], header, footer, .stAppDeployButton { display: none !important; }
    #MainMenu {visibility: hidden !important;}
    div[class^="viewerBadge"], [data-testid="stStatusWidget"] { display: none !important; }
    .block-container { padding-top: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO E FUNÇÕES DE DADOS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_louvores():
    df = conn.read(worksheet="Louvores", ttl=0)
    if df is not None and not df.empty:
        df['Busca'] = df['Musica'].fillna('').astype(str).str.lower().str.strip()
    return df

def carregar_cultos():
    return conn.read(worksheet="Cultos", ttl=0)

# --- CONFIGURAÇÕES DE SEGURANÇA ---
SENHA_GERAL = "igreja2026"
SENHA_LIDER = "shekina123"
LISTA_CATEGORIAS = ["Adoração", "Quebrantamento", "Congregacional", "Avivamento", "Espontâneo", "Júbilo", "Profético", "Antigo", "Clássico"]
LISTA_ANDAMENTO = ["Lento", "Médio", "Rápido"]

# 3. SIDEBAR
st.sidebar.markdown("# 🛡️ Grupo Shekiná")
st.sidebar.markdown(f'''
    <a href="https://www.instagram.com/comunicandoigrejas/" target="_blank">
        <button style="width: 100%; background-color: #333333; color: white; border: 1px solid #555555; padding: 10px; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 20px;">
            🔧 By Comunicando Igrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

# 4. LOGIN
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔑 Acesso Restrito")
    s = st.text_input("Senha da Equipe:", type="password")
    if st.button("Entrar"):
        if s in [SENHA_GERAL, SENHA_LIDER]:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 5. INTERFACE PRINCIPAL
perfil = st.sidebar.radio("Nível:", ["Integrantes", "Líder"])

if perfil == "Líder" and st.sidebar.text_input("Chave Mestre:", type="password") == SENHA_LIDER:
    df_l = carregar_louvores()
    t1, t2, t3, t4 = st.tabs(["🎸 Repertório", "➕ Cadastrar", "🗑️ Excluir", "📜 Histórico"])

    with t1:
        st.subheader("Montar Repertório")
        c1, c2 = st.columns(2)
        with c1: busca = st.text_input("Filtrar Nome:").lower()
        with c2: f_cat = st.selectbox("Estilo:", ["Todos"] + LISTA_CATEGORIAS)
        
        df_f = df_l.copy()
        if f_cat != "Todos": df_f = df_f[df_f['Categoria'].str.contains(f_cat, na=False)]
        if busca: df_f = df_f[df_f['Busca'].str.contains(busca)]
        
        sel = st.dataframe(df_f[['Musica', 'Artista', 'Tom', 'Andamento', 'Categoria']], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
        
        if 'set' not in st.session_state: st.session_state.set = []
        if sel.selection.rows:
            selec = df_f.iloc[sel.selection.rows]['Musica'].tolist()
            for sm in selec:
                if sm not in st.session_state.set: st.session_state.set.append(sm)
        
        st.write("---")
        n_c = st.text_input("Título do Culto:")
        dt_c = st.date_input("Data do Culto:", date.today())
        final = st.multiselect("Setlist Final:", options=sorted(df_l['Musica'].tolist()), default=[m for m in st.session_state.set if m in df_l['Musica'].tolist()])
        
        if st.button("💾 PUBLICAR NO GOOGLE SHEETS"):
            df_c_atual = carregar_cultos()
            novo_c = pd.DataFrame([[str(dt_c), n_c, ", ".join(final)]], columns=["Data_Culto", "Nome_Culto", "Musicas"])
            df_atualizado = pd.concat([df_c_atual, novo_c], ignore_index=True)
            conn.update(worksheet="Cultos", data=df_atualizado)
            st.success("✅ Publicado com sucesso!")
            st.session_state.set = []

    with t2:
        st.subheader("Novo Cadastro")
        with st.form("cad_form"):
            m, a, t = st.text_input("Música:"), st.text_input("Artista:"), st.text_input("Tom:")
            and_v = st.select_slider("Andamento:", options=LISTA_ANDAMENTO, value="Médio")
            cat_v = st.multiselect("Categorias:", LISTA_CATEGORIAS)
            if st.form_submit_button("Salvar na Nuvem"):
                nova_m = pd.DataFrame([[m, a, t, and_v, ", ".join(cat_v)]], columns=["Musica", "Artista", "Tom", "Andamento", "Categoria"])
                df_up = pd.concat([df_l.drop(columns=['Busca']), nova_m], ignore_index=True)
                conn.update(worksheet="Louvores", data=df_up)
                st.success("✅ Música salva no Google Sheets!")

    with t3:
        st.subheader("Excluir Louvor")
        m_ex = st.selectbox("Escolha:", [""] + sorted(df_l['Musica'].tolist()))
        if m_ex and st.button("Confirmar Exclusão"):
            df_del = df_l[df_l['Musica'] != m_ex].drop(columns=['Busca'])
            conn.update(worksheet="Louvores", data=df_del)
            st.rerun()

    with t4:
        st.subheader("Histórico de Cultos")
        h = carregar_cultos()
        if h is not None and not h.empty:
            if st.button("Limpar Histórico"):
                conn.update(worksheet="Cultos", data=pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Musicas"]))
                st.rerun()
            st.dataframe(h, use_container_width=True, hide_index=True)

else:
    st.header("📖 Repertório Oficial")
    hist = carregar_cultos()
    if hist is None or hist.empty:
        st.info("Nenhum repertório publicado.")
    else:
        opcoes = (hist['Data_Culto'].astype(str) + " | " + hist['Nome_Culto']).tolist()[::-1]
        escolha = st.selectbox("Selecione o Culto:", opcoes)
        if escolha:
            dt_s, nm_s = escolha.split(" | ")
            st.info(f"📅 **Data:** {dt_s} | ⛪ **Culto:** {nm_s}")
            reg = hist[(hist['Data_Culto'].astype(str) == dt_s) & (hist['Nome_Culto'] == nm_s)].iloc[0]
            m_lista = reg['Musicas'].split(", ")
            df_full = carregar_louvores()
            st.table(df_full[df_full['Musica'].isin(m_lista)][['Musica', 'Artista', 'Tom', 'Andamento', 'Categoria']])
