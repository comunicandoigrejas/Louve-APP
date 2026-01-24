import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse
import os

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

# 2. CSS NINJA: ESCONDE TUDO DO STREAMLIT E AJUSTA O VISUAL
st.markdown("""
    <style>
    /* Ocultar elementos da plataforma */
    [data-testid="stHeader"], header, footer, .stAppDeployButton {
        display: none !important;
        visibility: hidden !important;
    }
    #MainMenu {visibility: hidden !important;}
    
    /* Tentativa agressiva contra o Viewer Badge (Selo do Cloud) */
    div[class^="viewerBadge"], [data-testid="stStatusWidget"], .viewerBadge_container__1QSob {
        display: none !important;
        opacity: 0 !important;
    }

    /* Ajuste de espaçamento interno */
    .block-container {
        padding-top: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÕES DE ARQUIVOS ---
SENHA_MESTRE = "shekina123" 
ARQUIVO_LOUVORES = "louvores.csv"
ARQUIVO_CULTOS = "cultos_salvos.csv"

# --- FUNÇÕES DE BANCO DE DADOS ---
def carregar_dados():
    if not os.path.exists(ARQUIVO_LOUVORES):
        pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento", "Tags"]).to_csv(ARQUIVO_LOUVORES, index=False)
    try:
        df = pd.read_csv(ARQUIVO_LOUVORES)
        df['Musica_Busca'] = df['Musica'].fillna('').astype(str).str.lower().str.strip()
        df['Tags'] = df['Tags'].fillna('').astype(str).str.lower().str.strip()
        return df
    except:
        return pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento", "Tags"])

def carregar_cultos_salvos():
    if os.path.exists(ARQUIVO_CULTOS):
        try: return pd.read_csv(ARQUIVO_CULTOS)
        except: pass
    return pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Musicas"])

# 3. SIDEBAR COM A SUA NOVA ASSINATURA
st.sidebar.markdown("# 🛡️ Grupo Shekiná")

# --- BOTÃO ASSINADO: BY COMUNICANDO IGREJAS ---
link_ig = "https://www.instagram.com/comunicandoigrejas/"
st.sidebar.markdown(f'''
    <a href="{link_ig}" target="_blank">
        <button style="width: 100%; background-color: #333333; color: white; border: 1px solid #555555; padding: 10px; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 25px; box-shadow: 0px 4px 10px rgba(0,0,0,0.2);">
            🔧 By Comunicando Igrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

perfil = st.sidebar.radio("Nível de Acesso:", ["Integrantes", "Líder (Gestão)"])

# 4. PAINEL DO LÍDER
if perfil == "Líder (Gestão)":
    senha = st.sidebar.text_input("Senha:", type="password")
    if senha == SENHA_MESTRE:
        st.sidebar.success("Líder Autenticado!")
        t1, t2, t3, t4 = st.tabs(["🎸 Repertório", "➕ Novo Louvor", "🌅 Devocional", "📜 Histórico"])
        
        df_m = carregar_dados()
        lista_of = sorted(df_m['Musica'].unique().tolist())

        with t1:
            c1, c2 = st.columns([2, 1])
            with c1:
                st.subheader("Filtrar Catálogo")
                busca = st.text_input("Pesquisar louvor:").lower()
                cat = st.selectbox("Estilo:", ["Ver Todos", "Varões", "Mulheres", "Jovens", "Adoração", "Louvor", "Santa Ceia", "Missões", "Apelo", "Santidade", "Agitados"])
                
                df_f = df_m.copy()
                if cat != "Ver Todos":
                    df_f = df_f[df_f['Tags'].str.contains(cat.lower().replace("õ", "o"), na=False)]
                if busca:
                    df_f = df_f[df_f['Musica_Busca'].str.contains(busca)]
                
                sel = st.dataframe(df_f[['Musica', 'Artista', 'Tom']], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
                
                if 'cart' not in st.session_state: st.session_state.cart = []
                if sel.selection.rows:
                    for m in df_f.iloc[sel.selection.rows]['Musica'].tolist():
                        if m not in st.session_state.cart: st.session_state.cart.append(m)

            with c2:
                st.subheader("Publicar")
                nome_c = st.text_input("Título do Culto:")
                data_c = st.date_input("Data:", date.today())
                
                cart_v = [m for m in st.session_state.cart if m in lista_of]
                final = st.multiselect("Setlist:", options=lista_of, default=cart_v)
                st.session_state.cart = final
                
                if st.button("💾 PUBLICAR AGORA"):
                    if nome_c and final:
                        reg = pd.DataFrame([[str(data_c), nome_c, ", ".join(final)]], columns=["Data_Culto", "Nome_Culto", "Musicas"])
                        pd.concat([carregar_cultos_salvos(), reg], ignore_index=True).to_csv(ARQUIVO_CULTOS, index=False)
                        st.success("✅ Repertório Online!")
                        msg = f"🙌 *Grupo Shekiná*\n📌 *Culto:* {nome_c}\n🎶 *Músicas:* {', '.join(final)}"
                        st.session_state.wa_link = f"https://wa.me/?text={urllib.parse.quote(msg)}"
                
                if 'wa_link' in st.session_state:
                    st.markdown(f'<a href="{st.session_state.wa_link}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 12px; border-radius: 5px; width: 100%; font-weight: bold; cursor: pointer;">📢 MANDAR PRO WHATSAPP</button></a>', unsafe_allow_html=True)

        with t2:
            st.subheader("Cadastrar no Banco")
            with st.form("add_louvor_v17"):
                nm, ar, tm = st.text_input("Música:"), st.text_input("Artista:"), st.text_input("Tom:")
                tg = st.multiselect("Tags:", ["Adoração", "Louvor", "Varões", "Mulheres", "Jovens", "Santa Ceia", "Missões", "Apelo", "Santidade", "Agitados"])
                if st.form_submit_button("✅ Salvar Música"):
                    tag_s = " ".join([t.lower().replace("õ", "o") for t in tg])
                    nova = pd.DataFrame([[nm, ar, tm, "Medio", tag_s]], columns=["Musica", "Artista", "Tom", "Andamento", "Tags"])
                    pd.concat([pd.read_csv(ARQUIVO_LOUVORES), nova], ignore_index=True).to_csv(ARQUIVO_LOUVORES, index=False)
                    st.success(f"'{nm}' adicionado!")
                    st.rerun()

        with t3:
            st.subheader("Devocional")
            tema = st.text_input("Tema:")
            if st.button("Gerar"):
                st.session_state.dev_msg = f"🌅 *Devocional - Shekiná*\n📍 *Tema:* {tema}\n\n🔧 By Comunicando Igrejas"
            if 'dev_msg' in st.session_state:
                txt = st.text_area("Mensagem:", st.session_state.dev_msg, height=150)
                st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(txt)}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px; border-radius: 5px; width: 100%;">📲 Enviar WhatsApp</button></a>', unsafe_allow_html=True)

        with t4:
            st.subheader("Histórico")
            h = carregar_cultos_salvos()
            if not h.empty:
                for i, r in h.sort_values(by="Data_Culto", ascending=False).iterrows():
                    with st.expander(f"📅 {r['Data_Culto']} - {r['Nome_Culto']}"):
                        st.write(f"🎶 **Setlist:** {r['Musicas']}")

# 5. ÁREA DOS INTEGRANTES
else:
    st.header("📖 Repertório Oficial")
    hist = carregar_cultos_salvos()
    if hist.empty:
        st.info("Nenhum repertório publicado.")
    else:
        opcoes = (hist['Data_Culto'].astype(str) + " | " + hist['Nome_Culto']).tolist()[::-1]
        escolha = st.selectbox("Escolha o Culto:", opcoes)
        if escolha:
            d, n = escolha.split(" | ")
            reg = hist[(hist['Data_Culto'].astype(str) == d) & (hist['Nome_Culto'] == n)].iloc[0]
            musicas = reg['Musicas'].split(", ")
            df_v = carregar_dados()
            st.table(df_v[df_v['Musica'].isin(musicas)][['Musica', 'Artista', 'Tom']])
