import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse
import os

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

# 2. CSS "FORÇA BRUTA" - LIMPEZA TOTAL E BRANDING
# Oculta o selo do Streamlit Cloud, Menu, Header e Footer
st.markdown("""
    <style>
    [data-testid="stHeader"], header, footer, .stAppDeployButton { display: none !important; visibility: hidden !important; }
    #MainMenu {visibility: hidden !important;}
    div[class^="viewerBadge"], [data-testid="stStatusWidget"], .viewerBadge_container__1QSob { display: none !important; }
    button[title="View source"], .st-emotion-cache-164784p { display: none !important; }
    .block-container { padding-top: 1rem !important; }
    
    /* Estilização dos Botões */
    .stButton>button { border-radius: 8px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÕES DO SISTEMA ---
LISTA_CATEGORIAS = ["Adoração", "Quebrantamento", "Congregacional", "Avivamento", "Espontâneo", "Júbilo", "Profético", "Antigo", "Clássico"]
SENHA_ACESSO_GERAL = "igreja2026"  
SENHA_LIDER = "shekina123"        
ARQUIVO_LOUVORES = "louvores.csv"
ARQUIVO_CULTOS = "cultos_salvos.csv"

# --- FUNÇÕES DE DADOS (CORREÇÃO DO ERRO image_ed4870.png) ---
def carregar_dados():
    if not os.path.exists(ARQUIVO_LOUVORES):
        pd.DataFrame(columns=["Musica", "Artista", "Tom", "Categoria"]).to_csv(ARQUIVO_LOUVORES, index=False)
    try:
        df = pd.read_csv(ARQUIVO_LOUVORES)
        # SOLUÇÃO DO ERRO: Criação forçada da coluna de busca na memória
        df['Musica_Busca'] = df['Musica'].fillna('').astype(str).str.lower().str.strip()
        df['Categoria'] = df['Categoria'].fillna('Não Definido')
        return df
    except:
        return pd.DataFrame(columns=["Musica", "Artista", "Tom", "Categoria", "Musica_Busca"])

def carregar_cultos():
    if os.path.exists(ARQUIVO_CULTOS):
        try: return pd.read_csv(ARQUIVO_CULTOS)
        except: pass
    return pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Musicas"])

# 3. SIDEBAR - VISÍVEL ANTES E DEPOIS DO LOGIN
st.sidebar.markdown("# 🛡️ Grupo Shekiná")
link_ig = "https://www.instagram.com/comunicandoigrejas/"
st.sidebar.markdown(f'''
    <a href="{link_ig}" target="_blank">
        <button style="width: 100%; background-color: #333333; color: white; border: 1px solid #555555; padding: 12px; border-radius: 10px; cursor: pointer; font-weight: bold; margin-bottom: 25px;">
            🔧 By Comunicando Igrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

# 4. TELA DE LOGIN OBRIGATÓRIA
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🛡️ Acesso Restrito")
    col_log, _ = st.columns([1, 1])
    with col_log:
        senha_in = st.text_input("Senha da Equipe:", type="password")
        if st.button("Acessar Sistema"):
            if senha_in in [SENHA_ACESSO_GERAL, SENHA_LIDER]:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    st.stop()

# --- CONTEÚDO LIBERADO ---
perfil = st.sidebar.radio("Nível de Acesso:", ["Integrantes", "Líder (Gestão)"])

if perfil == "Líder (Gestão)":
    chave_gestor = st.sidebar.text_input("Chave de Gestor:", type="password")
    if chave_gestor == SENHA_LIDER:
        t1, t2, t3, t4, t5 = st.tabs(["🎸 Repertório", "➕ Novo Louvor", "🗑️ Excluir", "🌅 Devocional", "📜 Histórico"])
        df_m = carregar_dados()

        with t1:
            st.subheader("Montar Lista de Culto")
            col_b1, col_b2 = st.columns(2)
            with col_b1: b_nome = st.text_input("Procurar nome:").lower()
            with col_b2: b_cat = st.selectbox("Estilo:", ["Todos"] + LISTA_CATEGORIAS)
            
            df_f = df_m.copy()
            if b_cat != "Todos": df_f = df_f[df_f['Categoria'].str.contains(b_cat, na=False)]
            if b_nome: df_f = df_f[df_f['Musica_Busca'].str.contains(b_nome)]
            
            sel = st.dataframe(df_f[['Musica', 'Artista', 'Tom', 'Categoria']], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
            
            if 'cart' not in st.session_state: st.session_state.cart = []
            if sel.selection.rows:
                for m in df_f.iloc[sel.selection.rows]['Musica'].tolist():
                    if m not in st.session_state.cart: st.session_state.cart.append(m)
            
            c_save, c_clear = st.columns([3, 1])
            with c_save:
                nome_c = st.text_input("Título do Culto (Ex: Varões):")
                data_c = st.date_input("Data:", date.today())
                final_list = st.multiselect("Setlist Final:", options=sorted(df_m['Musica'].tolist()), default=[m for m in st.session_state.cart if m in df_m['Musica'].tolist()])
                st.session_state.cart = final_list
                if st.button("💾 PUBLICAR PARA EQUIPE"):
                    if nome_c and final_list:
                        reg = pd.DataFrame([[str(data_c), nome_c, ", ".join(final_list)]], columns=["Data_Culto", "Nome_Culto", "Musicas"])
                        pd.concat([carregar_cultos(), reg], ignore_index=True).to_csv(ARQUIVO_CULTOS, index=False)
                        st.success("✅ Repertório publicado!")
            with c_clear:
                st.write("---")
                if st.button("🗑️ Limpar Rascunho"):
                    st.session_state.cart = []
                    st.rerun()

        with t2:
            st.subheader("Cadastrar no Catálogo")
            with st.form("add", clear_on_submit=True):
                n, a, t = st.text_input("Música:"), st.text_input("Cantor/Ministério:"), st.text_input("Tom:")
                c = st.multiselect("Classificação:", LISTA_CATEGORIAS)
                if st.form_submit_button("✅ Salvar Música"):
                    nova = pd.DataFrame([[n, a, t, ", ".join(c)]], columns=["Musica", "Artista", "Tom", "Categoria"])
                    pd.concat([carregar_dados().drop(columns=['Musica_Busca']), nova], ignore_index=True).to_csv(ARQUIVO_LOUVORES, index=False)
                    st.success("Adicionado!")
                    st.rerun()

        with t3:
            st.subheader("Excluir do Catálogo")
            m_del = st.selectbox("Selecione para remover:", [""] + sorted(df_m['Musica'].tolist()))
            if m_del and st.button("CONFIRMAR EXCLUSÃO"):
                df_m[df_m['Musica'] != m_del].drop(columns=['Musica_Busca']).to_csv(ARQUIVO_LOUVORES, index=False)
                st.rerun()

        with t4:
            st.subheader("Gerar Devocional")
            tema = st.text_input("Tema:")
            if st.button("Gerar Mensagem"):
                msg = f"🌅 *Devocional Shekiná*\n📍 *Tema:* {tema}\n\n🔧 By Comunicando Igrejas"
                st.text_area("Copie e cole:", msg)

        with t5:
            st.subheader("Histórico de Cultos")
            h = carregar_cultos()
            if not h.empty:
                if st.button("🔴 APAGAR TODO O HISTÓRICO"):
                    pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Musicas"]).to_csv(ARQUIVO_CULTOS, index=False)
                    st.rerun()
                for i, r in h.sort_values(by="Data_Culto", ascending=False).iterrows():
                    with st.expander(f"📅 {r['Data_Culto']} - {r['Nome_Culto']}"):
                        st.write(f"🎶 {r['Musicas']}")
    else:
        st.sidebar.warning("Aguardando Chave de Gestor...")

else:
    st.header("📖 Repertório Oficial")
    hist = carregar_cultos()
    if hist.empty: st.info("Nada publicado.")
    else:
        op = (hist['Data_Culto'].astype(str) + " | " + hist['Nome_Culto']).tolist()[::-1]
        esc = st.selectbox("Selecione o Culto:", op)
        if esc:
            d, n = esc.split(" | ")
            reg = hist[(hist['Data_Culto'].astype(str) == d) & (hist['Nome_Culto'] == n)].iloc[0]
            st.table(carregar_dados()[carregar_dados()['Musica'].isin(reg['Musicas'].split(", "))][['Musica', 'Artista', 'Tom', 'Categoria']])
