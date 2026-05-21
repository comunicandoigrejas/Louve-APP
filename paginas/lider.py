import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse

# Botão de retorno seguro para a Página Inicial centralizada
if st.button("⬅️ Voltar para a Página Inicial"):
    st.switch_page("paginas/inicial.py")

st.title("🛠️ Painel de Controle e Gestão (Líder)")
st.markdown("Seja bem-vindo, abençoado! Aqui você gerencia toda a plataforma do Grupo Shekiná.")

conn = st.session_state.conn

# --- CARREGAMENTO SEGURO DOS DADOS DA PLANILHA ---
try:
    df_louvores = conn.read(worksheet="Louvores", ttl=0)
    df_louvores.columns = [c.strip() for c in df_louvores.columns]
except:
    df_louvores = pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento", "Categoria"])

try:
    df_cultos = conn.read(worksheet="Cultos", ttl=0)
    df_cultos.columns = [c.strip() for c in df_cultos.columns]
except:
    df_cultos = pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Tema_Culto", "Musicas"])

try:
    df_cifras = conn.read(worksheet="Cifras", ttl=0)
    df_cifras.columns = [c.strip() for c in df_cifras.columns]
except:
    df_cifras = pd.DataFrame(columns=["Musica", "Artista", "Tom_Padrao", "Tipo_Arquivo", "Link_Cifra"])


# --- ABAS DE GERENCIAMENTO UNIFICADO ---
tab_escalas, tab_novo_louvor, tab_nova_cifra = st.tabs([
    "📅 Agendar Culto / Ensaio", 
    "🎵 Cadastrar Novo Louvor", 
    "📜 Cadastrar Nova Cifra"
])


# ================= TAB 1: AGENDAR CULTOS E ENSAIOS =================
with tab_escalas:
    st.subheader("Nova Escala de Louvor")
    
    tipo_evento = st.selectbox("Selecione o Tipo de Evento:", ["Culto de Celebração", "Ensaio do Grupo", "Culto de Doutrina", "Vigília", "Festividade"])
    data_evento = st.date_input("Data marcada:", date.today())
    tema_evento = st.text_input("Tema Central ou Palavra da Noite:", placeholder="Ex: Gratidão, Fé, Santidade...")
    
    if not df_louvores.empty and 'Musica' in df_louvores.columns:
        lista_opcoes = sorted(df_louvores['Musica'].dropna().tolist())
        setlist = st.multiselect("Selecione os louvores para este dia (vêm do Repertório):", options=lista_opcoes)
    else:
        st.warning("Nenhum louvor cadastrado encontrado para seleção.")
        setlist = []
        
    st.write("---")
    
    if st.button("💾 SALVAR ESCALA NA PLANILHA", use_container_width=True):
        if tipo_evento and setlist:
            data_formatada = data_evento.strftime('%d/%m/%Y')
            m_juntas = ", ".join(setlist)
            
            nova_linha_culto = pd.DataFrame([[data_formatada, tipo_evento, tema_evento, m_juntas]], 
                                             columns=["Data_Culto", "Nome_Culto", "Tema_Culto", "Musicas"])
            
            df_final_cultos = pd.concat([df_cultos, nova_linha_culto], ignore_index=True)
            conn.update(worksheet="Cultos", data=df_final_cultos)
            st.success("🎉 Escala gravada com sucesso no Google Sheets!")
            
            # Gerador de mensagem formatada para WhatsApp
            texto_formatado = f"*🛡️ GRUPO SHEKINÁ - NOVA ESCALA*\n\n"
            texto_formatado += f"📅 *Data:* {data_formatada}\n"
            texto_formatado += f"⛪ *Evento:* {tipo_evento}\n"
            texto_formatado += f"📖 *Tema:* {tema_evento}\n\n"
            texto_formatado += f"🎶 *REPERTÓRIO:*\n"
            for idx, musica in enumerate(setlist, 1):
                texto_formatado += f"  {idx}. {musica}\n"
            texto_formatado += f"\n_Acedam ao nosso App para consultar os tons e as cifras!_"
            
            link_whatsapp = f"https://wa.me/?text={urllib.parse.quote(texto_formatado)}"
            st.markdown(f'''
                <a href="{link_whatsapp}" target="_blank">
                    <button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:8px; font-weight:bold; cursor:pointer;">
                        📢 COMPARTILHAR ESCALA NO WHATSAPP DO GRUPO
                    </button>
                </a>
            ''', unsafe_allow_html=True)
        else:
            st.error("Por favor, preencha as informações e adicione ao menos uma música.")


