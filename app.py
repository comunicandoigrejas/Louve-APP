import streamlit as st
import pandas as pd
from datetime import date

# Configuração da Página
st.set_page_config(page_title="App Louvor - Gestão", page_icon="🎸", layout="wide")

# --- SENHA DO LÍDER (Altere aqui) ---
SENHA_MESTRE = "igreja123" 

# 1. CARREGANDO DADOS
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv('louvores.csv')
        df['Tags'] = df['Tags'].fillna('').str.lower()
        return df
    except:
        return pd.DataFrame()

df_musicas = carregar_dados()

# Inicializa o histórico se não existir
if 'historico_cultos' not in st.session_state:
    st.session_state.historico_cultos = {}

if 'setlist_temp' not in st.session_state:
    st.session_state.setlist_temp = []

# 2. BARRA LATERAL - CONTROLE DE ACESSO
st.sidebar.title("🔐 Área de Acesso")
perfil = st.sidebar.radio("Selecione seu perfil:", ["Integrantes (Visualização)", "Líder (Gestão)"])

# ---------------------------------------------------------
# LÓGICA DE LOGIN PARA O LÍDER
# ---------------------------------------------------------
if perfil == "Líder (Gestão)":
    senha_digitada = st.sidebar.text_input("Digite a senha de líder:", type="password")
    
    if senha_digitada == SENHA_MESTRE:
        st.sidebar.success("Acesso Liberado!")
        
        # --- TODO O CONTEÚDO DO LÍDER FICA DENTRO DESTE IF ---
        st.header("👨‍💻 Painel de Gestão (Líder)")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("1. Buscar Louvores")
            aba_culto, aba_estilo = st.tabs(["🏛️ Perfil", "🔥 Estilo"])
            filtro = None
            with aba_culto:
                c = st.radio("Perfil:", ["Nenhum", "Varões", "Mulheres", "Jovens", "Culto de Louvor"], horizontal=True)
                if c != "Nenhum": filtro = c
            with aba_estilo:
                e = st.radio("Estilo:", ["Nenhum", "Adoração", "Louvor", "Agitados", "Santa Ceia", "Missões"], horizontal=True)
                if e != "Nenhum": filtro = e

            if filtro:
                # Dicionário simples para busca nas tags
                mapa = {"Varões": "varoes", "Missões": "missoes", "Santa Ceia": "santa ceia"}
                tag_busca = mapa.get(filtro, filtro.lower())
                
                sugestoes = df_musicas[df_musicas['Tags'].str.contains(tag_busca)].copy()
                
                sel = st.dataframe(sugestoes[['Musica', 'Artista', 'Tom']], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
                
                if sel.selection.rows:
                    novas = sugestoes.iloc[sel.selection.rows]['Musica'].tolist()
                    for m in novas:
                        if m not in st.session_state.setlist_temp:
                            st.session_state.setlist_temp.append(m)

        with col2:
            st.subheader("2. Salvar Setlist")
            nome_culto = st.text_input("Nome do Culto (Ex: Domingo Noite)")
            data_culto = st.date_input("Data", date.today())
            
            lista_final = st.multiselect("Músicas:", options=df_musicas['Musica'].tolist(), default=st.session_state.setlist_temp)
            st.session_state.setlist_temp = lista_final

            if st.button("💾 SALVAR REPERTÓRIO"):
                if nome_culto and lista_final:
                    chave = f"{data_culto.strftime('%d/%m')} - {nome_culto}"
                    st.session_state.historico_cultos[chave] = lista_final
                    st.success(f"Culto '{chave}' salvo com sucesso!")
                    st.session_state.setlist_temp = []
                else:
                    st.warning("Preencha o nome e selecione músicas.")
                    
    elif senha_digitada != "" and senha_digitada != SENHA_MESTRE:
        st.sidebar.error("Senha Incorreta!")
        st.info("Por favor, digite a senha correta para acessar as ferramentas de líder.")

# ---------------------------------------------------------
# ABA INTEGRANTES: APENAS VISUALIZAÇÃO
# ---------------------------------------------------------
else:
    st.header("📖 Repertório Oficial da Equipe")
    
    if not st.session_state.historico_cultos:
        st.info("Nenhum repertório foi publicado pelo líder ainda.")
    else:
        culto_escolhido = st.selectbox("Selecione o culto:", list(st.session_state.historico_cultos.keys()))
        
        if culto_escolhido:
            musicas_nomes = st.session_state.historico_cultos[culto_escolhido]
            df_exibir = df_musicas[df_musicas['Musica'].isin(musicas_nomes)]
            
            st.markdown(f"### 📋 Lista: {culto_escolhido}")
            st.table(df_exibir[['Musica', 'Artista', 'Tom', 'Andamento']])
            
            texto = f"🎸 *LOUVOR: {culto_escolhido}*\n\n"
            for _, r in df_exibir.iterrows():
                texto += f"✅ {r['Musica']} - Tom: {r['Tom']}\n"
            st.code(texto)
