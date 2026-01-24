import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse
import os

# 1. CONFIGURAÇÃO DA PÁGINA (Sempre o primeiro comando)
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

# 2. CSS AGRESSIVO PARA OCULTAR O SELO DO CLOUD, HEADER E FOOTER
st.markdown("""
    <style>
    /* Esconde o Header e o botão de Deploy */
    [data-testid="stHeader"], .stAppDeployButton, header {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* Esconde o Menu (3 linhas) e o Rodapé */
    #MainMenu, footer {
        visibility: hidden !important;
    }

    /* MATADOR DO BOTÃO FLUTUANTE (VIEWER BADGE) */
    div[class^="viewerBadge_container"], 
    div[class*="viewerBadge_container"],
    .viewerBadge_container__1QSob,
    [data-testid="stStatusWidget"],
    #stDecoration {
        display: none !important;
        visibility: hidden !important;
    }

    /* Esconde botões de ajuda e 'View Source' */
    button[title="View source"], 
    .st-emotion-cache-164784p,
    [data-testid="stHelpButton"] {
        display: none !important;
    }

    /* Ajusta o espaçamento do topo para o conteúdo subir */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÕES DO SISTEMA ---
SENHA_MESTRE = "shekina123" 
ARQUIVO_LOUVORES = "louvores.csv"
ARQUIVO_CULTOS = "cultos_salvos.csv"

# --- FUNÇÕES DE DADOS ---
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

# 3. BARRA LATERAL (SIDEBAR)
st.sidebar.markdown(f"## 🛡️ Grupo Shekiná")

# SEU INSTAGRAM PERSONALIZADO
link_instagram = "https://www.instagram.com/comunicandoigrejas/"
st.sidebar.markdown(f'''
    <a href="{link_instagram}" target="_blank">
        <button style="width: 100%; background-color: #E1306C; color: white; border: none; padding: 12px; border-radius: 10px; cursor: pointer; font-weight: bold; margin-bottom: 25px; box-shadow: 0px 4px 15px rgba(225, 48, 108, 0.4);">
            🔧 By Comunicando Igrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

perfil = st.sidebar.radio("Nível de Acesso:", ["Integrantes", "Líder (Gestão)"])

# 4. LÓGICA DO LÍDER
if perfil == "Líder (Gestão)":
    senha = st.sidebar.text_input("Senha:", type="password")
    if senha == SENHA_MESTRE:
        st.sidebar.success("Acesso Liberado")
        t1, t2, t3, t4 = st.tabs(["🎸 Repertório", "➕ Novo Louvor", "🌅 Devocional", "📜 Histórico"])
        
        df_musicas = carregar_dados()
        lista_oficial = sorted(df_musicas['Musica'].unique().tolist())

        with t1:
            c1, c2 = st.columns([2, 1])
            with c1:
                st.subheader("Buscar Louvores")
                b_n = st.text_input("Nome:").lower()
                cat = st.selectbox("Categoria:", ["Ver Todos", "Varões", "Mulheres", "Jovens", "Adoração", "Louvor", "Santa Ceia", "Missões", "Apelo", "Santidade"])
                df_f = df_musicas.copy()
                if cat != "Ver Todos":
                    df_f = df_f[df_f['Tags'].str.contains(cat.lower().replace("õ", "o"), na=False)]
                if b_n:
                    df_f = df_f[df_f['Musica_Busca'].str.contains(b_n)]
                
                sel = st.dataframe(df_f[['Musica', 'Artista', 'Tom']], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
                if 'carrinho' not in st.session_state: st.session_state.carrinho = []
                if sel.selection.rows:
                    for m in df_f.iloc[sel.selection.rows]['Musica'].tolist():
                        if m not in st.session_state.carrinho: st.session_state.carrinho.append(m)

            with c2:
                st.subheader("Publicar")
                nome_c = st.text_input("Culto:")
                data_c = st.date_input("Data:", date.today())
                carrinho_v = [m for m in st.session_state.carrinho if m in lista_oficial]
                final_list = st.multiselect("Setlist:", options=lista_oficial, default=carrinho_v)
                st.session_state.carrinho = final_list
                if st.button("💾 PUBLICAR"):
                    if nome_c and final_list:
                        novo = pd.DataFrame([[str(data_c), nome_c, ", ".join(final_list)]], columns=["Data_Culto", "Nome_Culto", "Musicas"])
                        pd.concat([carregar_cultos_salvos(), novo], ignore_index=True).to_csv(ARQUIVO_CULTOS, index=False)
                        st.success("✅ Publicado!")
                        msg = f"🙌 *Grupo Shekiná*\nCulto: *{nome_c}*\n🎶 *Lista:* {', '.join(final_list)}"
                        st.session_state.wa = f"https://wa.me/?text={urllib.parse.quote(msg)}"
                if 'wa' in st.session_state:
                    st.markdown(f'<a href="{st.session_state.wa}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 12px; border-radius: 5px; width: 100%; font-weight: bold;">📢 ENVIAR WHATSAPP</button></a>', unsafe_allow_html=True)

        with t2:
            st.subheader("Cadastrar Louvor")
            with st.form("cad"):
                nm, ar, tm = st.text_input("Música:"), st.text_input("Artista:"), st.text_input("Tom:")
                tg = st.multiselect("Tags:", ["Adoração", "Louvor", "Varões", "Mulheres", "Jovens", "Santa Ceia", "Missões", "Apelo", "Santidade"])
                if st.form_submit_button("✅ Adicionar"):
                    t_s = " ".join([t.lower().replace("õ", "o") for t in tg])
                    nova = pd.DataFrame([[nm, ar, tm, "Medio", t_s]], columns=["Musica", "Artista", "Tom", "Andamento", "Tags"])
                    pd.concat([pd.read_csv(ARQUIVO_LOUVORES), nova], ignore_index=True).to_csv(ARQUIVO_LOUVORES, index=False)
                    st.success("Adicionado!")
                    st.rerun()

        with t3:
            st.subheader("Devocional")
            tema = st.text_input("Tema:")
            if st.button("Gerar"):
                st.session_state.dev = f"🌅 *Devocional Shekiná*\n*Tema:* {tema}\n\nDeus abençoe!"
            if 'dev' in st.session_state:
                txt = st.text_area("Texto:", st.session_state.dev)
                st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(txt)}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px; border-radius: 5px;">📲 Enviar WhatsApp</button></a>', unsafe_allow_html=True)

        with t4:
            st.subheader("Histórico")
            h = carregar_cultos_salvos()
            if not h.empty:
                for i, r in h.sort_values(by="Data_Culto", ascending=False).iterrows():
                    with st.expander(f"📅 {r['Data_Culto']} - {r['Nome_Culto']}"):
                        st.write(f"🎶 {r['Musicas']}")

# 5. LÓGICA INTEGRANTES
else:
    st.header("📖 Repertório Oficial")
    h_i = carregar_cultos_salvos()
    if h_i.empty:
        st.info("Nenhum repertório publicado.")
    else:
        opc = (h_i['Data_Culto'].astype(str) + " | " + h_i['Nome_Culto']).tolist()[::-1]
        esc = st.selectbox("Escolha o Culto:", opc)
        if esc:
            d, n = esc.split(" | ")
            reg = h_i[(h_i['Data_Culto'].astype(str) == d) & (h_i['Nome_Culto'] == n)].iloc[0]
            m_l = reg['Musicas'].split(", ")
            df_v = carregar_dados()
            st.table(df_v[df_v['Musica'].isin(m_l)][['Musica', 'Artista', 'Tom']])
