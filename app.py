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

# 3. CSS DE MARCA
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
    # Prompt ajustado para forçar emojis padrão e evitar caracteres especiais problemáticos
    prompt = f"""
    Escreva um devocional para o Grupo Shekiná (músicos da igreja).
    Tema: {tema}.
    Regras:
    1. Texto com cerca de 200 palavras.
    2. Use emojis padrão de teclado (ex: 🙏, 📖, ✨, 🎸, 🕊️).
    3. NÃO use caracteres de desenho ou triângulos especiais.
    4. Inclua um versículo e uma breve oração ao final.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Você é um líder espiritual. Use emojis universais do WhatsApp."},
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except: return "Erro ao gerar devocional."

# 4. LOGIN E NÍVEIS (igreja2026 / shekina123)
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    senha = st.text_input("Senha da Equipe:", type="password")
    if st.button("Acessar"):
        if senha in ["igreja2026", "shekina123"]:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 5. INTERFACE LÍDER
perfil = st.sidebar.radio("Nível:", ["Integrantes", "Líder"])

if perfil == "Líder" and st.sidebar.text_input("Chave Mestre:", type="password") == "shekina123":
    df_l = carregar_louvores()
    t1, t2, t3, t4 = st.tabs(["🎸 Montar Setlist", "➕ Novo Louvor", "📜 Histórico", "🌅 Devocional IA"])

    with t1:
        st.subheader("Seleção de Louvores")
        busca = st.text_input("Pesquisar louvor:").lower()
        df_f = df_l[df_l['Musica_Busca'].str.contains(busca)] if busca else df_l
        sel = st.dataframe(df_f[["Musica", "Artista", "Tom"]], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
        
        if 'cart' not in st.session_state: st.session_state.cart = []
        if sel.selection.rows:
            for m in df_f.iloc[sel.selection.rows]['Musica'].tolist():
                if m not in st.session_state.cart: st.session_state.cart.append(m)

        st.write("---")
        c1, c2 = st.columns(2)
        with c1:
            nome_c = st.text_input("Nome do Culto:")
            data_c = st.date_input("Data:", date.today())
        with c2:
            tema_c = st.text_input("Tema:")
            final_list = st.multiselect("Setlist:", options=sorted(df_l['Musica'].tolist()), 
                                        default=[m for m in st.session_state.cart if m in df_l['Musica'].tolist()])
            st.session_state.cart = final_list

        if nome_c and final_list:
            # Lógica para Data e Dia da Semana
            dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
            dia_nome = dias_semana[data_c.weekday()]
            data_formatada = data_c.strftime('%d-%m-%y')

            texto_wa = f"A paz do senhor grupo segue os louvores do culto *{nome_c}* .......\n\n"
            texto_wa += f"📅 *Data:* {data_formatada} ({dia_nome})\n"
            texto_wa += f"📖 *Tema:* {tema_c}\n\n"
            texto_wa += "🎶 *LOUVORES:*\n"
            for i, m in enumerate(final_list, 1):
                texto_wa += f"{i}. {m}\n" # Removido tom e andamento
            
            texto_wa += "\n🔧 _By Comunicando Igrejas_"
            link_wa = f"https://wa.me/?text={urllib.parse.quote(texto_wa)}"
            st.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">📢 ENVIAR SETLIST WHATSAPP</button></a>', unsafe_allow_html=True)

    with t4:
        st.subheader("🌅 Devocional IA")
        tema_dev = st.selectbox("Tema:", ["Unidade", "Santidade", "Gratidão", "Excelência"])
        if st.button("✨ Gerar Devocional"):
            with st.spinner("A IA está escrevendo..."):
                texto = gerar_devocional_ia(tema_dev)
                st.session_state.dev_pronto = texto
        
        if 'dev_pronto' in st.session_state:
            st.write(st.session_state.dev_pronto)
            link_dev = f"https://wa.me/?text={urllib.parse.quote(st.session_state.dev_pronto + 'n\n🔧 _By Comunicando Igrejas_')}"
            st.markdown(f'<a href="{link_dev}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">📢 ENVIAR DEVOCIONAL</button></a>', unsafe_allow_html=True)

else:
    # VISÃO INTEGRANTES (Ajustada com o novo padrão)
    st.header("📖 Repertório Oficial")
    hist = carregar_cultos()
    if not hist.empty:
        op = (hist['Data_Culto'].astype(str) + " | " + hist['Nome_Culto']).tolist()[::-1]
        escolha = st.selectbox("Selecione o Culto:", op)
        if escolha:
            dt_raw, nm = escolha.split(" | ")
            reg = hist[(hist['Data_Culto'].astype(str) == dt_raw) & (hist['Nome_Culto'] == nm)].iloc[0]
            st.info(f"📅 {dt_raw} | ⛪ {nm} | 📖 Tema: {reg['Tema_Culto']}")
            m_list = reg['Musicas'].split(", ")
            df_full = carregar_louvores()
            st.table(df_full[df_full['Musica'].isin(m_list)][["Musica", "Artista"]])
