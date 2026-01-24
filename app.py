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
    div[class^="viewerBadge"], [data-testid="stStatusWidget"], .viewerBadge_container__1QSob { 
        display: none !important; 
    }
    .block-container { padding-top: 2rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LISTA OFICIAL DE CATEGORIAS ---
LISTA_CATEGORIAS = [
    "Adoração", "Quebrantamento", "Congregacional", "Avivamento", 
    "Espontâneo", "Júbilo", "Profético", "Antigo", "Clássico"
]

# --- CONFIGURAÇÕES DE SEGURANÇA ---
SENHA_ACESSO_GERAL = "igreja2026"  
SENHA_LIDER = "shekina123"        
ARQUIVO_LOUVORES = "louvores.csv"
ARQUIVO_CULTOS = "cultos_salvos.csv"

# 3. SIDEBAR (ASSINATURA)
st.sidebar.markdown("# 🎸 Grupo Shekiná")
link_ig = "https://www.instagram.com/comunicandoigrejas/"
st.sidebar.markdown(f'''
    <a href="{link_ig}" target="_blank">
        <button style="width: 100%; background-color: #333333; color: white; border: 1px solid #555555; padding: 10px; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 25px;">
            🔧 By Comunicando Igrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

# 4. LÓGICA DE ACESSO
if 'logado' not in st.session_state: st.session_state.logado = False
if not st.session_state.logado:
    st.title("🛡️ Acesso Restrito")
    col_l, _ = st.columns([1, 1])
    with col_l:
        entrada = st.text_input("Senha de Acesso:", type="password")
        if st.button("Entrar"):
            if entrada in [SENHA_ACESSO_GERAL, SENHA_LIDER]:
                st.session_state.logado = True
                st.rerun()
            else: st.error("Senha incorreta.")
    st.stop()

# --- FUNÇÕES DE DADOS ---
def carregar_dados():
    if not os.path.exists(ARQUIVO_LOUVORES):
        pd.DataFrame(columns=["Musica", "Artista", "Tom", "Categoria"]).to_csv(ARQUIVO_LOUVORES, index=False)
    try:
        df = pd.read_csv(ARQUIVO_LOUVORES)
        df['Musica_Busca'] = df['Musica'].fillna('').astype(str).str.lower().str.strip()
        df['Categoria'] = df['Categoria'].fillna('Não Definido')
        return df
    except: return pd.DataFrame(columns=["Musica", "Artista", "Tom", "Categoria"])

def carregar_cultos():
    if os.path.exists(ARQUIVO_CULTOS):
        try: return pd.read_csv(ARQUIVO_CULTOS)
        except: pass
    return pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Musicas"])

# 5. CONTEÚDO
perfil = st.sidebar.radio("Nível de Acesso:", ["Integrantes", "Líder (Gestão)"])

if perfil == "Líder (Gestão)":
    senha_g = st.sidebar.text_input("Chave de Gestor:", type="password")
    if senha_g == SENHA_LIDER:
        t1, t2, t3, t4 = st.tabs(["🎸 Repertório", "➕ Novo Louvor", "🗑️ Excluir", "📜 Histórico"])
        df_m = carregar_dados()

        with t1:
            st.subheader("Montar Repertório")
            c1, c2 = st.columns([1, 1])
            with c1: busca = st.text_input("Nome:").lower()
            with c2: cat_filtro = st.selectbox("Filtrar por Estilo:", ["Todos"] + LISTA_CATEGORIAS)
            
            df_f = df_m.copy()
            if cat_filtro != "Todos":
                df_f = df_f[df_f['Categoria'].str.contains(cat_filtro, na=False)]
            if busca:
                df_f = df_f[df_f['Musica_Busca'].str.contains(busca)]
            
            sel = st.dataframe(df_f[['Musica', 'Artista', 'Tom', 'Categoria']], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
            
            if 'cart' not in st.session_state: st.session_state.cart = []
            if sel.selection.rows:
                for m in df_f.iloc[sel.selection.rows]['Musica'].tolist():
                    if m not in st.session_state.cart: st.session_state.cart.append(m)
            
            n_c = st.text_input("Título do Culto:")
            d_c = st.date_input("Data:", date.today())
            final = st.multiselect("Setlist Selecionada:", options=sorted(df_m['Musica'].tolist()), default=[m for m in st.session_state.cart if m in df_m['Musica'].tolist()])
            st.session_state.cart = final
            
            if st.button("💾 PUBLICAR"):
                if n_c and final:
                    reg = pd.DataFrame([[str(d_c), n_c, ", ".join(final)]], columns=["Data_Culto", "Nome_Culto", "Musicas"])
                    pd.concat([carregar_cultos(), reg], ignore_index=True).to_csv(ARQUIVO_CULTOS, index=False)
                    st.success("Publicado!")
                    msg = f"🙌 *Shekiná*\n📌 *{n_c}*\n🎶 {', '.join(final)}"
                    st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(msg)}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px; border-radius: 5px; cursor: pointer;">📢 Enviar WhatsApp</button></a>', unsafe_allow_html=True)

        with t2:
            st.subheader("Cadastrar Louvor")
            with st.form("add_louvor", clear_on_submit=True):
                nm, ar, tm = st.text_input("Música:"), st.text_input("Artista:"), st.text_input("Tom:")
                # Multiselect com as categorias que você pediu
                ct = st.multiselect("Classificação:", LISTA_CATEGORIAS)
                if st.form_submit_button("✅ Salvar"):
                    if nm and ar:
                        nova = pd.DataFrame([[nm, ar, tm, ", ".join(ct)]], columns=["Musica", "Artista", "Tom", "Categoria"])
                        pd.concat([carregar_dados().drop(columns=['Musica_Busca']), nova], ignore_index=True).to_csv(ARQUIVO_LOUVORES, index=False)
                        st.success(f"'{nm}' salvo!")
                        st.rerun()

        with t3:
            st.subheader("🗑️ Remover do Catálogo")
            m_del = st.selectbox("Música:", [""] + sorted(df_m['Musica'].tolist()))
            if m_del and st.button("Confirmar Exclusão"):
                df_m[df_m['Musica'] != m_del].drop(columns=['Musica_Busca']).to_csv(ARQUIVO_LOUVORES, index=False)
                st.rerun()

        with t4:
            st.subheader("Histórico")
            h = carregar_cultos()
            if not h.empty:
                for i, r in h.sort_values(by="Data_Culto", ascending=False).iterrows():
                    with st.expander(f"📅 {r['Data_Culto']} - {r['Nome_Culto']}"):
                        st.write(r['Musicas'])

else:
    st.header("📖 Repertório Oficial")
    hist = carregar_cultos()
    if hist.empty: st.info("Nada publicado.")
    else:
        op = (hist['Data_Culto'].astype(str) + " | " + hist['Nome_Culto']).tolist()[::-1]
        esc = st.selectbox("Escolha o Culto:", op)
        if esc:
            d, n = esc.split(" | ")
            reg = hist[(hist['Data_Culto'].astype(str) == d) & (hist['Nome_Culto'] == n)].iloc[0]
            musicas_lista = reg['Musicas'].split(", ")
            df_v = carregar_dados()
            # Mostra para o integrante a Música, o Cantor, o Tom e a Classificação
            st.table(df_v[df_v['Musica'].isin(musicas_lista)][['Musica', 'Artista', 'Tom', 'Categoria']])