# ================= TAB 2: CADASTRAR NOVO LOUVOR =================
with tab_novo_louvor:
    st.subheader("Adicionar Música ao Repertório Geral")
    st.markdown("Esta aba alimenta a lista de consulta geral dos músicos do instrumental.")
    
    with st.form("form_novo_louvor", clear_on_submit=True):
        col_m, col_a, col_t = st.columns([2, 2, 1])
        with col_m:
            nome_musica = st.text_input("Nome da Música:")
        with col_a:
            artista_musica = st.text_input("Artista / Ministério:")
        with col_t:
            tom_musica = st.text_input("Tom Sugerido:")
            
        col_an, col_ca = st.columns(2)
        with col_an:
            andamento_musica = st.selectbox("Andamento / Ritmo:", ["Lento", "Médio", "Rápido"])
        with col_ca:
            categoria_musica = st.text_input("Categoria / Tags:", placeholder="Ex: Adoração, Jovens, Varoes...")
            
        if st.form_submit_button("➕ Gravar no Repertório", use_container_width=True):
            if nome_musica and artista_musica:
                nova_musica_df = pd.DataFrame([[nome_musica, artista_musica, tom_musica, andamento_musica, categoria_musica]], 
                                               columns=["Musica", "Artista", "Tom", "Andamento", "Categoria"])
                
                df_louvores_limpo = df_louvores.drop(columns=['Musica_Busca'], errors='ignore')
                df_final_louvores = pd.concat([df_louvores_limpo, nova_musica_df], ignore_index=True)
                conn.update(worksheet="Louvores", data=df_final_louvores)
                st.success(f"🔥 Benção! '{nome_musica}' foi adicionada com sucesso ao Repertório Geral!")
            else:
                st.error("Por favor, preencha obrigatoriamente o Nome da Música e o Artista.")


# ================= TAB 3: CADASTRAR NOVA CIFRA =================
with tab_nova_cifra:
    st.subheader("Adicionar Cifra ou Link de Apoio")
    st.markdown("Esta aba alimenta os botões de redirecionamento que os músicos abrem na aba Cifras.")
    
    with st.form("form_nova_cifra", clear_on_submit=True):
        cifra_musica = st.text_input("Nome exato da Música:")
        cifra_artista = st.text_input("Artista / Ministério:")
        
        c_tom, c_tipo = st.columns(2)
        with c_tom:
            cifra_tom = st.text_input("Tom Padrão da Cifra:")
        with c_tipo:
            cifra_tipo = st.selectbox("Tipo de Link:", ["PDF", "Cifra Club", "Google Drive", "Vídeo Aula"])
            
        cifra_link = st.text_input("Cole o Link completo (URL):", placeholder="https://...")
        
        if st.form_submit_button("➕ Gravar na Biblioteca de Cifras", use_container_width=True):
            if cifra_musica and cifra_link:
                nova_cifra_df = pd.DataFrame([[cifra_musica, cifra_artista, cifra_tom, cifra_tipo, cifra_link]], 
                                              columns=["Musica", "Artista", "Tom_Padrao", "Tipo_Arquivo", "Link_Cifra"])
                
                df_final_cifras = pd.concat([df_cifras, nova_cifra_df], ignore_index=True)
                conn.update(worksheet="Cifras", data=df_final_cifras)
                st.success(f"📜 Glória a Deus! A cifra de '{cifra_musica}' já está disponível para o grupo!")
            else:
                st.error("Por favor, preencha o Nome da Música e insira o Link válido.")
