import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse
import os

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Grupo Shekiná - Gestão", page_icon="🎸", layout="wide")

# 2. OCULTAR TODOS OS ELEMENTOS DO STREAMLIT (REFORÇADO)
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            header {visibility: hidden !important;}
            .stAppDeployButton {display:none !important;}
            [data-testid="stStatusWidget"] {display:none !important;}
            [data-testid="stHeader"] {display:none !important;}
            #stDecoration {display:none !important;}
            button[title="View source"] {display:none !important;}
            /* Esconde o botão de ajuda flutuante */
            .st-emotion-cache-164784p {display: none !important;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- CONFIGURAÇÕES DO SISTEMA ---
SENHA_MESTRE = "shekina123" 
ARQUIVO_LOUVORES = "louvores.csv"
ARQUIVO_CULTOS = "cultos_salvos.csv"

# --- FUNÇÕES DE CARREGAMENTO ---
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

# 3. INTERFACE E MENU LATERAL
st.sidebar.title("🛡️ Grupo Shekiná")

# --- SEU INSTAGRAM PERSONALIZADO ---
link_instagram = "https://www.instagram.com/comunicandoigrejas/"
st.sidebar.markdown(f'''
    <a href="{link_instagram}" target="_blank">
        <button style="width: 100%; background-color: #E1306C; color: white; border: none; padding: 12px; border-radius: 10px; cursor: pointer; font-weight: bold; margin-bottom: 20px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
            📸 Siga @comunicandoigrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

perfil = st.sidebar.radio("Selecione seu perfil:", ["Integrantes (Visualização)", "Líder (Gestão)"])

# 4. LÓGICA DO LÍDER (GESTÃO)
if perfil == "Líder (Gestão)":
    senha = st.sidebar.text_input("Senha de Líder:", type="password")
    if senha == SENHA_MESTRE:
        st.sidebar.success("Líder Autenticado")
        
        tab_repertorio, tab_cadastro, tab_devocional, tab_historico = st.tabs([
            "🎸 Montar Repertório", "➕ Novo Louvor", "🌅 Devocional", "📜 Histórico de Cultos"
        ])
        
        df_musicas = carregar_dados()
        lista_opcoes_oficial = sorted(df_musicas['Musica'].unique().tolist())

        with tab_repertorio:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("1. Localizar Louvores")
                busca_n = st.text_input("🔍 Nome da Música:").lower()
                cat = st.selectbox("📂 Categoria:", ["Ver Todos", "Varões", "Mulheres", "Jovens", "Adoração", "Louvor", "Santa Ceia", "Missões", "Apelo", "Santidade"])
                
                df_f = df_musicas.copy()
                if cat != "Ver Todos":
                    t_tag = cat.lower().replace("õ", "o").replace("ã", "a")
                    df_f = df_f[df_f['Tags'].str.contains(t_tag, na=False)]
                if busca_n:
                    df_f = df_f[df_f['Musica_Busca'].str.contains(busca_n)]

                sel = st.dataframe(df_f[['Musica', 'Artista', 'Tom']], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
                
                if 'carrinho' not in st.session_state: st.session_state.carrinho = []
                if sel.selection.rows:
                    itens = df_f.iloc[sel.selection.rows]['Musica'].tolist()
                    for m in itens:
                        if m not in st.session_state.carrinho: st.session_state.carrinho.append(m)

            with col2:
                st.subheader("2. Salvar e Notificar")
                nome_c = st.text_input("Nome do Culto:", key="nome_final_input")
                data_c = st.date_input("Data:", date.today())
                
                # TRAVA DE SEGURANÇA PARA O ERRO DA IMAGEM
                carrinho_validado = [m for m in st.session_state.carrinho if m in lista_opcoes_oficial]
                
                final_list = st.multiselect("Músicas na Setlist:", options=lista_opcoes_oficial, default=carrinho_validado)
                st.session_state.carrinho = final_list

                if st.button("💾 PUBLICAR REPERTÓRIO"):
                    if nome_c and final_list:
                        novo_reg = pd.DataFrame([[str(data_c), nome_c, ", ".join(final_list)]], columns=["Data_Culto", "Nome_Culto", "Musicas"])
                        pd.concat([carregar_cultos_salvos(), novo_reg], ignore_index=True).to_csv(ARQUIVO_CULTOS, index=False)
                        st.success("✅ Salvo com sucesso!")
                        msg_wa = f"🙌 *Grupo Shekiná*\nCulto: *{nome_c}*\n🎶 *Lista:* {', '.join(final_list)}"
                        st.session_state.link_wa = f"https://wa.me/?text={urllib.parse.quote(msg_wa)}"
                    else:
                        st.error("Preencha o nome e as músicas.")

                if 'link_wa' in st.session_state:
                    st.markdown(f'<a href="{st.session_state.link_wa}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 12px; border-radius: 5px; width: 100%; cursor: pointer; font-weight: bold;">📢 ENVIAR NO WHATSAPP</button></a>', unsafe_allow_html=True)

        with tab_cadastro:
            st.subheader("📝 Cadastrar Nova Música")
            with st.form("form_cad_shekina", clear_on_submit=True):
                n_m = st.text_input("Nome:")
                n_a = st.text_input("Artista:")
                n_t = st.text_input("Tom:")
                n_tags = st.multiselect("Tags:", ["Adoração", "Louvor", "Varões", "Mulheres", "Jovens", "Santa Ceia", "Missões", "Apelo", "Santidade"])
                if st.form_submit_button("✅ Adicionar"):
                    if n_m and n_a:
                        t_str = " ".join([t.lower().replace("õ", "o") for t in n_tags])
                        nova_mus = pd.DataFrame([[n_m, n_a, n_t, "Medio", t_str]], columns=["Musica", "Artista", "Tom", "Andamento", "Tags"])
                        pd.concat([carregar_dados().drop(columns=['Musica_Busca']), nova_mus], ignore_index=True).to_csv(ARQUIVO_LOUVORES, index=False)
                        st.success(f"'{n_m}' adicionado!")
                        st.rerun()

        with tab_historico:
            st.subheader("📜 Histórico")
            h = carregar_cultos_salvos()
            if not h.empty:
                for i, r in h.sort_values(by="Data_Culto", ascending=False).iterrows():
                    with st.expander(f"📅 {r['Data_Culto']} - {r['Nome_Culto']}"):
                        st.write(f"🎶 {r['Musicas']}")

# 5. LÓGICA INTEGRANTES
else:
    st.header("📖 Repertório Oficial")
    h_int = carregar_cultos_salvos()
    if h_int.empty:
        st.info("Nenhum repertório publicado.")
    else:
        opc = (h_int['Data_Culto'].astype(str) + " | " + h_int['Nome_Culto']).tolist()[::-1]
        esc = st.selectbox("Selecione o Culto:", opc)
        if esc:
            try:
                d_s, n_s = esc.split(" | ")
                reg = h_int[(h_int['Data_Culto'].astype(str) == d_s) & (h_int['Nome_Culto'] == n_s)].iloc[0]
                m_l = reg['Musicas'].split(", ")
                df_v = carregar_dados()
                st.table(df_v[df_v['Musica'].isin(m_l)][['Musica', 'Artista', 'Tom']])
            except:
                st.error("Selecione um culto válido.")
