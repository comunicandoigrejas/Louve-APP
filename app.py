import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse
import os

# Configuração da Página
st.set_page_config(page_title="Grupo Shekiná - Gestão", page_icon="🎸", layout="wide")

# --- CONFIGURAÇÕES ---
SENHA_MESTRE = "shekina123" 
ARQUIVO_LOUVORES = "louvores.csv"
ARQUIVO_CULTOS = "cultos_salvos.csv"

# 1. FUNÇÕES DE DADOS
def carregar_dados():
    try:
        df = pd.read_csv(ARQUIVO_LOUVORES)
        df['Musica_Busca'] = df['Musica'].fillna('').str.lower().str.strip()
        df['Tags'] = df['Tags'].fillna('').str.lower().str.strip()
        return df
    except:
        return pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento", "Tags"])

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
        
        # ABAS DO PAINEL DO LÍDER (Agora com Cadastro)
        tab_repertorio, tab_cadastro, tab_devocional, tab_historico = st.tabs([
            "🎸 Montar Repertório", "➕ Novo Louvor", "🌅 Devocional", "📜 Histórico de Cultos"
        ])
        
        # --- ABA 1: REPERTÓRIO (MANTIDA) ---
        with tab_repertorio:
            # (Mesma lógica de busca e carrinho das versões anteriores)
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

            st.markdown("---")
            nome_c = st.text_input("Nome do Culto (Ex: Varões):")
            data_c = st.date_input("Data:", date.today())
            lista_final = st.multiselect("Setlist Selecionada:", options=df_musicas['Musica'].tolist(), default=st.session_state.carrinho)
            st.session_state.carrinho = lista_final

            if st.button("💾 Salvar e Publicar Culto"):
                if nome_c and lista_final:
                    novos_dados = pd.DataFrame([[data_c, nome_c, ", ".join(lista_final)]], columns=["Data_Culto", "Nome_Culto", "Musicas"])
                    pd.concat([carregar_cultos_salvos(), novos_dados]).to_csv(ARQUIVO_CULTOS, index=False)
                    st.success(f"Culto de {nome_c} salvo com sucesso!")
                    st.session_state.carrinho = [] # Limpa após salvar
                    st.rerun()

        # --- ABA 2: NOVO LOUVOR (A SOLICITADA!) ---
        with tab_cadastro:
            st.subheader("📝 Cadastrar Nova Música no Catálogo")
            with st.form("form_novo_louvor", clear_on_submit=True):
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    novo_nome = st.text_input("Nome da Música:")
                    novo_artista = st.text_input("Cantor / Ministério:")
                with col_c2:
                    novo_tom = st.text_input("Tom Sugerido (Ex: G, Am):")
                    novo_andamento = st.selectbox("Andamento:", ["Lento", "Medio", "Rapido"])
                
                novas_tags = st.multiselect("Classificação (Tags):", 
                    ["Adoração", "Louvor", "Agitados", "Pentecostal", "Varões", "Mulheres", "Jovens", "Missões", "Apelo", "Santidade", "Santa Ceia", "Congregacional"])
                
                submit = st.form_submit_button("✅ Adicionar Louvor ao Banco de Dados")
                
                if submit:
                    if novo_nome and novo_artista:
                        # Prepara a linha para o CSV
                        tags_str = " ".join([t.lower().replace("õ", "o").replace("ã", "a").replace("é", "e") for t in novas_tags])
                        novo_row = pd.DataFrame([[novo_nome, novo_artista, novo_tom, novo_andamento, tags_str]], 
                                              columns=["Musica", "Artista", "Tom", "Andamento", "Tags"])
                        
                        # Salva no CSV de louvores
                        pd.concat([df_musicas.drop(columns=['Musica_Busca']), novo_row]).to_csv(ARQUIVO_LOUVORES, index=False)
                        st.success(f"'{novo_nome}' foi adicionado com sucesso!")
                        st.cache_data.clear() # Limpa o cache para a música aparecer na busca
                    else:
                        st.error("Nome da música e Artista são obrigatórios.")

        # --- ABA 3: DEVOCIONAL (MANTIDA) ---
        with tab_devocional:
            # (Lógica do devocional mantida)
            st.subheader("📖 Enviar Mensagem de Edificação")
            t_dev = st.text_input("Tema:")
            if st.button("Gerar"):
                st.session_state.d_text = f"🌅 *Devocional Shekiná*\n*Tema:* {t_dev}\n\nDeus é fiel!"
            if 'd_text' in st.session_state:
                st.text_area("Texto:", st.session_state.d_text)

        # --- ABA 4: HISTÓRICO DE CULTOS (VISUALIZAÇÃO POR DATA) ---
        with tab_historico:
            st.subheader("📜 Registro Cronológico de Cultos")
            h_db = carregar_cultos_salvos()
            if not h_db.empty:
                h_ord = h_db.sort_values(by="Data_Culto", ascending=False)
                for i, r in h_ord.iterrows():
                    with st.expander(f"📅 {r['Data_Culto']} - {r['Nome_Culto']}"):
                        st.write(f"**Músicas:** {r['Musicas']}")

# 5. LÓGICA INTEGRANTES (VISUALIZAÇÃO)
else:
    st.header("📖 Painel do Integrante")
    # ... (Visualização dos cultos salvos mantida)
