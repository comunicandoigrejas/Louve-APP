import streamlit as st
import pandas as pd

st.set_page_config(page_title="App de Louvor", page_icon="🎸", layout="wide")

st.title("🎸 Gerenciador de Repertório - Louvor")

# 1. CARREGANDO DADOS DA SUA PLANILHA (louvores.csv)
@st.cache_data
def carregar_dados():
    try:
        # Tenta ler o arquivo CSV que você vai criar
        return pd.read_csv('louvores.csv')
    except FileNotFoundError:
        # Se não achar o arquivo, cria um de exemplo
        dados_exemplo = {
            'Musica': ['A Casa é Sua', 'Porque Ele Vive', 'Raridade', 'Caminho no Deserto', 'Te Agradeço'],
            'Artista': ['Casa Worship', 'Harpa', 'Anderson Freire', 'Soraya Moraes', 'Kleber Lucas'],
            'Tom': ['G', 'G', 'C', 'A', 'E'],
            'Andamento': ['Lento', 'Médio', 'Lento', 'Médio', 'Rápido'],
            'Tema': ['Adoração', 'Celebração', 'Apelo', 'Adoração', 'Abertura'],
            'Tags': ['intimidade quebrantamento', 'ressurreicao domingo', 'salvacao perdao', 'fe milagres', 'gratidao festa']
        }
        return pd.DataFrame(dados_exemplo)

df_musicas = carregar_dados()

# 2. ASSISTENTE DE REPERTÓRIO (O RECURSO NOVO!)
st.markdown("---")
st.subheader("💡 Assistente de Repertório")
st.write("Me diga o estilo de louvor que você quer cantar hoje:")

# O usuário digita o que quer
busca_estilo = st.text_input("Ex: 'louvor animado para abertura' ou 'adoração lenta'")

if busca_estilo:
    busca = busca_estilo.lower()
    # O app procura o texto digitado nas colunas de Tema, Andamento e Tags
    sugestoes = df_musicas[
        df_musicas['Tema'].str.lower().str.contains(busca, na=False) |
        df_musicas['Andamento'].str.lower().str.contains(busca, na=False) |
        df_musicas['Tags'].str.lower().str.contains(busca, na=False)
    ]
    
    if not sugestoes.empty:
        st.success(f"Encontrei {len(sugestoes)} música(s) na sua lista para esse momento:")
        st.dataframe(sugestoes[['Musica', 'Artista', 'Tom', 'Andamento', 'Tema']], hide_index=True)
    else:
        st.warning("Poxa, não encontrei nenhuma música com esse estilo na sua lista. Tente usar outras palavras-chave.")

st.markdown("---")

# 3. CONSTRUTOR DE CULTO (MANTIDO DO ANTERIOR)
st.subheader("📝 Montar o Setlist do Culto")
musicas_selecionadas = st.multiselect(
    "Escolha as músicas:",
    options=df_musicas['Musica'].tolist()
)

if musicas_selecionadas:
    df_culto = df_musicas[df_musicas['Musica'].isin(musicas_selecionadas)]
    st.table(df_culto[['Musica', 'Artista', 'Tom']])
