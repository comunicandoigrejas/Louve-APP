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
        return pd.read_csv('louvores.csv')
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
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3293/3293810.png", width=100)
perfil = st.sidebar.radio("Acesso:", ["Integrantes (Visualização)", "Líder (Gestão)"])

# --- LÓGICA DO LÍDER ---
if perfil == "Líder (Gestão)":
    senha = st.sidebar.text_input("Senha:", type="password")
    if senha == SENHA_MESTRE:
        st.sidebar.success("Líder Autenticado")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("1. Seleção de Músicas")
            aba_perfil, aba_estilo = st.tabs(["🏛️ Perfil", "🔥 Estilo"])
            # ... (filtros de rádio mantidos conforme sua lista anterior)
            
            # Simulando seleção (ajustada para simplicidade do exemplo)
            busca_rapida = st.text_input("🔍 Busca rápida por tag (ex: jovens, mulheres):")
            if busca_rapida:
                sugestoes = df_musicas[df_musicas['Tags'].str.contains(busca_rapida.lower())]
                sel = st.dataframe(sugestoes[['Musica', 'Artista', 'Tom']], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
                
                if sel.selection.rows:
                    if 'temp_list' not in st.session_state: st.session_state.temp_list = []
                    nomes = sugestoes.iloc[sel.selection.rows]['Musica'].tolist()
                    for n in nomes:
                        if n not in st.session_state.temp_list: st.session_state.temp_list.append(n)

        with col2:
            st.subheader("2. Salvar e Notificar")
            nome_c = st.text_input("Nome do Culto:")
            data_c = st.date_input("Data:", date.today())
            lista_final = st.multiselect("Repertório:", options=df_musicas['Musica'].tolist(), default=st.session_state.get('temp_list', []))
            
            if st.button("💾 Salvar Louvor Oficial"):
                if nome_c and lista_final:
                    # Salva no arquivo CSV permanente
                    novos_dados = pd.DataFrame([[data_c, nome_c, ", ".join(lista_final)]], columns=["Data_Culto", "Nome_Culto", "Musicas"])
                    historico = carregar_cultos_salvos()
                    pd.concat([historico, novos_dados]).to_csv(ARQUIVO_CULTOS, index=False)
                    
                    st.success("Repertório Salvo no Banco de Dados!")
                    
                    # Gerar link de notificação WhatsApp
                    msg = f"🙌 *Grupo Shekiná - Novo Louvor!*\n\nO repertório para o culto *{nome_c}* ({data_c.strftime('%d/%m')}) já está disponível no nosso app!\n\n🎶 *Músicas:* {', '.join(lista_final)}"
                    msg_url = urllib.parse.quote(msg)
                    link_wa = f"https://wa.me/?text={msg_url}"
                    
                    st.markdown(f'''<a href="{link_wa}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">📢 Notificar Equipe no WhatsApp</button></a>''', unsafe_allow_html=True)
                else:
                    st.warning("Preencha todos os campos.")

# --- LÓGICA INTEGRANTES ---
else:
    st.subheader("📖 Repertórios Publicados - Grupo Shekiná")
    historico = carregar_cultos_salvos()
    
    if historico.empty:
        st.info("Aguardando o líder publicar o próximo culto.")
    else:
        # Mostra o mais recente primeiro
        lista_cultos = (historico['Data_Culto'] + " - " + historico['Nome_Culto']).tolist()
        escolha = st.selectbox("Selecione o Culto:", lista_cultos[::-1])
        
        if escolha:
            # Filtra a música do CSV salvo
            data_sel = escolha.split(" - ")[0]
            nome_sel = escolha.split(" - ")[1]
            musicas_str = historico[(historico['Data_Culto'] == data_sel) & (historico['Nome_Culto'] == nome_sel)]['Musicas'].values[0]
            lista_nomes = musicas_sel = musicas_str.split(", ")
            
            df_final = df_musicas[df_musicas['Musica'].isin(lista_nomes)]
            st.table(df_final[['Musica', 'Artista', 'Tom', 'Andamento']])
