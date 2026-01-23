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
        return pd.read_csv(ARQUIVO_CULTOS)
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
        
        # ABAS DO PAINEL DO LÍDER
        tab_repertorio, tab_devocional = st.tabs(["🎸 Montar Repertório", "🌅 Devocional Diário"])
        
        # --- ABA 1: REPERTÓRIO ---
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

        # --- ABA 2: DEVOCIONAL (NOVIDADE) ---
        with tab_devocional:
            st.subheader("📖 Gerador de Devocional Shekiná")
            tema_devocional = st.text_input("Digite o tema do dia (Ex: Fé, Humildade, Força):")
            
            if st.button("✨ Gerar Reflexão"):
                if tema_devocional:
                    # Aqui você pode personalizar os devocionais futuramente ou usar uma API
                    # Por enquanto, criamos uma estrutura base editável
                    st.session_state.devocional_pronto = f"🌅 *Devocional Diário - Grupo Shekiná*\n\n" \
                        f"📍 *Tema:* {tema_devocional.capitalize()}\n\n" \
                        f"📖 *Versículo:* \"Porque vivemos por fé, e não pelo que vemos.\" (2 Coríntios 5:7)\n\n" \
                        f"🙏 *Reflexão:* Que hoje possamos focar não nas dificuldades que os nossos olhos veem, " \
                        f"mas na promessa dAquele que nos chamou para servir. No louvor, a nossa fé se torna voz. " \
                        f"Mantenha seu coração afinado com o céu!\n\n" \
                        f"Deus abençoe seu dia!"
                else:
                    st.warning("Por favor, digite um tema.")

            if 'devocional_pronto' in st.session_state:
                st.text_area("Pré-visualização do Devocional:", st.session_state.devocional_pronto, height=200)
                msg_d = st.session_state.devocional_pronto
                st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(msg_d)}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px; border-radius: 5px; width: 100%;">📲 Enviar Devocional no WhatsApp</button></a>', unsafe_allow_html=True)

# 5. LÓGICA INTEGRANTES
else:
    st.header("📖 Painel do Integrante")
    # ... (Lógica de visualização mantida conforme v4.0)
