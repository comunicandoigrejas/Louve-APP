import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date
import urllib.parse
from openai import OpenAI

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

# 2. CLIENTE OPENAI & GOOGLE
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. CSS DE MARCA (By Comunicando Igrejas)
st.markdown("""
    <style>
    [data-testid="stHeader"], header, footer, .stAppDeployButton { display: none !important; }
    #MainMenu {visibility: hidden !important;}
    .block-container { padding-top: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE APOIO ---
def carregar_louvores():
    try:
        df = conn.read(worksheet="Louvores", ttl=0)
        df.columns = [c.strip() for c in df.columns]
        df['Musica_Busca'] = df['Musica'].fillna('').astype(str).str.lower().str.strip()
        return df
    except: return pd.DataFrame()

def carregar_cultos():
    try: return conn.read(worksheet="Cultos", ttl=0)
    except: return pd.DataFrame()

def gerar_devocional_ia(tema):
    prompt = f"""
    Escreva um devocional para um grupo de louvor de uma igreja evangélica chamado Grupo Shekiná.
    O tema é: {tema}.
    Requisitos:
    1. Comece com um versículo bíblico chave relacionado ao tema.
    2. Escreva uma reflexão profunda de aproximadamente 200 palavras voltada para músicos e ministros de louvor.
    3. Use um tom encorajador, espiritual e técnico quando relevante.
    4. Termine com uma breve oração.
    5. Adicione emojis para tornar a leitura dinâmica no WhatsApp.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # ou gpt-4
            messages=[{"role": "system", "content": "Você é um pastor e líder de adoração experiente."},
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro ao gerar devocional: {e}"

# 4. SIDEBAR
st.sidebar.markdown("# 🛡️ Grupo Shekiná")
st.sidebar.markdown(f'''
    <a href="https://www.instagram.com/comunicandoigrejas/" target="_blank">
        <button style="width: 100%; background-color: #333333; color: white; border: 1px solid #555555; padding: 10px; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 20px;">
            🔧 By Comunicando Igrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

# 5. LOGIN (Senhas: igreja2026 / shekina123)
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    senha = st.text_input("Senha da Equipe:", type="password")
    if st.button("Acessar"):
        if senha in ["igreja2026", "shekina123"]:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 6. INTERFACE LÍDER
perfil = st.sidebar.radio("Nível:", ["Integrantes", "Líder"])

if perfil == "Líder" and st.sidebar.text_input("Chave Mestre:", type="password") == "shekina123":
    t1, t2, t3, t4 = st.tabs(["🎸 Repertório", "➕ Cadastrar", "📜 Histórico", "🌅 Devocional IA"])

    with t1:
        st.subheader("Montar Setlist")
        df_l = carregar_louvores()
        busca = st.text_input("Pesquisar louvor:").lower()
        df_f = df_l[df_l['Musica_Busca'].str.contains(busca)] if busca else df_l
        sel = st.dataframe(df_f[["Musica", "Artista", "Tom"]], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
        
        # Botão WhatsApp Setlist
        if sel.selection.rows:
            selecionadas = df_f.iloc[sel.selection.rows]['Musica'].tolist()
            msg_wa = f"🎸 *SETLIST SHEKINÁ*\n\n" + "\n".join([f"• {m}" for m in selecionadas])
            link_wa = f"https://wa.me/?text={urllib.parse.quote(msg_wa)}"
            st.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:8px; cursor:pointer;">📢 ENVIAR SETLIST</button></a>', unsafe_allow_html=True)

    with t4:
        st.subheader("🌅 Gerador de Devocional com IA")
        tema = st.selectbox("Escolha o foco da semana:", ["Unidade", "Santidade", "Excelência", "Gratidão", "Oração", "Quebrantamento"])
        
        if st.button("✨ Gerar Devocional de 200 palavras"):
            with st.spinner("A IA está escrevendo..."):
                texto_gerado = gerar_devocional_ia(tema)
                st.session_state.devocional_pronto = texto_gerado
        
        if 'devocional_pronto' in st.session_state:
            st.markdown("---")
            st.write(st.session_state.devocional_pronto)
            
            # Botão WhatsApp Devocional
            msg_final = st.session_state.devocional_pronto + "\n\n🔧 _By Comunicando Igrejas_"
            link_dev_wa = f"https://wa.me/?text={urllib.parse.quote(msg_final)}"
            st.markdown(f'<a href="{link_dev_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:8px; cursor:pointer;">📲 ENVIAR PARA O GRUPO</button></a>', unsafe_allow_html=True)

else:
    st.header("📖 Espaço do Integrante")
    st.info("Aqui aparecerá o repertório publicado pelo líder.")
    # (Lógica de exibição de cultos salvas mantida conforme v40)
