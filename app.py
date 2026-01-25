import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

# 2. CSS DE LIMPEZA E BRANDING
st.markdown("""
    <style>
    [data-testid="stHeader"], header, footer, .stAppDeployButton { display: none !important; }
    #MainMenu {visibility: hidden !important;}
    div[class^="viewerBadge"], [data-testid="stStatusWidget"] { display: none !important; }
    .block-container { padding-top: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. CONEXÃO COM GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÕES DE DADOS (LENDO E ESCREVENDO NA NUVEM) ---
def carregar_louvores():
    try:
        df = conn.read(worksheet="Louvores", ttl=0)
        if df is not None and not df.empty:
            df.columns = [c.strip() for c in df.columns]
            # Cria busca na memória para evitar KeyError
            df['Musica_Busca'] = df['Musica'].fillna('').astype(str).str.lower().str.strip()
        return df
    except:
        return pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento", "Categoria", "Musica_Busca"])

def carregar_cultos():
    try:
        df = conn.read(worksheet="Cultos", ttl=0)
        if df is not None and not df.empty:
            df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Musicas"])

# --- CONFIGURAÇÕES ---
LISTA_CATEGORIAS = ["Adoração", "Quebrantamento", "Congregacional", "Avivamento", "Espontâneo", "Júbilo", "Profético", "Antigo", "Clássico"]
LISTA_ANDAMENTO = ["Lento", "Médio", "Rápido"]

# 4. SIDEBAR E ASSINATURA
st.sidebar.markdown("# 🛡️ Grupo Shekiná")
st.sidebar.markdown(f'''
    <a href="https://www.instagram.com/comunicandoigrejas/" target="_blank">
        <button style="width: 100%; background-color: #333333; color: white; border: 1px solid #555555; padding: 10px; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 20px;">
            🔧 By Comunicando Igrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

# 5. LOGIN
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔑 Acesso ao Sistema")
    s = st.text_input("Senha da Equipe:", type="password")
    if st.button("Entrar"):
        if s in ["igreja2026", "shekina123"]:
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
            st.subheader("Montar Repertório do Culto")
            c1, c2 = st.columns(2)
            with c1: busca = st.text_input("Nome:").lower()
            with c2: f_cat = st.selectbox("Estilo:", ["Todos"] + LISTA_CATEGORIAS)
            
            df_f = df_l.copy()
            if f_cat != "Todos": df_f = df_f[df_f['Categoria'].str.contains(f_cat, na=False)]
            if busca: df_f = df_f[df_f['Musica_Busca'].str.contains(busca)]
            
            sel = st.dataframe(df_f[['Musica', 'Artista', 'Tom', 'Andamento', 'Categoria']], 
                               use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
            
            if 'cart' not in st.session_state: st.session_state.cart = []
            if sel.selection.rows:
                selec = df_f.iloc[sel.selection.rows]['Musica'].tolist()
                for sm in selec:
                    if sm not in st.session_state.cart: st.session_state.cart.append(sm)
            
            st.write("---")
            n_c = st.text_input("Título do Culto:")
            dt_c = st.date_input("Data:", date.today())
            final = st.multiselect("Setlist Final:", options=sorted(df_l['Musica'].tolist()), 
                                   default=[m for m in st.session_state.cart if m in df_l['Musica'].tolist()])
            st.session_state.cart = final
            
            if st.button("💾 PUBLICAR NO GOOGLE SHEETS"):
                if n_c and final:
                    df_c_atual = carregar_cultos()
                    novo_c = pd.DataFrame([[str(dt_c), n_c, ", ".join(final)]], columns=["Data_Culto", "Nome_Culto", "Musicas"])
                    conn.update(worksheet="Cultos", data=pd.concat([df_c_atual, novo_c], ignore_index=True))
                    st.success("✅ Publicado com sucesso!")
                    st.session_state.cart = []

        with t2:
            st.subheader("Cadastrar Novo Louvor")
            with st.form("cad_l", clear_on_submit=True):
                m, a, t = st.text_input("Música:"), st.text_input("Artista:"), st.text_input("Tom:")
                and_v = st.select_slider("Andamento:", options=LISTA_ANDAMENTO, value="Médio")
                cat_v = st.multiselect("Categorias:", LISTA_CATEGORIAS)
                if st.form_submit_button("✅ Salvar na Nuvem"):
                    if m and a:
                        nova_m = pd.DataFrame([[m, a, t, and_v, ", ".join(cat_v)]], columns=["Musica", "Artista", "Tom", "Andamento", "Categoria"])
                        # Remove a coluna de busca antes de enviar para a planilha
                        df_up = pd.concat([df_l.drop(columns=['Musica_Busca'], errors='ignore'), nova_m], ignore_index=True)
                        conn.update(worksheet="Louvores", data=df_up)
                        st.success(f"'{m}' cadastrado com sucesso!")
                    else: st.warning("Preencha Nome e Artista.")

        with t3:
            st.subheader("🗑️ Excluir do Catálogo")
            m_ex = st.selectbox("Escolha a música:", [""] + sorted(df_l['Musica'].tolist()))
            if m_ex and st.button("Confirmar Exclusão Definitiva"):
                df_del = df_l[df_l['Musica'] != m_ex].drop(columns=['Musica_Busca'], errors='ignore')
                conn.update(worksheet="Louvores", data=df_del)
                st.success(f"'{m_ex}' removido!")
                st.rerun()

        with t4:
            st.subheader("📜 Histórico de Cultos")
            h = carregar_cultos()
            if not h.empty:
                if st.button("Limpar Histórico"):
                    conn.update(worksheet="Cultos", data=pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Musicas"]))
                    st.rerun()
                for i, r in h.sort_values(by="Data_Culto", ascending=False).iterrows():
                    with st.expander(f"📅 {r['Data_Culto']} - {r['Nome_Culto']}"):
                        st.write(f"🎶 {r['Musicas']}")

else:
    st.header("📖 Repertório Oficial")
    hist = carregar_cultos()
    if hist.empty: st.info("Nenhum repertório publicado.")
    else:
        op = (hist['Data_Culto'].astype(str) + " | " + hist['Nome_Culto']).tolist()[::-1]
        escolha = st.selectbox("Selecione o Culto:", op)
        if escolha:
            dt, nm = escolha.split(" | ")
            st.info(f"📅 **Data:** {dt} | ⛪ **Culto:** {nm}")
            reg = hist[(hist['Data_Culto'].astype(str) == dt) & (hist['Nome_Culto'] == nm)].iloc[0]
            m_list = reg['Musicas'].split(", ")
            df_full = carregar_louvores()
            st.table(df_full[df_full['Musica'].isin(m_list)][["Musica", "Artista", "Tom", "Andamento", "Categoria"]])
