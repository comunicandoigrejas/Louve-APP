import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse
import os

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

# 2. CSS DE LIMPEZA (REMOVE ELEMENTOS DO STREAMLIT)
st.markdown("""
    <style>
    [data-testid="stHeader"], header, footer, .stAppDeployButton { display: none !important; }
    #MainMenu {visibility: hidden !important;}
    div[class^="viewerBadge"], [data-testid="stStatusWidget"], .viewerBadge_container__1QSob { 
        display: none !important; 
    }
    .block-container { padding-top: 2rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÕES DE SEGURANÇA ---
SENHA_ACESSO_GERAL = "igreja2026"  
SENHA_LIDER = "shekina123"        
ARQUIVO_LOUVORES = "louvores.csv"
ARQUIVO_CULTOS = "cultos_salvos.csv"

# 3. BARRA LATERAL COM SUA ASSINATURA
st.sidebar.markdown("# 🎸 Grupo Shekiná")

link_ig = "https://www.instagram.com/comunicandoigrejas/"
st.sidebar.markdown(f'''
    <a href="{link_ig}" target="_blank">
        <button style="width: 100%; background-color: #333333; color: white; border: 1px solid #555555; padding: 12px; border-radius: 10px; cursor: pointer; font-weight: bold; margin-bottom: 25px; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);">
            🔧 By Comunicando Igrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

# 4. LÓGICA DE LOGIN
if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🛡️ Acesso Restrito")
    col_login, _ = st.columns([1, 1])
    with col_login:
        entrada = st.text_input("Senha de Acesso:", type="password")
        if st.button("Acessar Sistema"):
            if entrada == SENHA_ACESSO_GERAL or entrada == SENHA_LIDER:
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    st.stop()

# --- FUNÇÕES DE DADOS ---
def carregar_dados():
    if not os.path.exists(ARQUIVO_LOUVORES):
        pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento", "Tags"]).to_csv(ARQUIVO_LOUVORES, index=False)
    try:
        df = pd.read_csv(ARQUIVO_LOUVORES)
        df['Musica_Busca'] = df['Musica'].fillna('').astype(str).str.lower().str.strip()
        return df
    except: return pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento", "Tags"])

def carregar_cultos():
    if os.path.exists(ARQUIVO_CULTOS):
        try: return pd.read_csv(ARQUIVO_CULTOS)
        except: pass
    return pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Musicas"])

# 5. CONTEÚDO PRINCIPAL
perfil = st.sidebar.radio("Nível de Acesso:", ["Integrantes", "Líder (Gestão)"])

if perfil == "Líder (Gestão)":
    senha_gestor = st.sidebar.text_input("Chave de Gestor:", type="password")
    if senha_gestor == SENHA_LIDER:
        st.sidebar.success("Gestão Ativada")
        # Adicionada a aba "Excluir Louvor"
        t1, t2, t3, t4 = st.tabs(["🎸 Repertório", "➕ Novo Louvor", "🗑️ Excluir Louvor", "📜 Histórico"])
        
        df_m = carregar_dados()
        lista_of = sorted(df_m['Musica'].unique().tolist())

        with t1:
            st.subheader("Montar Lista de Louvor")
            busca = st.text_input("Filtrar música:").lower()
            df_f = df_m[df_m['Musica_Busca'].str.contains(busca)] if busca else df_m
            sel = st.dataframe(df_f[['Musica', 'Artista', 'Tom']], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
            
            if 'cart' not in st.session_state: st.session_state.cart = []
            if sel.selection.rows:
                for m in df_f.iloc[sel.selection.rows]['Musica'].tolist():
                    if m not in st.session_state.cart: st.session_state.cart.append(m)
            
            nome_c = st.text_input("Título do Culto:")
            data_c = st.date_input("Data:", date.today())
            final = st.multiselect("Setlist:", options=lista_of, default=[m for m in st.session_state.cart if m in lista_of])
            st.session_state.cart = final
            
            if st.button("💾 PUBLICAR"):
                if nome_c and final:
                    reg = pd.DataFrame([[str(data_c), nome_c, ", ".join(final)]], columns=["Data_Culto", "Nome_Culto", "Musicas"])
                    pd.concat([carregar_cultos(), reg], ignore_index=True).to_csv(ARQUIVO_CULTOS, index=False)
                    st.success("✅ Repertório publicado!")
                    msg = f"🙌 *Shekiná*\n📌 *{nome_c}*\n🎶 {', '.join(final)}"
                    st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(msg)}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px; border-radius: 5px; cursor: pointer;">📢 WhatsApp</button></a>', unsafe_allow_html=True)

        with t2:
            st.subheader("Cadastrar Novo Louvor")
            with st.form("add_form", clear_on_submit=True):
                nm, ar, tm = st.text_input("Nome da Música:"), st.text_input("Artista:"), st.text_input("Tom:")
                if st.form_submit_button("✅ Salvar no Catálogo"):
                    if nm and ar:
                        nova_linha = pd.DataFrame([[nm, ar, tm, "Medio", ""]], columns=["Musica", "Artista", "Tom", "Andamento", "Tags"])
                        pd.concat([carregar_dados().drop(columns=['Musica_Busca']), nova_linha], ignore_index=True).to_csv(ARQUIVO_LOUVORES, index=False)
                        st.success(f"'{nm}' adicionado!")
                        st.rerun()

        with t3:
            st.subheader("🗑️ Excluir Louvor do Catálogo")
            st.warning("Atenção: A exclusão é permanente.")
            musica_para_excluir = st.selectbox("Selecione a música que deseja remover:", [""] + lista_of)
            
            if musica_para_excluir != "":
                # Mostra detalhes para confirmar
                detalhe = df_m[df_m['Musica'] == musica_para_excluir].iloc[0]
                st.info(f"Música: {detalhe['Musica']} | Artista: {detalhe['Artista']}")
                
                if st.button("Confirmar Exclusão Definitiva"):
                    # Remove do DataFrame
                    df_novo = df_m[df_m['Musica'] != musica_para_excluir]
                    # Salva removendo a coluna auxiliar de busca
                    df_novo.drop(columns=['Musica_Busca']).to_csv(ARQUIVO_LOUVORES, index=False)
                    st.success(f"'{musica_para_excluir}' foi removida do sistema.")
                    st.rerun()

        with t4:
            st.subheader("Histórico")
            h = carregar_cultos()
            if not h.empty:
                for i, r in h.sort_values(by="Data_Culto", ascending=False).iterrows():
                    with st.expander(f"📅 {r['Data_Culto']} - {r['Nome_Culto']}"):
                        st.write(r['Musicas'])
    else:
        st.sidebar.warning("Aguardando Chave de Gestor...")

else:
    st.header("📖 Repertório Oficial")
    hist = carregar_cultos()
    if hist.empty: st.info("Nada publicado.")
    else:
        op = (hist['Data_Culto'].astype(str) + " | " + hist['Nome_Culto']).tolist()[::-1]
        esc = st.selectbox("Escolha o Culto:", op)
        if esc:
            d, n = esc.split(" | ")
            reg = hist[(hist['Data_Culto'].astype(str) == d) & (hist['Nome_Culto'] == n)].iloc[0]
            st.table(carregar_dados()[carregar_dados()['Musica'].isin(reg['Musicas'].split(", "))][['Musica', 'Artista', 'Tom']])
