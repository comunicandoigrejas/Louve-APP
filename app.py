import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

# 2. CSS DE LIMPEZA E MARCA (By Comunicando Igrejas)
st.markdown("""
    <style>
    [data-testid="stHeader"], header, footer, .stAppDeployButton { display: none !important; }
    #MainMenu {visibility: hidden !important;}
    .block-container { padding-top: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. CONEXÃO COM GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_louvores():
    try:
        df = conn.read(worksheet="Louvores", ttl=0)
        if df is not None and not df.empty:
            # SOLUÇÃO DO ERRO image_ed4870.png: 
            # Criamos a coluna de busca na memória, independente da planilha
            df['Musica_Busca'] = df['Musica'].fillna('').astype(str).str.lower().str.strip()
        return df
    except:
        return pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento", "Categoria", "Musica_Busca"])

def carregar_cultos():
    try:
        return conn.read(worksheet="Cultos", ttl=0)
    except:
        return pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Musicas"])

# 4. SIDEBAR
st.sidebar.markdown("# 🛡️ Grupo Shekiná")
st.sidebar.markdown(f'''
    <a href="https://www.instagram.com/comunicandoigrejas/" target="_blank">
        <button style="width: 100%; background-color: #333333; color: white; border: 1px solid #555555; padding: 10px; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 20px;">
            🔧 By Comunicando Igrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

# 5. SEGURANÇA (Senhas)
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔑 Acesso Restrito")
    senha = st.text_input("Senha da Equipe:", type="password")
    if st.button("Entrar"):
        if senha in ["igreja2026", "shekina123"]:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 6. INTERFACE
perfil = st.sidebar.radio("Nível:", ["Integrantes", "Líder"])

if perfil == "Líder":
    chave = st.sidebar.text_input("Chave Mestre:", type="password")
    if chave == "shekina123":
        t1, t2, t3, t4 = st.tabs(["🎸 Repertório", "➕ Cadastrar", "🗑️ Excluir", "📜 Histórico"])
        df_l = carregar_louvores()
        
        with t1:
            st.subheader("Montar Repertório")
            busca = st.text_input("Pesquisar louvor no catálogo:").lower()
            
            # Filtro usando a coluna criada na memória
            df_f = df_l.copy()
            if busca:
                df_f = df_f[df_f['Musica_Busca'].str.contains(busca)]
            
            # Exibe apenas as colunas úteis para o usuário
            colunas_ver = ["Musica", "Artista", "Tom", "Andamento", "Categoria"]
            sel = st.dataframe(df_f[colunas_ver], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
            
            if 'cart' not in st.session_state: st.session_state.cart = []
            if sel.selection.rows:
                selecionadas = df_f.iloc[sel.selection.rows]['Musica'].tolist()
                for s in selecionadas:
                    if s not in st.session_state.cart: st.session_state.cart.append(s)
            
            st.write("---")
            nome_c = st.text_input("Título do Culto:")
            data_c = st.date_input("Data do Culto:", date.today())
            final = st.multiselect("Setlist Final:", options=sorted(df_l['Musica'].tolist()), default=[m for m in st.session_state.cart if m in df_l['Musica'].tolist()])
            st.session_state.cart = final

            if st.button("💾 PUBLICAR NO GOOGLE SHEETS"):
                if nome_c and final:
                    df_c_atual = carregar_cultos()
                    novo_c = pd.DataFrame([[str(data_c), nome_c, ", ".join(final)]], columns=["Data_Culto", "Nome_Culto", "Musicas"])
                    conn.update(worksheet="Cultos", data=pd.concat([df_c_atual, novo_c], ignore_index=True))
                    st.success("✅ Publicado!")
                    st.session_state.cart = []

        with t2:
            st.subheader("Novo Cadastro")
            with st.form("cad_l"):
                m, a, t = st.text_input("Música:"), st.text_input("Artista:"), st.text_input("Tom:")
                and_v = st.select_slider("Andamento:", options=["Lento", "Médio", "Rápido"], value="Médio")
                cat_v = st.multiselect("Categorias:", ["Adoração", "Júbilo", "Avivamento", "Antigo", "Congregacional"])
                if st.form_submit_button("Salvar na Nuvem"):
                    nova = pd.DataFrame([[m, a, t, and_v, ", ".join(cat_v)]], columns=["Musica", "Artista", "Tom", "Andamento", "Categoria"])
                    df_up = pd.concat([df_l.drop(columns=['Musica_Busca'], errors='ignore'), nova], ignore_index=True)
                    conn.update(worksheet="Louvores", data=df_up)
                    st.success("Música cadastrada!")

        with t4:
            st.subheader("Histórico")
            st.dataframe(carregar_cultos(), use_container_width=True, hide_index=True)
else:
    # VISÃO INTEGRANTES
    st.header("📖 Repertório Oficial")
    hist = carregar_cultos()
    if hist.empty: st.info("Nada publicado.")
    else:
        op = (hist['Data_Culto'].astype(str) + " | " + hist['Nome_Culto']).tolist()[::-1]
        escolha = st.selectbox("Selecione o Culto:", op)
        if escolha:
            dt, nm = escolha.split(" | ")
            reg = hist[(hist['Data_Culto'].astype(str) == dt) & (hist['Nome_Culto'] == nm)].iloc[0]
            m_list = reg['Musicas'].split(", ")
            df_full = carregar_louvores()
            st.table(df_full[df_full['Musica'].isin(m_list)][["Musica", "Artista", "Tom", "Andamento", "Categoria"]])
