import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse

# Botão de retorno estilizado
if st.button("⬅️ Voltar para o Início"):
    st.switch_page("paginas/inicial.py")

st.title("🛠️ Painel Administrativo do Líder")
st.markdown("### Bem-vindo, Líder! Aqui você organiza as escalas e o repertório.")

conn = st.session_state.conn

# --- CARREGAMENTO DE DADOS ---
try:
    df_louvores = conn.read(worksheet="Louvores", ttl=0)
    df_louvores.columns = [c.strip() for c in df_louvores.columns]
except:
    st.error("Erro ao carregar a aba 'Louvores'. Verifique a planilha.")
    st.stop()

try:
    df_cultos = conn.read(worksheet="Cultos", ttl=0)
    df_cultos.columns = [c.strip() for c in df_cultos.columns]
except:
    df_cultos = pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Tema_Culto", "Musicas"])

# --- ORGANIZAÇÃO POR ABAS DENTRO DO PAINEL ---
tab_escala, tab_repertorio = st.tabs(["🎸 Montar Escala de Louvor", "➕ Gerenciar Repertório"])

with tab_escala:
    st.subheader("Cadastrar Novo Culto ou Ensaio")
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            tipo_evento = st.selectbox("Tipo de Compromisso:", ["Culto de Celebração", "Ensaio do Grupo", "Vigília", "Congresso", "Outro"])
            data_evento = st.date_input("Data do Evento:", date.today())
        with col2:
            tema_evento = st.text_input("Tema Central / Palavra:", placeholder="Ex: Santidade, Gratidão...")
            # Busca de músicas para a escala
            setlist_selecionada = st.multiselect("Selecione os Louvores (direto do repertório):", options=sorted(df_louvores['Musica'].tolist()))

    st.write("---")
    
    # Gerador de Mensagem para WhatsApp
    if st.button("💾 SALVAR PROGRAMAÇÃO E GERAR ESCALA"):
        if tipo_evento and setlist_selecionada:
            # 1. Salvar na Planilha
            data_formatada = data_evento.strftime('%d/%m/%y')
            nova_escala = pd.DataFrame([[data_formatada, tipo_evento, tema_evento, ", ".join(setlist_selecionada)]], 
                                        columns=["Data_Culto", "Nome_Culto", "Tema_Culto", "Musicas"])
            
            # Atualiza a aba 'Cultos' no Sheets
            df_atualizado = pd.concat([df_cultos, nova_escala], ignore_index=True)
            conn.update(worksheet="Cultos", data=df_atualizado)
            
            st.success("✅ Programação salva com sucesso na planilha!")
            
            # 2. Criar texto para WhatsApp
            texto_wa = f"*🛡️ GRUPO SHEKINÁ - ESCALA CONFIRMADA*\n\n"
            texto_wa += f"📅 *Data:* {data_formatada}\n"
            texto_wa += f"⛪ *Evento:* {tipo_evento}\n"
            texto_wa += f"📖 *Tema:* {tema_evento}\n\n"
            texto_wa += f"🎶 *LOUVORES SELECIONADOS:*\n"
            for i, musica in enumerate(setlist_selecionada, 1):
                texto_wa += f"{i}. {musica}\n"
            texto_wa += f"\n_Prestem atenção aos tons marcados no App! Deus abençoe._"
            
            # Botão de envio para WhatsApp
            link_wa = f"https://wa.me/?text={urllib.parse.quote(texto_wa)}"
            st.markdown(f'''
                <a href="{link_wa}" target="_blank">
                    <button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer;">
                        📢 ENVIAR ESCALA NO WHATSAPP DO GRUPO
                    </button>
                </a>
            ''', unsafe_allow_html=True)
        else:
            st.warning("Por favor, preencha o nome do evento e selecione ao menos uma música.")

with tab_repertorio:
    st.subheader("Adicionar Louvor ao Repertório Geral")
    with st.form("add_louvor", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1: nova_musica = st.text_input("Nome da Música:")
        with c2: novo_artista = st.text_input("Artista/Ministério:")
        with c3: novo_tom = st.text_input("Tom Sugerido:")
        
        if st.form_submit_button("➕ Cadastrar no Repertório"):
            if nova_musica and novo_artista:
                novo_item = pd.DataFrame([[nova_musica, novo_artista, novo_tom, "Média", "Geral"]], 
                                          columns=["Musica", "Artista", "Tom", "Andamento", "Categoria"])
                # Remove colunas de busca temporária se existirem
                df_louvores_limpo = df_louvores.drop(columns=['Musica_Busca'], errors='ignore')
                df_final = pd.concat([df_louvores_limpo, novo_item], ignore_index=True)
                conn.update(worksheet="Louvores", data=df_final)
                st.success(f"Música '{nova_musica}' adicionada ao repertório!")
            else:
                st.error("Preencha ao menos o nome da música e o artista.")

# Exibição do Histórico recente de cultos para o líder
st.write("---")
st.subheader("📋 Últimas Programações Lançadas")
st.dataframe(df_cultos.iloc[::-1], use_container_width=True, hide_index=True)
