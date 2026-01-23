import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse

# Configuração da Página
st.set_page_config(page_title="Grupo Shekiná - Gestão", page_icon="🎸", layout="wide")

# --- CONFIGURAÇÕES ---
SENHA_MESTRE = "shekina123" 
ARQUIVO_CULTOS = "cultos_salvos.csv"

# 1. CARREGAR DADOS
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv('louvores.csv')
        df['Musica_Busca'] = df['Musica'].fillna('').str.lower().str.strip()
        df['Tags'] = df['Tags'].fillna('').str.lower().str.strip()
        return df
    except:
        return pd.DataFrame()

def carregar_cultos_salvos():
    try:
        df = pd.read_csv(ARQUIVO_CULTOS)
        return df
    except:
        return pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Musicas"])

df_musicas = carregar_dados()

# 2. TÍTULO
st.title("🛡️ Grupo Shekiná - Gestão de Louvor")

# 3. BARRA LATERAL
st.sidebar.title("🔐 Acesso")
perfil = st.sidebar.radio("Selecione seu perfil:", ["Integrantes (Visualização)", "Líder (Gestão)"])

# 4. LÓGICA DO LÍDER
if perfil == "Líder (Gestão)":
    senha = st.sidebar.text_input("Senha de Líder:", type="password")
    if senha == SENHA_MESTRE:
        st.sidebar.success("Acesso Liberado")
        
        # NOVAS ABAS (Incluindo Histórico)
        tab_repertorio, tab_devocional, tab_historico = st.tabs(["🎸 Montar Repertório", "🌅 Devocional", "📜 Histórico de Uso"])
        
        # --- ABA 1: REPERTÓRIO (Já existente) ---
        with tab_repertorio:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("1. Localizar Louvores")
                col_b1, col_b2 = st.columns([1, 1])
                with col_b1: busca_nome = st.text_input("🔍 Nome da Música:")
                with col_b2: categoria = st.selectbox("📂 Categoria:", ["Ver Todos", "Varões", "Mulheres", "Jovens", "Culto de Louvor", "Adoração", "Louvor", "Congregacional", "Missões", "Apelo", "Santidade", "Santa Ceia", "Agitados"])

                df_exibir = df_musicas.copy()
                if categoria != "Ver Todos":
                    termo_tag = categoria.lower().replace("õ", "o").replace("ã", "a").replace("é", "e")
                    df_exibir = df_exibir[df_exibir['Tags'].str.contains(termo_tag, na=False)]
                if busca_nome:
                    df_exibir = df_exibir[df_exibir['Musica_Busca'].str.contains(busca_nome.lower())]

                selecao = st.dataframe(df_exibir[['Musica', 'Artista', 'Tom']], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
                if 'carrinho' not in st.session_state: st.session_state.carrinho = []
                if selecao.selection.rows:
                    novas = df_exibir.iloc[selecao.selection.rows]['Musica'].tolist()
                    for m in novas:
                        if m not in st.session_state.carrinho: st.session_state.carrinho.append(m)

            with col2:
                st.subheader("2. Salvar Setlist")
                nome_c = st.text_input("Nome do Culto:")
                data_c = st.date_input("Data:", date.today())
                lista_final = st.multiselect("Setlist:", options=df_musicas['Musica'].tolist(), default=st.session_state.carrinho)
                st.session_state.carrinho = lista_final

                if st.button("💾 Publicar Repertório"):
                    if nome_c and lista_final:
                        novos_dados = pd.DataFrame([[data_c, nome_c, ", ".join(lista_final)]], columns=["Data_Culto", "Nome_Culto", "Musicas"])
                        pd.concat([carregar_cultos_salvos(), novos_dados]).to_csv(ARQUIVO_CULTOS, index=False)
                        st.success("Publicado!")
                        msg_l = f"🙌 *Grupo Shekiná - Repertório*\nCulto: *{nome_c}*\n🎶 *Lista:* {', '.join(lista_final)}"
                        st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(msg_l)}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px; border-radius: 5px; width: 100%;">📢 Enviar para Equipe</button></a>', unsafe_allow_html=True)

        # --- ABA 2: DEVOCIONAL ---
        with tab_devocional:
            st.subheader("📖 Gerador de Devocional Shekiná")
            tema_dev = st.text_input("Tema do dia:")
            if st.button("✨ Gerar Mensagem"):
                st.session_state.dev_txt = f"🌅 *Devocional - Grupo Shekiná*\n\n*Tema:* {tema_dev}\n\n📖 \"Lâmpada para os meus pés é tua palavra...\" (Sl 119:105)\n\n🙏 Ministrar louvor é mais que música, é entrega!"
            if 'dev_txt' in st.session_state:
                txt = st.text_area("Editar:", st.session_state.dev_txt, height=150)
                st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(txt)}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px; border-radius: 5px;">📲 Enviar Devocional</button></a>', unsafe_allow_html=True)

        # --- ABA 3: HISTÓRICO DE CULTOS (Visualização por Data) ---
        with tab_historico:
            st.subheader("📜 Registro Geral de Cultos")
            historico_db = carregar_cultos_salvos()
            
            if historico_db.empty:
                st.info("Nenhum culto registrado no histórico ainda.")
            else:
                # Ordenar para que o mais recente apareça no topo
                historico_ordenado = historico_db.sort_values(by="Data_Culto", ascending=False)
                
                for index, row in historico_ordenado.iterrows():
                    # Criar um "Card" para cada culto
                    with st.expander(f"📅 {row['Data_Culto']} - {row['Nome_Culto']}"):
                        st.markdown(f"**Data:** {row['Data_Culto']}")
                        st.markdown(f"**Tipo de Culto:** {row['Nome_Culto']}")
                        st.markdown("**Louvores Cantados:**")
                        
                        # Transforma a string de músicas em uma lista para exibir em tópicos
                        lista_musicas = row['Musicas'].split(", ")
                        for musica in lista_musicas:
                            st.write(f"🎶 {musica}")
                        
                        # Botão extra caso queira copiar esse histórico antigo
                        msg_retro = f"🕒 *Histórico Grupo Shekiná*\n*Culto:* {row['Nome_Culto']}\n*Data:* {row['Data_Culto']}\n*Músicas:* {row['Musicas']}"
                        st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(msg_retro)}" target="_blank"><button style="background-color: #f0f2f6; color: black; border: 1px solid #d1d1d1; padding: 5px 10px; border-radius: 5px; font-size: 12px;">Repostar no WhatsApp</button></a>', unsafe_allow_html=True)

# 5. LÓGICA INTEGRANTES
else:
    st.header("📖 Repertórios Publicados")
    hist = carregar_cultos_salvos()
    if not hist.empty:
        opcoes = (hist['Data_Culto'].astype(str) + " | " + hist['Nome_Culto']).tolist()[::-1]
        escolha = st.selectbox("Escolha o Culto:", opcoes)
        if escolha:
            dt, nm = escolha.split(" | ")
            linha = hist[(hist['Data_Culto'] == dt) & (hist['Nome_Culto'] == nm)]
            lista_n = linha['Musicas'].values[0].split(", ")
            st.table(df_musicas[df_musicas['Musica'].isin(lista_n)][['Musica', 'Artista', 'Tom', 'Andamento']])
