import streamlit as st
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="App de Louvor", page_icon="🎸", layout="wide")

st.title("🎸 Gerenciador de Repertório - Louvor")

# Inicializar a lista de seleção no estado da sessão (Session State)
if 'setlist_selecionada' not in st.session_state:
    st.session_state.setlist_selecionada = []

# 1. CARREGANDO DADOS
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv('louvores.csv')
        df['Tags'] = df['Tags'].fillna('').str.lower()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar banco de dados: {e}")
        return pd.DataFrame()

df_musicas = carregar_dados()

# Dicionário de tradução
tradutor = {
    "Varões": "varoes", "Mulheres": "mulheres", "Jovens": "jovens", "Culto de Louvor": "culto de louvor",
    "Adoração": "adoracao", "Louvor": "louvor", "Congregacional": "congregacional",
    "Missões": "missoes", "Apelo": "apelo", "Santidade": "santidade", 
    "Santa Ceia": "santa ceia", "Agitados": "agitados"
}

st.markdown("---")
st.subheader("🎛️ 1. Encontre e Selecione as Músicas")
st.caption("Dica: Use os filtros abaixo e marque o check ao lado da música para adicioná-la ao culto.")

aba_culto, aba_estilo = st.tabs(["🏛️ Perfil do Culto", "🔥 Estilo / Clima"])
filtro_selecionado = None

with aba_culto:
    culto = st.radio("Qual o perfil do culto?", ["Nenhum", "Varões", "Mulheres", "Jovens", "Culto de Louvor"], horizontal=True)
    if culto != "Nenhum": filtro_selecionado = culto

with aba_estilo:
    estilo = st.radio("Qual o clima?", ["Nenhum", "Adoração", "Louvor", "Congregacional", "Missões", "Apelo", "Santidade", "Santa Ceia", "Agitados"], horizontal=True)
    if estilo != "Nenhum": filtro_selecionado = estilo

# LÓGICA DE FILTRAGEM E SELEÇÃO DIRETA
if filtro_selecionado:
    busca = tradutor[filtro_selecionado]
    sugestoes = df_musicas[df_musicas['Tags'].str.contains(rf'\b{busca}\b', case=False, regex=True)].copy()
    
    if not sugestoes.empty:
        # Criando a tabela interativa para seleção
        event = st.dataframe(
            sugestoes[['Musica', 'Artista', 'Tom', 'Andamento']],
            use_container_width=True,
            hide_index=True,
            on_select="rerun", # Faz o app atualizar assim que clica
            selection_mode="multi-row" # Permite selecionar várias
        )

        # Se houver linhas selecionadas na tabela, adicionamos ao Session State
        selecionados_na_tabela = event.selection.rows
        if selecionados_na_tabela:
            novas_musicas = sugestoes.iloc[selecionados_na_tabela]['Musica'].tolist()
            # Unir com o que já estava selecionado sem duplicar
            for m in novas_musicas:
                if m not in st.session_state.setlist_selecionada:
                    st.session_state.setlist_selecionada.append(m)

st.markdown("---")

# 2. LISTA FINAL DO CULTO
st.subheader("📝 2. Setlist Final do Culto")

# O Multiselect agora é alimentado pelo clique na tabela, mas também permite busca manual
setlist_final = st.multiselect(
    "Músicas escolhidas (você pode remover ou adicionar aqui também):",
    options=df_musicas['Musica'].tolist(),
    default=st.session_state.setlist_selecionada
)

# Atualiza o estado caso o usuário remova algo no multiselect
st.session_state.setlist_selecionada = setlist_final

if setlist_final:
    df_culto = df_musicas[df_musicas['Musica'].isin(setlist_final)]
    st.table(df_culto[['Musica', 'Artista', 'Tom']])
    
    # Botão para limpar tudo
    if st.button("Limpar Lista"):
        st.session_state.setlist_selecionada = []
        st.rerun()

    # Gerador de Texto para WhatsApp
    texto_whatsapp = f"🎸 *REPERTÓRIO: {filtro_selecionado if filtro_selecionado else 'CULTO'}*\n\n"
    for _, row in df_culto.iterrows():
        texto_whatsapp += f"✅ *{row['Musica']}* ({row['Artista']}) - Tom: {row['Tom']}\n"
        
    st.code(texto_whatsapp, language="markdown")
else:
    st.info("Sua lista está vazia. Selecione as músicas na tabela acima.")
