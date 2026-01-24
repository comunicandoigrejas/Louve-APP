import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse
import os

# Configuração da Página
st.set_page_config(page_title="Grupo Shekiná - Gestão", page_icon="🎸", layout="wide")

# --- CONFIGURAÇÕES ---
SENHA_MESTRE = "shekina123" 
ARQUIVO_LOUVORES = "louvores.csv"
ARQUIVO_CULTOS = "cultos_salvos.csv"

# 1. FUNÇÕES DE DADOS (Com limpeza de Cache para garantir visualização)
def carregar_dados():
    try:
        df = pd.read_csv(ARQUIVO_LOUVORES)
        df['Musica_Busca'] = df['Musica'].fillna('').str.lower().str.strip()
        df['Tags'] = df['Tags'].fillna('').str.lower().str.strip()
        return df
    except:
        return pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento", "Tags"])

def carregar_cultos_salvos():
    if os.path.exists(ARQUIVO_CULTOS):
        return pd.read_csv(ARQUIVO_CULTOS)
    return pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Musicas"])

# 2. INTERFACE
st.title("🛡️ Grupo Shekiná - Gestão de Louvor")

# BARRA LATERAL
st.sidebar.title("🔐 Acesso")
perfil = st.sidebar.radio("Selecione seu perfil:", ["Integrantes (Visualização)", "Líder (Gestão)"])

# 3. LÓGICA DO LÍDER
if perfil == "Líder (Gestão)":
    senha = st.sidebar.text_input("Senha de Líder:", type="password")
    if senha == SENHA_MESTRE:
        st.sidebar.success("Acesso Liberado")
        
        tab_repertorio, tab_cadastro, tab_devocional, tab_historico = st.tabs([
            "🎸 Montar Repertório", "➕ Novo Louvor", "🌅 Devocional", "📜 Histórico de Cultos"
        ])
        
        df_musicas = carregar_dados()

        with tab_repertorio:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("1. Selecionar Músicas")
                busca_n = st.text_input("🔍 Nome da Música:").lower()
                cat = st.selectbox("📂 Categoria:", ["Ver Todos", "Varões", "Mulheres", "Jovens", "Culto de Louvor", "Adoração", "Louvor", "Congregacional", "Missões", "Apelo", "Santidade", "Santa Ceia", "Agitados"])
                
                df_f = df_musicas.copy()
                if cat != "Ver Todos":
                    t_tag = cat.lower().replace("õ", "o").replace("ã", "a").replace("é", "e")
                    df_f = df_f[df_f['Tags'].str.contains(t_tag, na=False)]
                if busca_n:
                    df_f = df_f[df_f['Musica_Busca'].str.contains(busca_n)]

                sel = st.dataframe(df_f[['Musica', 'Artista', 'Tom']], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
                
                if 'carrinho' not in st.session_state: st.session_state.carrinho = []
                if sel.selection.rows:
                    itens = df_f.iloc[sel.selection.rows]['Musica'].tolist()
                    for i in itens:
                        if i not in st.session_state.carrinho: st.session_state.carrinho.append(i)

            with col2:
                st.subheader("2. Salvar e Notificar")
                nome_c = st.text_input("Nome do Culto:", key="nome_culto_input")
                data_c = st.date_input("Data:", date.today())
                
                final_list = st.multiselect("Setlist:", options=df_musicas['Musica'].tolist(), default=st.session_state.carrinho)
                st.session_state.carrinho = final_list

                if st.button("💾 PUBLICAR PARA A EQUIPE"):
                    if nome_c and final_list:
                        novo_culto = pd.DataFrame([[str(data_c), nome_c, ", ".join(final_list)]], columns=["Data_Culto", "Nome_Culto", "Musicas"])
                        hist = carregar_cultos_salvos()
                        pd.concat([hist, novo_culto]).to_csv(ARQUIVO_CULTOS, index=False)
                        st.success("✅ Salvo com Sucesso!")
                        
                        # Preparar Mensagem WhatsApp
                        msg = f"🙌 *Grupo Shekiná - Novo Louvor!*\n\nCulto: *{nome_c}*\nData: {data_c.strftime('%d/%m')}\n\n🎶 *Lista:* {', '.join(final_list)}"
                        st.session_state.link_whatsapp = f"https://wa.me/?text={urllib.parse.quote(msg)}"
                    else:
                        st.error("Preencha o nome e as músicas!")

                # Botão WhatsApp aparece aqui se o link existir
                if 'link_whatsapp' in st.session_state:
                    st.markdown(f'<a href="{st.session_state.link_whatsapp}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 12px; border-radius: 5px; width: 100%; cursor: pointer; font-weight: bold;">📢 ENVIAR NO WHATSAPP</button></a>', unsafe_allow_html=True)

        with tab_cadastro:
            st.subheader("📝 Cadastrar Novo Louvor")
            with st.form("add_music"):
                n_m = st.text_input("Música:")
                n_a = st.text_input("Artista:")
                n_t = st.text_input("Tom:")
                n_tags = st.multiselect("Tags:", ["Adoração", "Louvor", "Varões", "Mulheres", "Jovens", "Santa Ceia", "Agitados"])
                if st.form_submit_button("Adicionar"):
                    t_str = " ".join([t.lower().replace("õ", "o") for t in n_tags])
                    nova_r = pd.DataFrame([[n_m, n_a, n_t, "Medio", t_str]], columns=["Musica", "Artista", "Tom", "Andamento", "Tags"])
                    pd.concat([carregar_dados().drop(columns=['Musica_Busca']), nova_r]).to_csv(ARQUIVO_LOUVORES, index=False)
                    st.success("Adicionado!")
                    st.rerun()

        with tab_historico:
            st.subheader("📜 Histórico")
            h = carregar_cultos_salvos()
            if not h.empty:
                st.dataframe(h.sort_values(by="Data_Culto", ascending=False), use_container_width=True, hide_index=True)

# 4. LÓGICA INTEGRANTES
else:
    st.header("📖 Repertório Oficial - Grupo Shekiná")
    h = carregar_cultos_salvos()
    
    if h.empty:
        st.info("Nenhum culto publicado.")
    else:
        # Criar a lista de opções para o selectbox
        opcoes = (h['Data_Culto'].astype(str) + " | " + h['Nome_Culto']).tolist()[::-1]
        escolha = st.selectbox("Selecione o Culto:", opcoes)
        
        if escolha:
            dt_s, nm_s = escolha.split(" | ")
            # Filtragem exata
            linha = h[(h['Data_Culto'].astype(str) == dt_s) & (h['Nome_Culto'] == nm_s)].iloc[0]
            m_nomes = linha['Musicas'].split(", ")
            
            # Carrega dados das músicas para pegar os tons
            df_m = carregar_dados()
            df_v = df_m[df_m['Musica'].isin(m_nomes)]
            
            st.markdown(f"### 📋 Lista: {nm_s}")
            st.table(df_v[['Musica', 'Artista', 'Tom']])
