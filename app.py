import streamlit as st
from streamlit_gsheets import GSheetsConnection
from openai import OpenAI
import pandas as pd
from datetime import date
import urllib.parse

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

# 2. INICIALIZAÇÃO SEGURA
try:
    openai_key = st.secrets.get("OPENAI_API_KEY")
    client = OpenAI(api_key=openai_key) if openai_key else None
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    st.error("Erro crítico: Verifique os Secrets (OpenAI e Google JSON).")
    st.stop()

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
    prompt = f"Escreva um devocional de 200 palavras para o Grupo Shekiná sobre: {tema}. Use emojis simples (🙏, 📖, ✨). Inclua versículo e oração."
    try:
        res = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
        return res.choices[0].message.content
    except: return "Erro ao gerar devocional com a IA."

# 4. SIDEBAR E IDENTIDADE
st.sidebar.markdown("# 🛡️ Grupo Shekiná")
st.sidebar.markdown(f'''
    <a href="https://www.instagram.com/comunicandoigrejas/" target="_blank">
        <button style="width: 100%; background-color: #333333; color: white; border: 1px solid #555555; padding: 10px; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 20px;">
            🔧 By Comunicando Igrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

# 5. LOGIN DO SISTEMA (Gateway)
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔑 Acesso ao Sistema")
    acesso = st.text_input("Digite a senha da equipe:", type="password")
    if st.button("Entrar"):
        if acesso in ["igreja2026", "shekina123"]:
            st.session_state.auth = True
            st.rerun()
        else: st.error("Senha incorreta!")
    st.stop()

# 6. INTERFACE DE NÍVEIS
perfil = st.sidebar.radio("Selecione seu nível:", ["Integrantes", "Líder"])

# --- ÁREA DO LÍDER ---
if perfil == "Líder":
    chave_mestre = st.sidebar.text_input("Chave Mestre:", type="password")
    if chave_mestre == "shekina123":
        df_l = carregar_louvores()
        t1, t2, t3, t4, t5 = st.tabs(["🎸 Montar Setlist", "➕ Cadastrar", "🗑️ Excluir", "📜 Histórico", "🌅 Devocional IA"])

        with t1:
            st.subheader("Seleção de Louvores")
            busca = st.text_input("🔍 Pesquisar louvor (digite para filtrar):").lower()
            df_f = df_l[df_l['Musica_Busca'].str.contains(busca)] if busca else df_l
            sel = st.dataframe(df_f[["Musica", "Artista", "Tom"]], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
            
            if 'cart' not in st.session_state: st.session_state.cart = []
            if sel.selection.rows:
                for m in df_f.iloc[sel.selection.rows]['Musica'].tolist():
                    if m not in st.session_state.cart: st.session_state.cart.append(m)

            st.write("---")
            c1, c2 = st.columns(2)
            with c1:
                nome_c = st.text_input("Nome do Culto:", value="Culto de Celebração")
                data_c = st.date_input("Data do Culto:", date.today())
            with c2:
                tema_c = st.text_input("Tema da Mensagem:")
                final_list = st.multiselect("Setlist Final:", options=sorted(df_l['Musica'].tolist()) if not df_l.empty else [], 
                                            default=[m for m in st.session_state.cart if m in df_l['Musica'].tolist()])
                st.session_state.cart = final_list

            if nome_c and final_list:
                # Formatação solicitada: dd-mm-aa e dia da semana
                dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
                msg_wa = f"A paz do senhor grupo segue os louvores do culto *{nome_c}* .......\n\n"
                msg_wa += f"📅 *Data:* {data_c.strftime('%d-%m-%y')} ({dias[data_c.weekday()]})\n"
                msg_wa += f"📖 *Tema:* {tema_c}\n\n🎶 *LOUVORES:*\n"
                for i, m in enumerate(final_list, 1): msg_wa += f"{i}. {m}\n"
                msg_wa += "\n🔧 _By Comunicando Igrejas_"
                
                col_save, col_wa = st.columns(2)
                with col_save:
                    if st.button("💾 PUBLICAR PARA EQUIPE"):
                        df_h = carregar_cultos()
                        novo = pd.DataFrame([[str(data_c), nome_c, tema_c, ", ".join(final_list)]], columns=df_h.columns)
                        conn.update(worksheet="Cultos", data=pd.concat([df_h, novo], ignore_index=True))
                        st.success("✅ Publicado no Google Sheets!")
                with col_wa:
                    link = f"https://wa.me/?text={urllib.parse.quote(msg_wa)}"
                    st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">📢 WHATSAPP</button></a>', unsafe_allow_html=True)

        with t2:
            st.subheader("Novo Cadastro")
            with st.form("cad", clear_on_submit=True):
                m, a, t = st.text_input("Música:"), st.text_input("Artista:"), st.text_input("Tom:")
                cat = st.multiselect("Categorias:", ["Adoração", "Júbilo", "Avivamento", "Congregacional"])
                if st.form_submit_button("Salvar na Nuvem"):
                    if m and a:
                        nova = pd.DataFrame([[m, a, t, "Médio", ", ".join(cat)]], columns=["Musica", "Artista", "Tom", "Andamento", "Categoria"])
                        conn.update(worksheet="Louvores", data=pd.concat([df_l.drop(columns=['Musica_Busca'], errors='ignore'), nova], ignore_index=True))
                        st.success("Música cadastrada!")
        
        with t3:
            st.subheader("Excluir Louvor")
            m_ex = st.selectbox("Selecione:", [""] + sorted(df_l['Musica'].tolist()))
            if m_ex and st.button("Confirmar Exclusão"):
                conn.update(worksheet="Louvores", data=df_l[df_l['Musica'] != m_ex].drop(columns=['Musica_Busca'], errors='ignore'))
                st.rerun()

        with t4:
            st.subheader("Histórico")
            st.dataframe(carregar_cultos(), use_container_width=True, hide_index=True)

        with t5:
            st.subheader("🌅 Devocional IA")
            tema_dev = st.selectbox("Foco:", ["Unidade", "Santidade", "Gratidão"])
            if st.button("✨ Gerar Devocional"):
                with st.spinner("IA escrevendo..."):
                    res = gerar_devocional_ia(tema_dev)
                    st.session_state.dev_res = res
            if 'dev_res' in st.session_state:
                st.write(st.session_state.dev_res)
                link_dev = f"https://wa.me/?text={urllib.parse.quote(st.session_state.dev_res + 'n\n🔧 _By Comunicando Igrejas_')}"
                st.markdown(f'<a href="{link_dev}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:8px; font-weight:bold; cursor:pointer;">📢 ENVIAR DEVOCIONAL</button></a>', unsafe_allow_html=True)
    else: st.warning("Digite a Chave Mestre na barra lateral.")

# --- ÁREA DOS INTEGRANTES ---
else:
    st.header("📖 Repertório Oficial")
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
            df_full = carregar_louvores()
            st.table(df_full[df_full['Musica'].isin(m_list)][["Musica", "Artista", "Tom"]])
