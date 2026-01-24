import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse
import os

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

# 2. CSS DE LIMPEZA
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

# --- FUNÇÃO DE DADOS REFORÇADA ---
def carregar_dados():
    if not os.path.exists(ARQUIVO_LOUVORES):
        df_vazio = pd.DataFrame(columns=["Musica", "Artista", "Tom", "Categoria"])
        df_vazio.to_csv(ARQUIVO_LOUVORES, index=False, encoding='utf-8')
        return df_vazio
    
    try:
        # Lendo com encoding utf-8 para evitar erros de acentuação
        df = pd.read_csv(ARQUIVO_LOUVORES, encoding='utf-8')
        
        # REMOVENDO LINHAS COMPLETAMENTE VAZIAS
        df = df.dropna(subset=['Musica'])
        
        # CRIANDO A COLUNA DE BUSCA (A que causou o erro anterior)
        df['Musica_Busca'] = df['Musica'].astype(str).str.lower().str.strip()
        df['Categoria'] = df['Categoria'].fillna('Geral')
        
        return df
    except Exception as e:
        st.error(f"Erro ao ler louvores.csv: {e}")
        return pd.DataFrame(columns=["Musica", "Artista", "Tom", "Categoria", "Musica_Busca"])

def carregar_cultos():
    if os.path.exists(ARQUIVO_CULTOS):
        return pd.read_csv(ARQUIVO_CULTOS, encoding='utf-8')
    return pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Musicas"])

# 3. SIDEBAR E BRANDING
st.sidebar.markdown("# 🛡️ Grupo Shekiná")
st.sidebar.markdown(f'''
    <a href="https://www.instagram.com/comunicandoigrejas/" target="_blank">
        <button style="width: 100%; background-color: #333333; color: white; border: 1px solid #555555; padding: 10px; border-radius: 8px; cursor: pointer; font-weight: bold;">
            🔧 By Comunicando Igrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

# 4. LOGIN
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🛡️ Login")
    s = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        if s in [SENHA_ACESSO_GERAL, SENHA_LIDER]:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 5. PAINEL PRINCIPAL
p = st.sidebar.radio("Nível:", ["Integrantes", "Líder"])

if p == "Líder":
    chave = st.sidebar.text_input("Chave Mestre:", type="password")
    if chave == SENHA_LIDER:
        df_m = carregar_dados()
        
        # --- INDICADOR DE SAÚDE DO BANCO ---
        total = len(df_m)
        st.sidebar.metric("📚 Louvores Cadastrados", total)
        if st.sidebar.button("🔄 Atualizar Banco"): st.rerun()

        t1, t2, t3, t4 = st.tabs(["🎸 Repertório", "➕ Cadastrar", "🗑️ Excluir", "📜 Histórico"])

        with t1:
            st.subheader("Montar Repertório")
            c1, c2 = st.columns(2)
            with c1: busca = st.text_input("Pesquisar por Nome:").lower()
            with c2: filtro_cat = st.selectbox("Estilo:", ["Todos"] + LISTA_CATEGORIAS)
            
            df_f = df_m.copy()
            if filtro_cat != "Todos":
                df_f = df_f[df_f['Categoria'].str.contains(filtro_cat, na=False)]
            if busca:
                df_f = df_f[df_f['Musica_Busca'].str.contains(busca)]
            
            if df_f.empty:
                st.warning("Nenhuma música encontrada com esses filtros.")
            else:
                sel = st.dataframe(df_f[['Musica', 'Artista', 'Tom', 'Categoria']], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
                
                # Gerenciamento do Carrinho (Setlist)
                if 'setlist' not in st.session_state: st.session_state.setlist = []
                if sel.selection.rows:
                    selecionadas = df_f.iloc[sel.selection.rows]['Musica'].tolist()
                    for s in selecionadas:
                        if s not in st.session_state.setlist: st.session_state.setlist.append(s)
                
                col_save, col_del = st.columns([3, 1])
                with col_save:
                    n_c = st.text_input("Nome do Culto:")
                    list_oficial = sorted(df_m['Musica'].tolist())
                    final = st.multiselect("Músicas Selecionadas:", options=list_oficial, default=[m for m in st.session_state.setlist if m in list_oficial])
                    st.session_state.setlist = final
                    if st.button("💾 PUBLICAR"):
                        if n_c and final:
                            novo = pd.DataFrame([[str(date.today()), n_c, ", ".join(final)]], columns=["Data_Culto", "Nome_Culto", "Musicas"])
                            pd.concat([carregar_cultos(), novo], ignore_index=True).to_csv(ARQUIVO_CULTOS, index=False, encoding='utf-8')
                            st.success("✅ Publicado!")
                with col_del:
                    st.write("---")
                    if st.button("🗑️ Limpar Lista"):
                        st.session_state.setlist = []
                        st.rerun()

        with t2:
            st.subheader("Novo Cadastro")
            with st.form("cad_louvor", clear_on_submit=True):
                m, a, t = st.text_input("Nome:"), st.text_input("Ministério:"), st.text_input("Tom:")
                cat = st.multiselect("Categoria:", LISTA_CATEGORIAS)
                if st.form_submit_button("✅ Salvar"):
                    if m and a:
                        nova_musica = pd.DataFrame([[m, a, t, ", ".join(cat)]], columns=["Musica", "Artista", "Tom", "Categoria"])
                        pd.concat([carregar_dados().drop(columns=['Musica_Busca']), nova_musica], ignore_index=True).to_csv(ARQUIVO_LOUVORES, index=False, encoding='utf-8')
                        st.success("Salvo!")
                        st.rerun()

        with t3:
            st.subheader("Remover Música")
            m_del = st.selectbox("Escolha:", [""] + sorted(df_m['Musica'].tolist()))
            if m_del and st.button("Excluir"):
                df_m[df_m['Musica'] != m_del].drop(columns=['Musica_Busca']).to_csv(ARQUIVO_LOUVORES, index=False, encoding='utf-8')
                st.rerun()

        with t4:
            st.subheader("Histórico")
            h = carregar_cultos()
            if not h.empty:
                if st.button("Limpar Histórico"):
                    pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Musicas"]).to_csv(ARQUIVO_CULTOS, index=False)
                    st.rerun()
                st.dataframe(h, use_container_width=True, hide_index=True)

else:
    # Lógica de integrantes mantida
    st.header("📖 Repertório Oficial")
    hist = carregar_cultos()
    if hist.empty: st.info("Nada publicado.")
    else:
        op = (hist['Data_Culto'].astype(str) + " | " + hist['Nome_Culto']).tolist()[::-1]
        escolha = st.selectbox("Culto:", op)
        if escolha:
            d, n = escolha.split(" | ")
            reg = hist[(hist['Data_Culto'].astype(str) == d) & (hist['Nome_Culto'] == n)].iloc[0]
            st.table(carregar_dados()[carregar_dados()['Musica'].isin(reg['Musicas'].split(", "))][['Musica', 'Artista', 'Tom']])
