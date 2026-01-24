import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse
import os

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Grupo Shekiná - Gestão", page_icon="🎸", layout="wide")

# 2. OCULTAR MENU, FOOTER E BOTÕES DO TOPO (VISUAL LIMPO)
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stAppDeployButton {display:none;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- CONFIGURAÇÕES DO SISTEMA ---
SENHA_MESTRE = "shekina123" 
ARQUIVO_LOUVORES = "louvores.csv"
ARQUIVO_CULTOS = "cultos_salvos.csv"

# --- FUNÇÕES DE CARREGAMENTO DE DADOS ---
def carregar_dados():
    if not os.path.exists(ARQUIVO_LOUVORES):
        df_init = pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento", "Tags"])
        df_init.to_csv(ARQUIVO_LOUVORES, index=False)
        return df_init
    try:
        df = pd.read_csv(ARQUIVO_LOUVORES)
        df['Musica_Busca'] = df['Musica'].fillna('').astype(str).str.lower().str.strip()
        df['Tags'] = df['Tags'].fillna('').astype(str).str.lower().str.strip()
        return df
    except:
        return pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento", "Tags"])

def carregar_cultos_salvos():
    if os.path.exists(ARQUIVO_CULTOS):
        try:
            return pd.read_csv(ARQUIVO_CULTOS)
        except:
            pass
    return pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Musicas"])

# 3. INTERFACE PRINCIPAL
st.title("🛡️ Grupo Shekiná - Gestão de Louvor")

# BARRA LATERAL
st.sidebar.title("🔐 Acesso ao App")
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

        # --- ABA 1: MONTAR REPERTÓRIO ---
        with tab_repertorio:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("1. Localizar e Escolher Louvores")
                busca_n = st.text_input("🔍 Pesquisar por Nome:").lower()
                cat = st.selectbox("📂 Filtrar por Categoria:", ["Ver Todos", "Varões", "Mulheres", "Jovens", "Culto de Louvor", "Adoração", "Louvor", "Congregacional", "Missões", "Apelo", "Santidade", "Santa Ceia", "Agitados"])
                
                df_f = df_musicas.copy()
                if cat != "Ver Todos":
                    t_tag = cat.lower().replace("õ", "o").replace("ã", "a").replace("é", "e")
                    df_f = df_f[df_f['Tags'].str.contains(t_tag, na=False)]
                if busca_n:
                    df_f = df_f[df_f['Musica_Busca'].str.contains(busca_n)]

                # Seleção na tabela interativa
                sel = st.dataframe(df_f[['Musica', 'Artista', 'Tom']], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
                
                if 'carrinho' not in st.session_state: 
                    st.session_state.carrinho = []
                
                if sel.selection.rows:
                    itens_selecionados = df_f.iloc[sel.selection.rows]['Musica'].tolist()
                    for item in itens_selecionados:
                        if item not in st.session_state.carrinho:
                            st.session_state.carrinho.append(item)

            with col2:
                st.subheader("2. Finalizar e Publicar")
                nome_c = st.text_input("Nome do Culto:", placeholder="Ex: Culto de Jovens")
                data_c = st.date_input("Data:", date.today())
                
                # VALIDAÇÃO CRÍTICA: Evita o erro de API travando o multiselect
                carrinho_validado = [m for m in st.session_state.carrinho if m in lista_opcoes_oficial]
                
                final_list = st.multiselect(
                    "Músicas na Setlist:", 
                    options=lista_opcoes_oficial, 
                    default=carrinho_validado
                )
                st.session_state.carrinho = final_list

                if st.button("💾 PUBLICAR REPERTÓRIO"):
                    if nome_c and final_list:
                        novo_reg = pd.DataFrame([[str(data_c), nome_c, ", ".join(final_list)]], columns=["Data_Culto", "Nome_Culto", "Musicas"])
                        hist_db = carregar_cultos_salvos()
                        pd.concat([hist_db, novo_reg], ignore_index=True).to_csv(ARQUIVO_CULTOS, index=False)
                        
                        # Criar link do WhatsApp
                        msg_wa = f"🙌 *Grupo Shekiná - Novo Louvor!*\n\nCulto: *{nome_c}*\nData: {data_c.strftime('%d/%m')}\n\n🎶 *Lista:* {', '.join(final_list)}"
                        st.session_state.link_envio = f"https://wa.me/?text={urllib.parse.quote(msg_wa)}"
                        st.success("✅ Salvo no banco de dados!")
                    else:
                        st.error("Preencha o nome do culto e as músicas.")

                if 'link_envio' in st.session_state:
                    st.markdown(f'<a href="{st.session_state.link_envio}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 12px; border-radius: 5px; width: 100%; cursor: pointer; font-weight: bold;">📢 ENVIAR NO WHATSAPP</button></a>', unsafe_allow_html=True)

        # --- ABA 2: CADASTRAR NOVO LOUVOR ---
        with tab_cadastro:
            st.subheader("📝 Cadastrar Novo Louvor no Catálogo")
            with st.form("form_cadastro", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    nome_m = st.text_input("Nome da Música:")
                    artista_m = st.text_input("Artista/Ministério:")
                with c2:
                    tom_m = st.text_input("Tom Sugerido:")
                    tags_m = st.multiselect("Categorias:", ["Adoração", "Louvor", "Varões", "Mulheres", "Jovens", "Santa Ceia", "Agitados", "Missões", "Apelo", "Santidade", "Congregacional"])
                
                if st.form_submit_button("✅ Adicionar Louvor"):
                    if nome_m and artista_m:
                        t_str = " ".join([t.lower().replace("õ", "o").replace("ã", "a") for t in tags_m])
                        nova_musica = pd.DataFrame([[nome_m, artista_m, tom_m, "Medio", t_str]], columns=["Musica", "Artista", "Tom", "Andamento", "Tags"])
                        df_atual = pd.read_csv(ARQUIVO_LOUVORES)
                        pd.concat([df_atual, nova_musica], ignore_index=True).to_csv(ARQUIVO_LOUVORES, index=False)
                        st.success(f"'{nome_m}' adicionado!")
                        st.rerun()

        # --- ABA 3: DEVOCIONAL ---
        with tab_devocional:
            st.subheader("📖 Gerador de Devocional")
            tema_d = st.text_input("Tema do dia:")
            if st.button("Gerar Mensagem"):
                st.session_state.msg_dev = f"🌅 *Devocional Grupo Shekiná*\n\n*Tema:* {tema_d}\n\n📖 \"Lâmpada para os meus pés é a tua palavra...\"\n\n🙏 Tenha um dia abençoado!"
            if 'msg_dev' in st.session_state:
                txt_edit = st.text_area("Edite antes de enviar:", st.session_state.msg_dev, height=150)
                st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(txt_edit)}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px; border-radius: 5px;">📲 Enviar Devocional</button></a>', unsafe_allow_html=True)

        # --- ABA 4: HISTÓRICO DE CULTOS ---
        with tab_historico:
            st.subheader("📜 Histórico Cronológico")
            h_data = carregar_cultos_salvos()
            if not h_data.empty:
                h_ord = h_data.sort_values(by="Data_Culto", ascending=False)
                for i, r in h_ord.iterrows():
                    with st.expander(f"📅 {r['Data_Culto']} - {r['Nome_Culto']}"):
                        st.write(f"🎶 **Músicas:** {r['Musicas']}")

    elif senha != "" and senha != SENHA_MESTRE:
        st.sidebar.error("Senha Incorreta")

# 5. LÓGICA DOS INTEGRANTES (VISUALIZAÇÃO)
else:
    st.header("📖 Repertório Oficial da Equipe")
    h_integrante = carregar_cultos_salvos()
    
    if h_integrante.empty:
        st.info("Nenhum repertório publicado até o momento.")
    else:
        # Pega as opções de culto
        opcoes_c = (h_integrante['Data_Culto'].astype(str) + " | " + h_integrante['Nome_Culto']).tolist()[::-1]
        escolha_c = st.selectbox("Selecione o Culto para ver a lista:", opcoes_c)
        
        if escolha_c:
            data_s, nome_s = escolha_c.split(" | ")
            # Filtragem robusta
            registro = h_integrante[(h_integrante['Data_Culto'].astype(str) == data_s) & (h_integrante['Nome_Culto'] == nome_s)].iloc[0]
            nomes_m = registro['Musicas'].split(", ")
            
            # Busca os detalhes das músicas (tons)
            df_detalhes = carregar_dados()
            df_final_v = df_detalhes[df_detalhes['Musica'].isin(nomes_m)]
            
            st.markdown(f"### 📋 {nome_s}")
            st.table(df_final_v[['Musica', 'Artista', 'Tom']])
