import streamlit as st
from streamlit_gsheets import GSheetsConnection
from openai import OpenAI
import pandas as pd
from datetime import date
import urllib.parse

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Grupo Shekiná", page_icon="🎸", layout="wide")

# 2. INICIALIZAÇÃO SEGURA (Evita erro da image_b66295)
openai_key = st.secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=openai_key) if openai_key else None
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. CSS DE MARCA (By Comunicando Igrejas)
st.markdown("""
    <style>
    [data-testid="stHeader"], header, footer, .stAppDeployButton { display: none !important; }
    #MainMenu {visibility: hidden !important;}
    .block-container { padding-top: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE APOIO ---
def carregar_louvores():
    try:
        df = conn.read(worksheet="Louvores", ttl=0)
        df.columns = [c.strip() for c in df.columns]
        df['Musica_Busca'] = df['Musica'].fillna('').astype(str).str.lower().str.strip()
        return df
    except: return pd.DataFrame()

def carregar_cultos():
    try: 
        df = conn.read(worksheet="Cultos", ttl=0)
        return df
    except: return pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Tema_Culto", "Musicas"])

# 4. INTERFACE DO LÍDER (Acesso: shekina123)
df_l = carregar_louvores()
t1, t2 = st.tabs(["🎸 Montar Setlist", "📜 Histórico"])

with t1:
    st.subheader("Seleção de Louvores")
    busca = st.text_input("Pesquisar louvor:").lower()
    df_f = df_l[df_l['Musica_Busca'].str.contains(busca)] if (not df_l.empty and busca) else df_l
    sel = st.dataframe(df_f[["Musica", "Artista"]], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
    
    st.write("---")
    nome_c = st.text_input("Nome do Culto:")
    data_c = st.date_input("Data do Culto:", date.today())
    tema_c = st.text_input("Tema do Culto:")
    
    if st.button("💾 PUBLICAR E SALVAR HISTÓRICO"):
        if sel.selection.rows and nome_c:
            try:
                # Coleta as músicas selecionadas
                selecionadas = df_f.iloc[sel.selection.rows]['Musica'].tolist()
                df_h_atual = carregar_cultos()
                # CORREÇÃO DA DATA: dd-mm-yy
                data_str = data_c.strftime('%d-%m-%y')
                novo_registro = pd.DataFrame([[data_str, nome_c, tema_c, ", ".join(selecionadas)]], 
                                            columns=["Data_Culto", "Nome_Culto", "Tema_Culto", "Musicas"])
                # TENTA SALVAR (Exige Conta de Serviço nos Secrets)
                conn.update(worksheet="Cultos", data=pd.concat([df_h_atual, novo_registro], ignore_index=True))
                st.success("✅ Histórico registrado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao salvar: {e}. Verifique se configurou a 'Service Account'.")

    # BOTÃO WHATSAPP CORRIGIDO (Evita image_b57940)
    if nome_c and sel.selection.rows:
        dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        msg = f"A paz do senhor grupo segue os louvores do culto *{nome_c}* .......\n\n"
        msg += f"📅 *Data:* {data_c.strftime('%d-%m-%y')} ({dias[data_c.weekday()]})\n"
        msg += f"📖 *Tema:* {tema_c}\n\n🎶 *LOUVORES:*\n"
        selecionadas = df_f.iloc[sel.selection.rows]['Musica'].tolist()
        for i, m in enumerate(selecionadas, 1): msg += f"{i}. {m}\n"
        
        # urllib.parse.quote resolve o problema dos triângulos pretos (image_b57940)
        link_wa = f"https://wa.me/?text={urllib.parse.quote(msg)}"
        st.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">📢 ENVIAR SETLIST WHATSAPP</button></a>', unsafe_allow_html=True)
