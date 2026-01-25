import streamlit as st
from streamlit_gsheets import GSheetsConnection
from openai import OpenAI
import pandas as pd
from datetime import date
import urllib.parse

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

# 2. INICIALIZAÇÃO (OpenAI e Google Sheets)
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    st.error("Erro: Verifique a chave 'OPENAI_API_KEY' nos Secrets.")

conn = st.connection("gsheets", type=GSheetsConnection)

# 3. CSS DE MARCA (By Comunicando Igrejas)
st.markdown("""
    <style>
    [data-testid="stHeader"], header, footer, .stAppDeployButton { display: none !important; }
    #MainMenu {visibility: hidden !important;}
    .block-container { padding-top: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS ---
def carregar_louvores():
    try:
        df = conn.read(worksheet="Louvores", ttl=0)
        df.columns = [c.strip() for c in df.columns]
        df['Musica_Busca'] = df['Musica'].fillna('').astype(str).str.lower().str.strip()
        return df
    except: return pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento", "Categoria", "Musica_Busca"])

def carregar_cultos():
    try:
        df = conn.read(worksheet="Cultos", ttl=0)
        df.columns = [c.strip() for c in df.columns]
        return df
    except: return pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Tema_Culto", "Musicas"])

def gerar_devocional_ia(tema):
    prompt = f"Escreva um devocional de 200 palavras sobre {tema} para músicos da igreja ISOSED Cosmópolis, incluindo versículo e oração."
    try:
        res = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
        return res.choices[0].message.content
    except: return "Erro ao gerar devocional."

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

# 6. INTERFACE
perfil = st.sidebar.radio("Nível:", ["Integrantes", "Líder"])

if perfil == "Líder" and st.sidebar.text_input("Chave Mestre:", type="password") == "shekina123":
    df_l = carregar_louvores()
    t1, t2, t3, t4 = st.tabs(["🎸 Montar Setlist", "➕ Novo Louvor", "📜 Histórico", "🌅 Devocional IA"])

    with t1:
        st.subheader("Seleção de Louvores")
        busca = st.text_input("Pesquisar no catálogo:").lower()
        df_f = df_l[df_l['Musica_Busca'].str.contains(busca)] if busca else df_l
        
        sel = st.dataframe(df_f[["Musica", "Artista", "Tom"]], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
        
        if 'cart' not in st.session_state: st.session_state.cart = []
        if sel.selection.rows:
            selecionadas = df_f.iloc[sel.selection.rows]['Musica'].tolist()
            for sm in selecionadas:
                if sm not in st.session_state.cart: st.session_state.cart.append(sm)
        
        st.write("---")
        st.subheader("Configurações do Culto")
        c1, c2 = st.columns(2)
        with c1:
            nome_c = st.text_input("Nome do Culto:")
            data_c = st.date_input("Data:", date.today())
        with c2:
            tema_c = st.text_input("Tema do Culto:")
            final_list = st.multiselect("Setlist Final:", options=sorted(df_l['Musica'].tolist()), 
                                        default=[m for m in st.session_state.cart if m in df_l['Musica'].tolist()])
            st.session_state.cart = final_list

        col_pub, col_wa = st.columns(2)
        with col_pub:
            if st.button("💾 PUBLICAR PARA INTEGRANTES"):
                if nome_c and final_list:
                    df_c_atual = carregar_cultos()
                    novo_c = pd.DataFrame([[str(data_c), nome_c, tema_c, ", ".join(final_list)]], 
                                         columns=["Data_Culto", "Nome_Culto", "Tema_Culto", "Musicas"])
                    conn.update(worksheet="Cultos", data=pd.concat([df_c_atual, novo_c], ignore_index=True))
                    st.success("✅ Publicado!")
                    st.session_state.cart = []

        with col_wa:
            if nome_c and final_list:
                # TEMPLATE DA MENSAGEM SOLICITADO
                texto_wa = f"A paz do senhor grupo segue os louvores do culto *{nome_c}* .......\n\n"
                texto_wa += f"📅 *Data:* {data_c}\n"
                texto_wa += f"📖 *Tema:* {tema_c}\n\n"
                texto_wa += "🎶 *LOUVORES:*\n"
                for i, m in enumerate(final_list, 1):
                    # Busca o tom para enviar na mensagem também
                    tom_m = df_l[df_l['Musica'] == m]['Tom'].values[0] if m in df_l['Musica'].values else "?"
                    texto_wa += f"{i}. {m} (Tom: {tom_m})\n"
                
                texto_wa += "\n🔧 _By Comunicando Igrejas_"
                link_wa = f"https://wa.me/?text={urllib.parse.quote(texto_wa)}"
                st.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:8px; font-weight:bold; cursor:pointer;">📢 ENVIAR PELO WHATSAPP</button></a>', unsafe_allow_html=True)

    with t4:
        st.subheader("🌅 Devocional com IA")
        tema_dev = st.selectbox("Tema:", ["Fé", "Unidade", "Santidade", "Gratidão"])
        if st.button("Gerar Devocional"):
            with st.spinner("Escrevendo..."):
                txt = gerar_devocional_ia(tema_dev)
                st.session_state.dev_txt = txt
        if 'dev_txt' in st.session_state:
            st.write(st.session_state.dev_txt)
            link_dev = f"https://wa.me/?text={urllib.parse.quote(st.session_state.dev_txt + 'n\n🔧 _By Comunicando Igrejas_')}"
            st.markdown(f'<a href="{link_dev}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:8px; font-weight:bold; cursor:pointer;">📢 ENVIAR DEVOCIONAL</button></a>', unsafe_allow_html=True)

else:
    # VISÃO INTEGRANTES (Simplificada com Tema)
    st.header("📖 Repertório Oficial")
    hist = carregar_cultos()
    if hist.empty: st.info("Sem publicações.")
    else:
        op = (hist['Data_Culto'].astype(str) + " | " + hist['Nome_Culto']).tolist()[::-1]
        escolha = st.selectbox("Selecione o Culto:", op)
        if escolha:
            dt, nm = escolha.split(" | ")
            reg = hist[(hist['Data_Culto'].astype(str) == dt) & (hist['Nome_Culto'] == nm)].iloc[0]
            st.info(f"📅 {dt} | ⛪ {nm} | 📖 Tema: {reg['Tema_Culto']}")
            m_list = reg['Musicas'].split(", ")
            df_full = carregar_louvores()
            st.table(df_full[df_full['Musica'].isin(m_list)][["Musica", "Artista", "Tom"]])
