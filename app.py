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
        # Garante que os textos (sem valor) não deem erro e coloca tudo em minúsculo para a busca
        df['Tags'] = df['Tags'].fillna('').str.lower()
        df['Tema'] = df['Tema'].fillna('').str.lower()
        return df
    except FileNotFoundError:
        st.error("Arquivo louvores.csv não encontrado. Crie o arquivo na mesma pasta.")
        return pd.DataFrame()

df_musicas = carregar_dados()

# 2. FILTROS RÁPIDOS POR BOTÕES (O RECURSO NOVO!)
st.markdown("---")
st.subheader("🎛️ Assistente: Encontre a música ideal")

# Criamos abas para organizar os botões
aba_culto, aba_estilo, aba_andamento = st.tabs(["🏛️ Por Tipo de Culto", "🔥 Por Estilo", "⏱️ Por Andamento"])

filtro_selecionado = None

with aba_culto:
    culto = st.radio(
        "Para qual culto você precisa das músicas?",
        ["Nenhum", "Jovens", "Varões", "Mulheres", "Missões", "Santa Ceia"],
        horizontal=True
    )
    if culto != "Nenhum":
        filtro_selecionado = culto

with aba_estilo:
    estilo = st.radio(
        "Qual o clima/estilo do momento?",
        ["Nenhum", "Adoração", "Pentecostal", "Celebração", "Busca", "Santificação", "Apelo"],
        horizontal=True
    )
    if estilo != "Nenhum":
        filtro_selecionado = estilo

with aba_andamento:
    andamento = st.radio(
        "Qual o ritmo das músicas?",
        ["Nenhum", "Lento", "Medio", "Rapido"],
        horizontal=True
    )
    if andamento != "Nenhum":
        filtro_selecionado = andamento

# LÓGICA DE FILTRAGEM
if filtro_selecionado:
    busca = filtro_selecionado.lower()
    
    # Se for busca por andamento, olha na coluna certa
    if filtro_selecionado in ["Lento", "Medio", "Rapido"]:
        sugestoes = df_musicas[df_musicas['Andamento'].str.lower() == busca]
    else:
        # Se for estilo ou culto, olha nas Tags e no Tema
        sugestoes = df_musicas[
            df_musicas['Tema'].str.contains(busca) |
            df_musicas['Tags'].str.contains(busca)
        ]
    
    # Exibir o resultado
    if not sugestoes.empty:
        st.success(f"🎵 Encontrei {len(sugestoes)} música(s) para: **{filtro_selecionado}**")
        
        # Formatação bonita da tabela de resultados
        st.dataframe(
            sugestoes[['Musica', 'Artista', 'Tom', 'Andamento', 'Tema']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Nenhuma música encontrada com esse filtro.")

st.markdown("---")

# 3. CONSTRUTOR DE CULTO
st.subheader("📝 Montar o Setlist do Culto")
musicas_selecionadas = st.multiselect(
    "Escolha as músicas para a lista final:",
    options=df_musicas['Musica'].tolist()
)

if musicas_selecionadas:
    df_culto = df_musicas[df_musicas['Musica'].isin(musicas_selecionadas)]
    st.table(df_culto[['Musica', 'Artista', 'Tom']])
    
    # Gerador de Texto para WhatsApp
    texto_whatsapp = "🎸 *Repertório de Hoje:*\n"
    for _, row in df_culto.iterrows():
        texto_whatsapp += f"- {row['Musica']} ({row['Artista']}) | Tom: {row['Tom']}\n"
        
    st.code(texto_whatsapp, language="markdown")
