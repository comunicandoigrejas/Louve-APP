import streamlit as st
from streamlit_gsheets import GSheetsConnection
from openai import OpenAI
import pandas as pd
from datetime import date
import urllib.parse

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

# 2. INICIALIZAÇÃO
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. CSS PARA FOCO NA PESQUISA
st.markdown("""
    <style>
    [data-testid="stHeader"], header, footer, .stAppDeployButton { display: none !important; }
    #MainMenu {visibility: hidden !important;}
    .block-container { padding-top: 1rem !important; }
    /* Estilo para destacar o campo de busca */
    .stTextInput > div > div > input {
        background-color: #f0f2f6;
        color: #31333F;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS ---
@st.cache_data(ttl=60) # Cache de 1 minuto para busca ultra rápida
def carregar_louvores_busca():
    try:
        df = conn.read(worksheet="Louvores", ttl=0)
        df.columns = [c.strip() for c in df.columns]
        df['Musica_Busca'] = df['Musica'].fillna('').astype(str).str.lower().str.strip()
        return df
    except: return pd.DataFrame()

def carregar_cultos():
    try: return conn.read(worksheet="Cultos", ttl=0)
    except: return pd.DataFrame()

# 4. SIDEBAR
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
    s = st.text_input("Senha da Equipe:", type="password")
    if st.button("Entrar"):
        if s in ["igreja2026", "shekina123"]:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 6. INTERFACE LÍDER
perfil = st.sidebar.radio("Nível:", ["Integrantes", "Líder"])

if perfil == "Líder" and st.sidebar.text_input("Chave Mestre:", type="password") == "shekina123":
    df_l = carregar_louvores_busca()
    t1, t2, t3, t4 = st.tabs(["🎸 Montar Setlist", "➕ Novo Louvor", "📜 Histórico", "🌅 Devocional IA"])

    with t1:
        st.subheader("🔍 Pesquisa em Tempo Real")
        # O segredo do "conforme digita" está aqui
        busca = st.text_input("Digite o nome do louvor para filtrar a lista:", placeholder="Ex: Aclame ao Senhor...")
        
        df_f = df_l[df_l['Musica_Busca'].str.contains(busca.lower())] if busca else df_l
        
        st.write(f"Exibindo {len(df_f)} de {len(df_l)} louvores")
        
        # Tabela interativa para seleção
        sel = st.dataframe(df_f[["Musica", "Artista", "Tom", "Andamento"]], 
                           use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
        
        # Gerenciamento inteligente do Carrinho (Session State)
        if 'cart' not in st.session_state: st.session_state.cart = []
        
        if sel.selection.rows:
            selecionadas_agora = df_f.iloc[sel.selection.rows]['Musica'].tolist()
            for s_musica in selecionadas_agora:
                if s_musica not in st.session_state.cart:
                    st.session_state.cart.append(s_musica)
        
        st.write("---")
        st.subheader("📝 Detalhes do Culto")
        col1, col2 = st.columns(2)
        with col1:
            nome_c = st.text_input("Nome do Culto:", value="Culto de Celebração")
            data_c = st.date_input("Data:", date.today())
        with col2:
            tema_c = st.text_input("Tema do Culto:", placeholder="Ex: Santidade")
            final_list = st.multiselect("Setlist Final (Ajuste a ordem aqui):", 
                                        options=sorted(df_l['Musica'].tolist()), 
                                        default=[m for m in st.session_state.cart if m in df_l['Musica'].tolist()])
            st.session_state.cart = final_list

        if st.button("💾 PUBLICAR PARA EQUIPE"):
            if nome_c and final_list:
                df_c_atual = carregar_cultos()
                novo_c = pd.DataFrame([[str(data_c), nome_c, tema_c, ", ".join(final_list)]], 
                                     columns=["Data_Culto", "Nome_Culto", "Tema_Culto", "Musicas"])
                conn.update(worksheet="Cultos", data=pd.concat([df_c_atual, novo_c], ignore_index=True))
                st.success("✅ Publicado no Google Sheets!")
                st.session_state.cart = []

        # BOTÃO WHATSAPP COM O TEMPLATE PEDIDO
        if nome_c and final_list:
            texto_wa = f"A paz do senhor grupo segue os louvores do culto *{nome_c}* .......\n\n"
            texto_wa += f"📅 *Data:* {data_c}\n"
            texto_wa += f"📖 *Tema:* {tema_c}\n\n"
            texto_wa += "🎶 *LOUVORES:*\n"
            for i, m in enumerate(final_list, 1):
                tom_m = df_l[df_l['Musica'] == m]['Tom'].values[0] if m in df_l['Musica'].values else "?"
                texto_wa += f"{i}. {m} (Tom: {tom_m})\n"
            
            texto_wa += "\n🔧 _By Comunicando Igrejas_"
            link_wa = f"https://wa.me/?text={urllib.parse.quote(texto_wa)}"
            st.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:8px; font-weight:bold; cursor:pointer; font-size:16px;">📢 ENVIAR PARA WHATSAPP</button></a>', unsafe_allow_html=True)

    # ... (Restante do código de Cadastro e IA mantidos)
else:
    # VISÃO INTEGRANTES
    st.header("📖 Repertório Publicado")
    hist = carregar_cultos()
    if hist.empty: st.info("Nada publicado.")
    else:
        op = (hist['Data_Culto'].astype(str) + " | " + hist['Nome_Culto']).tolist()[::-1]
        escolha = st.selectbox("Selecione o Culto:", op)
        if escolha:
            dt, nm = escolha.split(" | ")
            reg = hist[(hist['Data_Culto'].astype(str) == dt) & (hist['Nome_Culto'] == nm)].iloc[0]
            st.info(f"📅 {dt} | ⛪ {nm} | 📖 Tema: {reg['Tema_Culto']}")
            m_list = reg['Musicas'].split(", ")
            df_full = carregar_louvores_busca()
            st.table(df_full[df_full['Musica'].isin(m_list)][["Musica", "Artista", "Tom"]])
