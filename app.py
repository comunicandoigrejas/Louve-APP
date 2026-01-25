import streamlit as st
from streamlit_gsheets import GSheetsConnection
from openai import OpenAI
import pandas as pd
from datetime import date
import urllib.parse

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

# 2. BRANDING NA SIDEBAR (Sempre visível, no topo)
st.sidebar.markdown("# 🛡️ Grupo Shekiná")
st.sidebar.markdown(f'''
    <a href="https://www.instagram.com/comunicandoigrejas/" target="_blank">
        <button style="width: 100%; background-color: #333333; color: white; border: 1px solid #555555; padding: 12px; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 20px;">
            🔧 By Comunicando Igrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

# 3. INICIALIZAÇÃO
try:
    openai_key = st.secrets.get("OPENAI_API_KEY")
    client = OpenAI(api_key=openai_key) if openai_key else None
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    st.error("Erro nos Secrets. Verifique as chaves da OpenAI e Google.")
    st.stop()

# 4. LOGIN DO SISTEMA
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔑 Acesso ao Sistema")
    acesso = st.text_input("Senha da equipe:", type="password")
    if st.button("Entrar"):
        if acesso in ["igreja2026", "shekina123"]:
            st.session_state.auth = True
            st.rerun()
        else: st.error("Senha incorreta!")
    st.stop()

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
        return df
    except: return pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Tema_Culto", "Musicas"])

# 5. INTERFACE DE NÍVEIS
perfil = st.sidebar.radio("Nível:", ["Integrantes", "Líder"])

if perfil == "Líder":
    chave_mestre = st.sidebar.text_input("Chave Mestre:", type="password")
    if chave_mestre == "shekina123":
        df_l = carregar_louvores()
        t1, t2, t3, t4, t5 = st.tabs(["🎸 Setlist", "➕ Cadastrar", "🗑️ Excluir", "📜 Histórico", "🌅 Devocional IA"])

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
                nome_c = st.text_input("Tipo de Culto (Nome):")
                data_c = st.date_input("Data do Culto:", date.today())
            with c2:
                tema_c = st.text_input("Tema do Culto:")
                final_list = st.multiselect("Setlist Final:", options=sorted(df_l['Musica'].tolist()), 
                                            default=[m for m in st.session_state.cart if m in df_l['Musica'].tolist()])
                st.session_state.cart = final_list

            if nome_c and final_list:
                dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
                data_f = data_c.strftime('%d-%m-%y')
                dia_nome = dias[data_c.weekday()]

                # CONSTRUÇÃO DA MENSAGEM - CORREÇÃO DE EMOJIS
                msg_wa = f"A paz do senhor grupo segue os louvores do culto *{nome_c}* .......\n\n"
                msg_wa += f"📅 *Data:* {data_f} ({dia_nome})\n"
                msg_wa += f"📖 *Tema:* {tema_c}\n\n"
                msg_wa += "🎶 *LOUVORES:*\n"
                for i, m in enumerate(final_list, 1):
                    msg_wa += f"{i}. {m}\n"
                msg_wa += "\n🔧 _By Comunicando Igrejas_"
                
                col_save, col_wa = st.columns(2)
                with col_save:
                    if st.button("💾 PUBLICAR E SALVAR"):
                        df_h = carregar_cultos()
                        # Garantindo a ordem exata das colunas para não salvar trocado
                        novo = pd.DataFrame([[data_f, nome_c, tema_c, ", ".join(final_list)]], 
                                            columns=["Data_Culto", "Nome_Culto", "Tema_Culto", "Musicas"])
                        conn.update(worksheet="Cultos", data=pd.concat([df_h, novo], ignore_index=True))
                        st.success("✅ Histórico registrado corretamente!")
                
                with col_wa:
                    # O segredo para o emoji colorido está no urllib.parse.quote
                    link_wa = f"https://wa.me/?text={urllib.parse.quote(msg_wa)}"
                    st.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">📢 ENVIAR WHATSAPP</button></a>', unsafe_allow_html=True)

        with t4:
            st.subheader("📜 Histórico de Cultos")
            st.dataframe(carregar_cultos().iloc[::-1], use_container_width=True, hide_index=True)

        with t5:
            st.subheader("🌅 Devocional IA")
            if st.button("✨ Gerar Mensagem"):
                with st.spinner("Criando devocional..."):
                    p = f"Escreva um devocional de 200 palavras sobre {tema_c if tema_c else 'Adoração'}. Use emojis: 🙏, ✨, 📖. Sem triângulos pretos."
                    res = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": p}])
                    st.session_state.dev_txt = res.choices[0].message.content
            if 'dev_txt' in st.session_state:
                st.write(st.session_state.dev_txt)
                link_dev = f"https://wa.me/?text={urllib.parse.quote(st.session_state.dev_txt + 'n\n🔧 _By Comunicando Igrejas_')}"
                st.markdown(f'<a href="{link_dev}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:8px; font-weight:bold; cursor:pointer;">📢 ENVIAR DEVOCIONAL</button></a>', unsafe_allow_html=True)
    
    # Abas t2 e t3 (Cadastro/Exclusão) seguem o padrão funcional anterior...
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
            df_full = carregar_louvores()
            st.table(df_full[df_full['Musica'].isin(m_list)][["Musica", "Artista"]])
