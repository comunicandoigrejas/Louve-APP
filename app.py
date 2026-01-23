import streamlit as st
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="App de Louvor", page_icon="🎸", layout="wide")

st.title("🎸 Gerenciador de Repertório - Louvor")

# 1. CARREGANDO DADOS DA PLANILHA
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

# Dicionário de tradução simplificado (mantendo o que você definiu)
tradutor = {
    "Varões": "varoes", 
    "Mulheres": "mulheres", 
    "Jovens": "jovens", 
    "Culto de Louvor": "culto de louvor",
    "Adoração": "adoracao", 
    "Louvor": "louvor", 
    "Congregacional": "congregacional",
    "Missões": "missoes", 
    "Apelo": "apelo", 
    "Santidade": "santidade", 
    "Santa Ceia": "santa ceia", 
    "Agitados": "agitados"
}

st.markdown("---")
st.subheader("🎛️ Filtros Inteligentes de Repertório")

# ABAS COM AS SUAS CATEGORIAS EXATAS
aba_culto, aba_estilo = st.tabs(["🏛️ Perfil do Culto", "🔥 Estilo / Clima"])

filtro_selecionado = None

with aba_culto:
    culto = st.radio(
        "Qual o perfil do culto hoje?", 
        ["Nenhum", "Varões", "Mulheres", "Jovens", "Culto de Louvor"], 
        horizontal=True
    )
    if culto != "Nenhum": filtro_selecionado = culto

with aba_estilo:
    estilo = st.radio(
        "Qual o clima/momento?", 
        ["Nenhum", "Adoração", "Louvor", "Congregacional", "Missões", "Apelo", "Santidade", "Santa Ceia", "Agitados"], 
        horizontal=True
    )
    if estilo != "Nenhum": filtro_selecionado = estilo

# LÓGICA DE FILTRAGEM
if filtro_selecionado:
    busca = tradutor[filtro_selecionado]
    # Busca inteligente: verifica se a tag está presente na string de tags
    sugestoes = df_musicas[df_musicas['Tags'].str.contains(rf'\b{busca}\b', case=False, regex=True)]
    
    if not sugestoes.empty:
        st.success(f"🎵 {len(sugestoes)} músicas encontradas para: **{filtro_selecionado}**")
        st.dataframe(sugestoes[['Musica', 'Artista', 'Tom', 'Andamento']], use_container_width=True, hide_index=True)
    else:
        st.warning(f"Nenhuma música cadastrada para '{filtro_selecionado}' ainda.")

st.markdown("---")

# 3. CONSTRUTOR DE CULTO
st.subheader("📝 Montar o Setlist do Culto")
if not df_musicas.empty:
    musicas_selecionadas = st.multiselect("Selecione as músicas para o repertório final:", options=df_musicas['Musica'].tolist())

    if musicas_selecionadas:
        df_culto = df_musicas[df_musicas['Musica'].isin(musicas_selecionadas)]
        st.table(df_culto[['Musica', 'Artista', 'Tom']])
        
        # Gerador de Texto para WhatsApp
        texto_whatsapp = f"🎸 *REPERTÓRIO: {filtro_selecionado if filtro_selecionado else 'CULTO'}*\n\n"
        for _, row in df_culto.iterrows():
            texto_whatsapp += f"✅ *{row['Musica']}* ({row['Artista']}) - Tom: {row['Tom']}\n"
            
        st.code(texto_whatsapp, language="markdown")
