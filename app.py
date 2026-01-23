import streamlit as st
import pandas as pd
from datetime import date

# Configuração da Página
st.set_page_config(page_title="App Louvor - Gestão", page_icon="🎸", layout="wide")

# 1. BANCO DE DADOS E ESTADO DA SESSÃO
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv('louvores.csv')
        df['Tags'] = df['Tags'].fillna('').str.lower()
        return df
    except:
        return pd.DataFrame()

df_musicas = carregar_dados()

# Inicializa o histórico de cultos salvos (Simulado - em produção usaríamos um CSV ou Sheets)
if 'historico_cultos' not in st.session_state:
    st.session_state.historico_cultos = {} # Ex: {"25/01/2026 - Noite": [Musicas]}

if 'setlist_temp' not in st.session_state:
    st.session_state.setlist_temp = []

# 2. BARRA LATERAL - CONTROLE DE ACESSO
st.sidebar.title("🔐 Acesso")
perfil = st.sidebar.radio("Selecione seu perfil:", ["Integrantes (Visualização)", "Líder (Gestão)"])

# ---------------------------------------------------------
# ABA DO LÍDER: CRIAÇÃO E SALVAMENTO
# ---------------------------------------------------------
if perfil == "Líder (Gestão)":
    st.header("👨‍" + "💻 Painel do Líder")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("1. Montar Repertório")
        aba_culto, aba_estilo = st.tabs(["🏛️ Perfil", "🔥 Estilo"])
        
        filtro = None
        with aba_culto:
            c = st.radio("Perfil:", ["Nenhum", "Varões", "Mulheres", "Jovens", "Louvor"], horizontal=True)
            if c != "Nenhum": filtro = c
        with aba_estilo:
            e = st.radio("Estilo:", ["Nenhum", "Adoração", "Louvor", "Agitados", "Santa Ceia"], horizontal=True)
            if e != "Nenhum": filtro = e

        if filtro:
            tag = filtro.lower().replace("õ", "o")
            sugestoes = df_musicas[df_musicas['Tags'].str.contains(tag)].copy()
            
            sel = st.dataframe(sugestoes[['Musica', 'Artista', 'Tom']], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
            
            if sel.selection.rows:
                novas = sugestoes.iloc[sel.selection.rows]['Musica'].tolist()
                for m in novas:
                    if m not in st.session_state.setlist_temp:
                        st.session_state.setlist_temp.append(m)

    with col2:
        st.subheader("2. Salvar Culto")
        nome_culto = st.text_input("Nome do Culto (Ex: Domingo Noite)")
        data_culto = st.date_input("Data", date.today())
        
        lista_final = st.multiselect("Músicas na lista:", options=df_musicas['Musica'].tolist(), default=st.session_state.setlist_temp)
        st.session_state.setlist_temp = lista_final

        if st.button("💾 SALVAR REPERTÓRIO OFICIAL"):
            if nome_culto and lista_final:
                chave = f"{data_culto.strftime('%d/%m')} - {nome_culto}"
                st.session_state.historico_cultos[chave] = lista_final
                st.success(f"Culto '{chave}' salvo para a equipe!")
                st.session_state.setlist_temp = [] # Limpa após salvar
            else:
                st.warning("Preencha o nome e escolha as músicas.")

# ---------------------------------------------------------
# ABA INTEGRANTES: APENAS VISUALIZAÇÃO
# ---------------------------------------------------------
else:
    st.header("📖 Repertório Oficial")
    
    if not st.session_state.historico_cultos:
        st.info("O líder ainda não liberou o repertório para os próximos cultos.")
    else:
        culto_escolhido = st.selectbox("Selecione o culto para ver as músicas:", list(st.session_state.historico_cultos.keys()))
        
        if culto_escolhido:
            musicas_nomes = st.session_state.historico_cultos[culto_escolhido]
            df_exibir = df_musicas[df_musicas['Musica'].isin(musicas_nomes)]
            
            st.markdown(f"### 📋 Lista para: {culto_escolhido}")
            st.table(df_exibir[['Musica', 'Artista', 'Tom', 'Andamento']])
            
            # Botão para o integrante copiar a lista
            texto = f"🎸 *LOUVOR: {culto_escolhido}*\n\n"
            for _, r in df_exibir.iterrows():
                texto += f"🔹 {r['Musica']} ({r['Tom']})\n"
            st.code(texto)
