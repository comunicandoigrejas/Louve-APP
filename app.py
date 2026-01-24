import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse
import os

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

# --- CONFIGURAÇÕES ---
ARQUIVO_LOUVORES = "louvores.csv"
ARQUIVO_CULTOS = "cultos_salvos.csv"
SENHA_ACESSO_GERAL = "igreja2026"  
SENHA_LIDER = "shekina123"
LISTA_CATEGORIAS = ["Adoração", "Quebrantamento", "Congregacional", "Avivamento", "Espontâneo", "Júbilo", "Profético", "Antigo", "Clássico"]
LISTA_ANDAMENTO = ["Lento", "Médio", "Rápido"]

# --- FUNÇÕES DE DADOS (5 COLUNAS + DATA) ---
def carregar_dados():
    if not os.path.exists(ARQUIVO_LOUVORES):
        pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento", "Categoria"]).to_csv(ARQUIVO_LOUVORES, index=False, encoding='utf-8')
    try:
        df = pd.read_csv(ARQUIVO_LOUVORES, encoding='utf-8')
        df = df.dropna(subset=['Musica'])
        df['Musica_Busca'] = df['Musica'].astype(str).str.lower().str.strip()
        return df
    except:
        return pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento", "Categoria", "Musica_Busca"])

def carregar_cultos():
    if not os.path.exists(ARQUIVO_CULTOS):
        pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Musicas"]).to_csv(ARQUIVO_CULTOS, index=False, encoding='utf-8')
    return pd.read_csv(ARQUIVO_CULTOS, encoding='utf-8')

# 3. SIDEBAR (ASSINATURA BY COMUNICANDO IGREJAS)
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
    st.title("🛡️ Acesso Restrito")
    s = st.text_input("Senha da Equipe:", type="password")
    if st.button("Entrar"):
        if s in [SENHA_ACESSO_GERAL, SENHA_LIDER]:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 5. INTERFACE
p = st.sidebar.radio("Nível:", ["Integrantes", "Líder"])

if p == "Líder" and st.sidebar.text_input("Chave Mestre:", type="password") == SENHA_LIDER:
    df_m = carregar_dados()
    t1, t2, t3, t4 = st.tabs(["🎸 Repertório", "➕ Cadastrar", "🗑️ Excluir", "📜 Histórico"])

    with t1:
        st.subheader("Montar Repertório")
        c1, c2, c3 = st.columns(3)
        with c1: busca = st.text_input("Filtrar Nome:").lower()
        with c2: f_cat = st.selectbox("Estilo:", ["Todos"] + LISTA_CATEGORIAS)
        with c3: f_and = st.selectbox("Andamento:", ["Todos"] + LISTA_ANDAMENTO)
        
        df_f = df_m.copy()
        if f_cat != "Todos": df_f = df_f[df_f['Categoria'].str.contains(f_cat, na=False)]
        if f_and != "Todos": df_f = df_f[df_f['Andamento'] == f_and]
        if busca: df_f = df_f[df_f['Musica_Busca'].str.contains(busca)]
        
        sel = st.dataframe(df_f[['Musica', 'Artista', 'Tom', 'Andamento', 'Categoria']], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
        
        if 'set' not in st.session_state: st.session_state.set = []
        if sel.selection.rows:
            selec = df_f.iloc[sel.selection.rows]['Musica'].tolist()
            for s_mus in selec:
                if s_mus not in st.session_state.set: st.session_state.set.append(s_mus)
        
        st.write("---")
        n_c = st.text_input("Título do Culto (Ex: Culto de Jovens):")
        data_c = st.date_input("Data do Culto:", date.today()) # CAMPO DATA
        l_v = sorted(df_m['Musica'].tolist())
        final = st.multiselect("Setlist Final:", options=l_v, default=[m for m in st.session_state.set if m in l_v])
        st.session_state.set = final
        
        if st.button("💾 PUBLICAR REPERTÓRIO"):
            if n_c and final:
                # CORREÇÃO: Salvando a data_c selecionada pelo usuário
                novo = pd.DataFrame([[str(data_c), n_c, ", ".join(final)]], columns=["Data_Culto", "Nome_Culto", "Musicas"])
                pd.concat([carregar_cultos(), novo], ignore_index=True).to_csv(ARQUIVO_CULTOS, index=False, encoding='utf-8')
                st.success(f"✅ Repertório para o dia {data_c} publicado!")
                st.session_state.set = []
            else:
                st.warning("Preencha o nome do culto e selecione as músicas.")

    with t2:
        st.subheader("Novo Cadastro")
        with st.form("cad"):
            m, a, t = st.text_input("Música:"), st.text_input("Artista:"), st.text_input("Tom:")
            and_v = st.select_slider("Andamento:", options=LISTA_ANDAMENTO, value="Médio")
            cat_v = st.multiselect("Categorias:", LISTA_CATEGORIAS)
            if st.form_submit_button("Salvar Música"):
                nova = pd.DataFrame([[m, a, t, and_v, ", ".join(cat_v)]], columns=["Musica", "Artista", "Tom", "Andamento", "Categoria"])
                pd.concat([carregar_dados().drop(columns=['Musica_Busca']), nova], ignore_index=True).to_csv(ARQUIVO_LOUVORES, index=False, encoding='utf-8')
                st.success("Salvo com sucesso!")

    with t3:
        st.subheader("🗑️ Apagar Música")
        m_ex = st.selectbox("Escolha a música:", [""] + sorted(df_m['Musica'].tolist()))
        if m_ex and st.button("Confirmar Exclusão"):
            df_m[df_m['Musica'] != m_ex].drop(columns=['Musica_Busca']).to_csv(ARQUIVO_LOUVORES, index=False)
            st.rerun()

    with t4:
        st.subheader("📜 Histórico")
        h = carregar_cultos()
        if not h.empty:
            for i, r in h.sort_values(by="Data_Culto", ascending=False).iterrows():
                with st.expander(f"📅 {r['Data_Culto']} - {r['Nome_Culto']}"):
                    st.write(f"🎶 Músicas: {r['Musicas']}")
        else: st.info("Histórico vazio.")

# 6. VISUALIZAÇÃO DOS INTEGRANTES
else:
    st.header("📖 Repertório Publicado")
    hist = carregar_cultos()
    if hist.empty:
        st.info("Nenhum repertório disponível no momento.")
    else:
        # Mostra primeiro os cultos mais recentes
        opcoes = (hist['Data_Culto'].astype(str) + " | " + hist['Nome_Culto']).tolist()[::-1]
        escolha = st.selectbox("Selecione o Culto:", opcoes)
        
        if escolha:
            dt_sel, nome_sel = escolha.split(" | ")
            # Destaque para a Data e Nome do Culto
            st.info(f"📅 **Data:** {dt_sel} | ⛪ **Culto:** {nome_sel}")
            
            reg = hist[(hist['Data_Culto'].astype(str) == dt_sel) & (hist['Nome_Culto'] == nome_sel)].iloc[0]
            m_lista = reg['Musicas'].split(", ")
            df_v = carregar_dados()
            st.table(df_v[df_v['Musica'].isin(m_lista)][['Musica', 'Artista', 'Tom', 'Andamento', 'Categoria']])
