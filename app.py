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
        df['Musica_Busca'] = df['Musica'].fillna('').astype(str).str.lower()
        return df
    except: return pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento", "Categoria", "Musica_Busca"])

def carregar_cultos():
    try:
        df = conn.read(worksheet="Cultos", ttl=0)
        df.columns = [c.strip() for c in df.columns]
        return df
    except: return pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Tema_Culto", "Musicas"])

# 4. LOGIN (igreja2026 / shekina123)
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    acesso = st.text_input("Senha da Equipe:", type="password")
    if st.button("Acessar"):
        if acesso in ["igreja2026", "shekina123"]:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 5. INTERFACE
perfil = st.sidebar.radio("Nível:", ["Integrantes", "Líder"])

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
            data_c = st.date_input("Data do Culto:", date.today())
        with c2:
            tema_c = st.text_input("Tema do Culto:")
            final_list = st.multiselect("Setlist Final:", options=sorted(df_l['Musica'].tolist()), 
                                        default=[m for m in st.session_state.cart if m in df_l['Musica'].tolist()])
            st.session_state.cart = final_list

        if nome_c and final_list:
            # Formatação de Data e Dia da Semana
            dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
            dia_nome = dias_semana[data_c.weekday()]
            data_formatada = data_c.strftime('%d-%m-%y')

            # Mensagem do WhatsApp (Emojis corrigidos com urllib.parse.quote)
            msg_wa = f"A paz do senhor grupo segue os louvores do culto *{nome_c}* .......\n\n"
            msg_wa += f"📅 *Data:* {data_formatada} ({dia_nome})\n"
            msg_wa += f"📖 *Tema:* {tema_c}\n\n"
            msg_wa += "🎶 *LOUVORES:*\n"
            for i, m in enumerate(final_list, 1): msg_wa += f"{i}. {m}\n"
            msg_wa += "\n🔧 _By Comunicando Igrejas_"
            
            col_save, col_wa = st.columns(2)
            with col_save:
                if st.button("💾 PUBLICAR E SALVAR"):
                    df_h = carregar_cultos()
                    # ORDEM DAS COLUNAS CORRIGIDA: Data, Nome, Tema, Musicas
                    novo_registro = pd.DataFrame([[data_formatada, nome_c, tema_c, ", ".join(final_list)]], 
                                                columns=["Data_Culto", "Nome_Culto", "Tema_Culto", "Musicas"])
                    conn.update(worksheet="Cultos", data=pd.concat([df_h, novo_registro], ignore_index=True))
                    st.success("✅ Registrado no histórico!")
            
            with col_wa:
                # O quote garante que emojis não virem triângulos
                link_wa = f"https://wa.me/?text={urllib.parse.quote(msg_wa)}"
                st.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">📢 ENVIAR NO WHATSAPP</button></a>', unsafe_allow_html=True)

    with t4:
        st.subheader("🌅 Devocional IA")
        if st.button("✨ Gerar Devocional de 200 palavras"):
            with st.spinner("IA escrevendo..."):
                prompt = f"Escreva um devocional de 200 palavras sobre {tema_c if tema_c else 'Adoração'} para o Grupo Shekiná. Use emojis como 🙏, 📖, ✨. Sem triângulos."
                res = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
                texto_ia = res.choices[0].message.content
                st.session_state.dev_ia = texto_ia
        
        if 'dev_ia' in st.session_state:
            st.write(st.session_state.dev_ia)
            link_dev = f"https://wa.me/?text={urllib.parse.quote(st.session_state.dev_ia + 'n\n🔧 _By Comunicando Igrejas_')}"
            st.markdown(f'<a href="{link_dev}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">📢 ENVIAR DEVOCIONAL</button></a>', unsafe_allow_html=True)

else:
    # ÁREA INTEGRANTES (v51)
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
