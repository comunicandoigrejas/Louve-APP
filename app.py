import streamlit as st
from streamlit_gsheets import GSheetsConnection
from openai import OpenAI
import pandas as pd
from datetime import date
import urllib.parse

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

# 2. CLIENTE OPENAI & GOOGLE
openai_key = st.secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=openai_key) if openai_key else None
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. CSS E IDENTIDADE VISUAL (Visível antes do login)
st.markdown("""
    <style>
    [data-testid="stHeader"], header, footer, .stAppDeployButton { display: none !important; }
    #MainMenu {visibility: hidden !important;}
    .block-container { padding-top: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO E BOTÃO INSTAGRAM (SEMPRE VISÍVEIS) ---
st.title("🎸 Grupo Shekiná")

st.markdown(f'''
    <a href="https://www.instagram.com/comunicandoigrejas/" target="_blank">
        <button style="width: 100%; background-color: #E1306C; color: white; border: none; padding: 12px; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 25px;">
            📸 By Comunicando Igrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

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

# 4. LOGIN DO SISTEMA (Gateway)
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    acesso = st.text_input("Senha da Equipe:", type="password")
    if st.button("Entrar no Sistema"):
        if acesso in ["igreja2026", "shekina123"]:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 5. INTERFACE LOGADA
perfil = st.sidebar.radio("Selecione seu nível:", ["Integrantes", "Líder"])

if perfil == "Líder" and st.sidebar.text_input("Chave Mestre:", type="password") == "shekina123":
    df_l = carregar_louvores()
    t1, t2, t3, t4 = st.tabs(["🎸 Setlist", "➕ Cadastrar", "📜 Histórico", "🌅 Devocional IA"])

    with t1:
        st.subheader("Montar Escala")
        busca = st.text_input("🔍 Pesquisar louvor:").lower()
        df_f = df_l[df_l['Musica_Busca'].str.contains(busca)] if busca else df_l
        sel = st.dataframe(df_f[["Musica", "Artista"]], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
        
        if 'cart' not in st.session_state: st.session_state.cart = []
        if sel.selection.rows:
            for m in df_f.iloc[sel.selection.rows]['Musica'].tolist():
                if m not in st.session_state.cart: st.session_state.cart.append(m)

        st.write("---")
        c1, c2 = st.columns(2)
        with c1:
            nome_c = st.text_input("Tipo de Culto:")
            data_c = st.date_input("Data:", date.today())
        with c2:
            tema_c = st.text_input("Tema:")
            final_list = st.multiselect("Setlist Final:", options=sorted(df_l['Musica'].tolist()) if not df_l.empty else [], 
                                        default=[m for m in st.session_state.cart if m in df_l['Musica'].tolist()])
            st.session_state.cart = final_list

        if nome_c and final_list:
            dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
            data_formatada = data_c.strftime('%d-%m-%y')
            dia_nome = dias[data_c.weekday()]

            # Template da Mensagem WhatsApp
            msg_wa = f"A paz do senhor grupo segue os louvores do culto *{nome_c}* .......\n\n"
            msg_wa += f"📅 *Data:* {data_formatada} ({dia_nome})\n"
            msg_wa += f"📖 *Tema:* {tema_c}\n\n🎶 *LOUVORES:*\n"
            for i, m in enumerate(final_list, 1): msg_wa += f"{i}. {m}\n"
            msg_wa += "\n🔧 _By Comunicando Igrejas_"
            
            col_save, col_wa = st.columns(2)
            with col_save:
                if st.button("💾 PUBLICAR E SALVAR"):
                    df_h = carregar_cultos()
                    novo = pd.DataFrame([[data_formatada, nome_c, tema_c, ", ".join(final_list)]], columns=df_h.columns)
                    conn.update(worksheet="Cultos", data=pd.concat([df_h, novo], ignore_index=True))
                    st.success("✅ Salvo no histórico!")
            with col_wa:
                link = f"https://wa.me/?text={urllib.parse.quote(msg_wa)}"
                st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">📢 ENVIAR WHATSAPP</button></a>', unsafe_allow_html=True)

    with t4:
        st.subheader("🌅 Devocional IA")
        if st.button("✨ Gerar Mensagem de 200 palavras"):
            with st.spinner("IA escrevendo..."):
                prompt = f"Escreva um devocional para o Grupo Shekiná sobre {tema_c if tema_c else 'Adoração'}. Mínimo 200 palavras. Use emojis 🙏, ✨, 📖, 🕊️. Seja dinâmico."
                res = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
                st.session_state.dev_ia = res.choices[0].message.content
        if 'dev_ia' in st.session_state:
            st.info(st.session_state.dev_ia)
            link_dev = f"https://wa.me/?text={urllib.parse.quote(st.session_state.dev_ia + 'n\n🔧 _By Comunicando Igrejas_')}"
            st.markdown(f'<a href="{link_dev}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">📢 ENVIAR DEVOCIONAL</button></a>', unsafe_allow_html=True)

else:
    # ÁREA INTEGRANTES
    st.header("📖 Repertório Oficial")
    hist = carregar_cultos()
    if not hist.empty:
        op = (hist['Data_Culto'].astype(str) + " | " + hist['Nome_Culto']).tolist()[::-1]
        escolha = st.selectbox("Selecione o Culto:", op)
        if escolha:
            dt, nm = escolha.split(" | ")
            reg = hist[(hist['Data_Culto'].astype(str) == dt) & (hist['Nome_Culto'] == nm)].iloc[0]
            st.info(f"📅 {dt} | ⛪ {nm} | 📖 Tema: {reg['Tema_Culto']}")
            m_list = reg['Musicas'].split(", ")
            st.table(carregar_louvores()[carregar_louvores()['Musica'].isin(m_list)][["Musica", "Artista"]])
