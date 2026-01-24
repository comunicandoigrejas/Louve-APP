import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse
import os

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

# --- SEGURANÇA: TELA DE ENTRADA DO APP ---
# Isso impede que curiosos vejam qualquer conteúdo sem a senha inicial
if 'autenticado_geral' not in st.session_state:
    st.session_state.autenticado_geral = False

if not st.session_state.autenticado_geral:
    st.title("🛡️ Acesso Restrito - Grupo Shekiná")
    # Substitua 'igreja2026' pela senha que você quer dar para TODOS os músicos
    senha_entrada = st.text_input("Digite a senha de acesso da equipe:", type="password")
    if st.button("Entrar no Sistema"):
        if senha_entrada == "igreja2026": # SENHA GERAL DE ENTRADA
            st.session_state.autenticado_geral = True
            st.rerun()
        else:
            st.error("Senha incorreta. Solicite ao líder do ministério.")
    st.stop() # Interrompe o código aqui se não estiver autenticado

# --- DAQUI PARA BAIXO O CÓDIGO SÓ RODA SE A PESSOA ACERTOU A SENHA ---

# 2. CSS DE LIMPEZA
st.markdown("""
    <style>
    [data-testid="stHeader"], header, footer, .stAppDeployButton { display: none !important; }
    #MainMenu {visibility: hidden !important;}
    div[class^="viewerBadge"], [data-testid="stStatusWidget"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÕES ---
SENHA_LIDER = "shekina123" # Senha apenas para as funções de gestão
ARQUIVO_LOUVORES = "louvores.csv"
ARQUIVO_CULTOS = "cultos_salvos.csv"

# --- FUNÇÕES DE DADOS ---
def carregar_dados():
    if not os.path.exists(ARQUIVO_LOUVORES):
        pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento", "Tags"]).to_csv(ARQUIVO_LOUVORES, index=False)
    try:
        df = pd.read_csv(ARQUIVO_LOUVORES)
        df['Musica_Busca'] = df['Musica'].fillna('').astype(str).str.lower().str.strip()
        df['Tags'] = df['Tags'].fillna('').astype(str).str.lower().str.strip()
        return df
    except: return pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento", "Tags"])

def carregar_cultos_salvos():
    if os.path.exists(ARQUIVO_CULTOS):
        try: return pd.read_csv(ARQUIVO_CULTOS)
        except: pass
    return pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Musicas"])

# 3. SIDEBAR COM ASSINATURA
st.sidebar.markdown("# 🎸 Grupo Shekiná")
st.sidebar.markdown(f'''
    <a href="https://www.instagram.com/comunicandoigrejas/" target="_blank">
        <button style="width: 100%; background-color: #333333; color: white; border: 1px solid #555555; padding: 10px; border-radius: 8px; cursor: pointer; font-weight: bold;">
            🔧 By Comunicando Igrejas
        </button>
    </a>
    ''', unsafe_allow_html=True)

perfil = st.sidebar.radio("Nível de Acesso:", ["Integrantes", "Líder (Gestão)"])

# 4. LÓGICA DO LÍDER / INTEGRANTES
if perfil == "Líder (Gestão)":
    senha = st.sidebar.text_input("Senha de Gestor:", type="password")
    if senha == SENHA_LIDER:
        st.sidebar.success("Gestão Liberada")
        t1, t2, t3, t4 = st.tabs(["🎸 Repertório", "➕ Novo Louvor", "🌅 Devocional", "📜 Histórico"])
        
        df_m = carregar_dados()
        lista_of = sorted(df_m['Musica'].unique().tolist())

        with t1:
            c1, c2 = st.columns([2, 1])
            with c1:
                st.subheader("Buscar Louvores")
                busca = st.text_input("Pesquisar:").lower()
                df_f = df_m[df_m['Musica_Busca'].str.contains(busca)] if busca else df_m
                sel = st.dataframe(df_f[['Musica', 'Artista', 'Tom']], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
                if 'cart' not in st.session_state: st.session_state.cart = []
                if sel.selection.rows:
                    for m in df_f.iloc[sel.selection.rows]['Musica'].tolist():
                        if m not in st.session_state.cart: st.session_state.cart.append(m)
            with c2:
                st.subheader("Publicar")
                n_c = st.text_input("Culto:")
                d_c = st.date_input("Data:", date.today())
                cart_v = [m for m in st.session_state.cart if m in lista_of]
                final = st.multiselect("Setlist:", options=lista_of, default=cart_v)
                st.session_state.cart = final
                if st.button("💾 PUBLICAR AGORA"):
                    if n_c and final:
                        reg = pd.DataFrame([[str(d_c), n_c, ", ".join(final)]], columns=["Data_Culto", "Nome_Culto", "Musicas"])
                        pd.concat([carregar_cultos_salvos(), reg], ignore_index=True).to_csv(ARQUIVO_CULTOS, index=False)
                        st.success("✅ Online!")
                        msg = f"🙌 *Grupo Shekiná*\n📌 *Culto:* {n_c}\n🎶 *Lista:* {', '.join(final)}"
                        st.session_state.wa = f"https://wa.me/?text={urllib.parse.quote(msg)}"
                if 'wa' in st.session_state:
                    st.markdown(f'<a href="{st.session_state.wa}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 12px; border-radius: 5px; width: 100%; font-weight: bold;">📢 WHATSAPP</button></a>', unsafe_allow_html=True)

        with t2:
            st.subheader("Cadastrar Louvor")
            with st.form("add_l"):
                nm, ar, tm = st.text_input("Música:"), st.text_input("Artista:"), st.text_input("Tom:")
                if st.form_submit_button("✅ Salvar"):
                    pd.concat([pd.read_csv(ARQUIVO_LOUVORES), pd.DataFrame([[nm, ar, tm, "Medio", ""]], columns=["Musica", "Artista", "Tom", "Andamento", "Tags"])], ignore_index=True).to_csv(ARQUIVO_LOUVORES, index=False)
                    st.success("Adicionado!")
                    st.rerun()

        with t4:
            st.subheader("Histórico")
            h = carregar_cultos_salvos()
            if not h.empty:
                for i, r in h.sort_values(by="Data_Culto", ascending=False).iterrows():
                    with st.expander(f"📅 {r['Data_Culto']} - {r['Nome_Culto']}"):
                        st.write(f"🎶 {r['Musicas']}")
else:
    st.header("📖 Repertório Oficial")
    hist = carregar_cultos_salvos()
    if hist.empty: st.info("Nenhum repertório publicado.")
    else:
        op = (hist['Data_Culto'].astype(str) + " | " + hist['Nome_Culto']).tolist()[::-1]
        escolha = st.selectbox("Selecione:", op)
        if escolha:
            d, n = escolha.split(" | ")
            reg = hist[(hist['Data_Culto'].astype(str) == d) & (hist['Nome_Culto'] == n)].iloc[0]
            st.table(carregar_dados()[carregar_dados()['Musica'].isin(reg['Musicas'].split(", "))][['Musica', 'Artista', 'Tom']])
