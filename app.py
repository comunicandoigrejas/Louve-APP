import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse

# Configuração da Página
st.set_page_config(page_title="Grupo Shekiná - Louvor", page_icon="🎸", layout="wide")

# --- CONFIGURAÇÕES ---
SENHA_MESTRE = "shekina123" 
ARQUIVO_CULTOS = "cultos_salvos.csv"

# 1. CARREGAR DADOS
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv('louvores.csv')
        # Limpeza de dados: remove espaços em branco e padroniza para minúsculo
        df['Musica'] = df['Musica'].str.strip()
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

# 2. TÍTULO PERSONALIZADO
st.title("🛡️ Grupo Shekiná - Gestão de Louvor")

# 3. BARRA LATERAL
st.sidebar.title("🔐 Acesso")
perfil = st.sidebar.radio("Selecione seu perfil:", ["Integrantes (Visualização)", "Líder (Gestão)"])

# 4. LÓGICA DO LÍDER
if perfil == "Líder (Gestão)":
    senha = st.sidebar.text_input("Senha de Líder:", type="password")
    if senha == SENHA_MESTRE:
        st.sidebar.success("Acesso Liberado")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("1. Buscar e Selecionar Louvores")
            
            # NOVOS BOTÕES DE FILTRO (Corrigidos para buscar nas tags)
            categoria = st.selectbox(
                "Filtrar por Tipo de Culto ou Estilo:",
                ["Ver Todos", "Varões", "Mulheres", "Jovens", "Culto de Louvor", "Adoração", "Louvor", "Congregacional", "Missões", "Apelo", "Santidade", "Santa Ceia", "Agitados"]
            )

            # Lógica de filtragem aprimorada
            if categoria != "Ver Todos":
                # Tradução simples para as tags do CSV (sem acento e minúsculo)
                termo_busca = categoria.lower().replace("õ", "o").replace("ã", "a").replace("é", "e")
                # Filtra se o termo de busca estiver contido na coluna Tags
                df_exibir = df_musicas[df_musicas['Tags'].str.contains(termo_busca, na=False)]
            else:
                df_exibir = df_musicas

            st.write(f"Exibindo {len(df_exibir)} músicas encontradas:")
            
            # Tabela Interativa de Seleção
            selecao = st.dataframe(
                df_exibir[['Musica', 'Artista', 'Tom', 'Andamento']],
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="multi-row"
            )

            # Adicionar selecionados ao carrinho (Session State)
            if 'carrinho' not in st.session_state: st.session_state.carrinho = []
            
            if selecao.selection.rows:
                selecionadas_agora = df_exibir.iloc[selecao.selection.rows]['Musica'].tolist()
                for m in selecionadas_agora:
                    if m not in st.session_state.carrinho:
                        st.session_state.carrinho.append(m)

        with col2:
            st.subheader("2. Finalizar Repertório")
            nome_c = st.text_input("Nome do Culto:", placeholder="Ex: Domingo Noite")
            data_c = st.date_input("Data:", date.today())
            
            lista_final = st.multiselect(
                "Músicas na Setlist:", 
                options=df_musicas['Musica'].tolist(),
                default=st.session_state.carrinho
            )
            st.session_state.carrinho = lista_final

            if st.button("💾 Salvar para a Equipe Shekiná"):
                if nome_c and lista_final:
                    # Salva permanentemente
                    novos_dados = pd.DataFrame([[data_c, nome_c, ", ".join(lista_final)]], columns=["Data_Culto", "Nome_Culto", "Musicas"])
                    historico = carregar_cultos_salvos()
                    pd.concat([historico, novos_dados]).to_csv(ARQUIVO_CULTOS, index=False)
                    
                    st.success("Repertório publicado!")
                    
                    # Link WhatsApp
                    msg = f"🙌 *Grupo Shekiná - Repertório Liberado!*\n\nCulto: *{nome_c}*\nData: {data_c.strftime('%d/%m')}\n\n🎶 *Lista:* {', '.join(lista_final)}"
                    st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(msg)}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; width: 100%;">📢 Notificar no WhatsApp</button></a>', unsafe_allow_html=True)
                else:
                    st.warning("Dê um nome ao culto e selecione as músicas.")

# 5. LÓGICA DOS INTEGRANTES (VISUALIZAÇÃO)
else:
    st.header("📖 Painel do Integrante")
    historico = carregar_cultos_salvos()
    
    if historico.empty:
        st.info("Aguardando o líder salvar o primeiro repertório.")
    else:
        # Pega os cultos salvos e inverte para o mais novo aparecer primeiro
        opcoes = (historico['Data_Culto'].astype(str) + " | " + historico['Nome_Culto']).tolist()[::-1]
        escolha = st.selectbox("Selecione o culto para ver os tons:", opcoes)
        
        if escolha:
            data_s, nome_s = escolha.split(" | ")
            linha = historico[(historico['Data_Culto'] == data_s) & (historico['Nome_Culto'] == nome_s)]
            lista_nomes = linha['Musicas'].values[0].split(", ")
            
            df_visualizar = df_musicas[df_musicas['Musica'].isin(lista_nomes)]
            st.markdown(f"### 📋 Repertório: {nome_s}")
            st.table(df_visualizar[['Musica', 'Artista', 'Tom', 'Andamento']])
