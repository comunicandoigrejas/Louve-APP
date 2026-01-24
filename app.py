import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse
import os

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

# --- CONFIGURAÇÕES DO SISTEMA ---
ARQUIVO_LOUVORES = "louvores.csv"
ARQUIVO_CULTOS = "cultos_salvos.csv"
SENHA_ACESSO_GERAL = "igreja2026"  
SENHA_LIDER = "shekina123"
LISTA_CATEGORIAS = ["Adoração", "Quebrantamento", "Congregacional", "Avivamento", "Espontâneo", "Júbilo", "Profético", "Antigo", "Clássico"]
LISTA_ANDAMENTO = ["Lento", "Médio", "Rápido"]

# --- FUNÇÕES DE DADOS (ATUALIZADAS PARA 5 COLUNAS) ---
def carregar_dados():
    if not os.path.exists(ARQUIVO_LOUVORES):
        # Cria o arquivo com a nova estrutura: Musica, Artista, Tom, Andamento, Categoria
        pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento", "Categoria"]).to_csv(ARQUIVO_LOUVORES, index=False, encoding='utf-8')
    
    try:
        df = pd.read_csv(ARQUIVO_LOUVORES, encoding='utf-8')
        # Garante que a coluna Andamento exista em arquivos antigos
        if "Andamento" not in df.columns:
            df["Andamento"] = "Médio"
        
        df = df.dropna(subset=['Musica'])
        df['Musica_Busca'] = df['Musica'].astype(str).str.lower().str.strip()
        return df
    except:
        return pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento", "Categoria", "Musica_Busca"])

def carregar_cultos():
    if os.path.exists(ARQUIVO_CULTOS):
        return pd.read_csv(ARQUIVO_CULTOS, encoding='utf-8')
    return pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Musicas"])

# 3. SIDEBAR E ASSINATURA
st.sidebar.markdown("# 🛡️ Grupo Shekiná")
st.sidebar.markdown(f'''
    <a href="https://www.instagram.com/comunicandoigrejas/" target="_blank">
        <button style="width: 100%; background-color: #333333; color: white; border: 1px solid #555555; padding: 10px; border-radius: 8px; cursor: pointer; font-weight: bold;">
            🔧 By Comunicando Igrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

# 4. LOGIN OBRIGATÓRIO
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🛡️ Acesso Restrito")
    s = st.text_input("Senha de Entrada:", type="password")
    if st.button("Entrar"):
        if s in [SENHA_ACESSO_GERAL, SENHA_LIDER]:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 5. INTERFACE PRINCIPAL
p = st.sidebar.radio("Nível:", ["Integrantes", "Líder"])

if p == "Líder" and st.sidebar.text_input("Chave Mestre:", type="password") == SENHA_LIDER:
    df_m = carregar_dados()
    t1, t2, t3, t4, t5 = st.tabs(["🎸 Repertório", "➕ Cadastrar", "🗑️ Excluir", "📜 Histórico", "📂 Banco de Dados"])

    with t1:
        st.subheader("Montar Repertório")
        c1, c2, c3 = st.columns(3)
        with c1: busca = st.text_input("Nome:").lower()
        with c2: f_cat = st.selectbox("Estilo:", ["Todos"] + LISTA_CATEGORIAS)
        with c3: f_and = st.selectbox("Andamento:", ["Todos"] + LISTA_ANDAMENTO)
        
        df_f = df_m.copy()
        if f_cat != "Todos": df_f = df_f[df_f['Categoria'].str.contains(f_cat, na=False)]
        if f_and != "Todos": df_f = df_f[df_f['Andamento'] == f_and]
        if busca: df_f = df_f[df_f['Musica_Busca'].str.contains(busca)]
        
        sel = st.dataframe(df_f[['Musica', 'Artista', 'Tom', 'Andamento', 'Categoria']], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
        
        if 'set' not in st.session_state: st.session_state.set = []
        if sel.selection.rows:
            selecionadas = df_f.iloc[sel.selection.rows]['Musica'].tolist()
            for s in selecionadas:
                if s not in st.session_state.set: st.session_state.set.append(s)
        
        n_c = st.text_input("Título do Culto:")
        l_v = sorted(df_m['Musica'].tolist())
        final = st.multiselect("Setlist:", options=l_v, default=[m for m in st.session_state.set if m in l_v])
        st.session_state.set = final
        
        if st.button("💾 PUBLICAR"):
            if n_c and final:
                novo = pd.DataFrame([[str(date.today()), n_c, ", ".join(final)]], columns=["Data_Culto", "Nome_Culto", "Musicas"])
                pd.concat([carregar_cultos(), novo], ignore_index=True).to_csv(ARQUIVO_CULTOS, index=False)
                st.success("Publicado!")

    with t2:
        st.subheader("Novo Cadastro")
        with st.form("cad", clear_on_submit=True):
            m, a, t = st.text_input("Música:"), st.text_input("Artista:"), st.text_input("Tom:")
            and_v = st.select_slider("Andamento:", options=LISTA_ANDAMENTO, value="Médio")
            cat_v = st.multiselect("Categorias:", LISTA_CATEGORIAS)
            if st.form_submit_button("Salvar"):
                nova = pd.DataFrame([[m, a, t, and_v, ", ".join(cat_v)]], columns=["Musica", "Artista", "Tom", "Andamento", "Categoria"])
                pd.concat([carregar_dados().drop(columns=['Musica_Busca']), nova], ignore_index=True).to_csv(ARQUIVO_LOUVORES, index=False)
                st.success("Salvo!")
                st.rerun()

    with t3:
        st.subheader("Excluir")
        m_ex = st.selectbox("Música:", [""] + sorted(df_m['Musica'].tolist()))
        if m_ex and st.button("Excluir"):
            df_m[df_m['Musica'] != m_ex].drop(columns=['Musica_Busca']).to_csv(ARQUIVO_LOUVORES, index=False)
            st.rerun()

    with t5:
        st.subheader("Importar/Exportar CSV")
        st.download_button("Baixar louvores.csv", data=df_m.drop(columns=['Musica_Busca']).to_csv(index=False).encode('utf-8'), file_name="louvores.csv", mime="text/csv")
        up = st.file_uploader("Substituir lista (Upload)", type="csv")
        if up and st.button("Confirmar Upload"):
            pd.read_csv(up).to_csv(ARQUIVO_LOUVORES, index=False)
            st.rerun()

else:
    st.header("📖 Repertório Oficial")
    hist = carregar_cultos()
    if hist.empty: st.info("Nada publicado.")
    else:
        op = (hist['Data_Culto'].astype(str) + " | " + hist['Nome_Culto']).tolist()[::-1]
        escolha = st.selectbox("Selecione o Culto:", op)
        if escolha:
            d, n = escolha.split(" | ")
            reg = hist[(hist['Data_Culto'].astype(str) == d) & (hist['Nome_Culto'] == n)].iloc[0]
            musicas = reg['Musicas'].split(", ")
            st.table(carregar_dados()[carregar_dados()['Musica'].isin(musicas)][['Musica', 'Artista', 'Tom', 'Andamento', 'Categoria']])
