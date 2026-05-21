import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse

# Botão de retorno seguro
if st.button("⬅️ Voltar para a Página Inicial"):
    st.switch_page("paginas/inicial.py")

st.title("🛠️ Cadastro de Cultos e Ensaios (Líder)")
st.markdown("Use este painel para atualizar a agenda do grupo e escalar os louvores.")

conn = st.session_state.conn

# Carrega o repertório de louvores cadastrados
try:
    df_louvores = conn.read(worksheet="Louvores", ttl=0)
    df_louvores.columns = [c.strip() for c in df_louvores.columns]
except:
    df_louvores = pd.DataFrame(columns=["Musica", "Artista", "Tom"])

# Carrega o histórico de cultos lançados
try:
    df_cultos = conn.read(worksheet="Cultos", ttl=0)
    df_cultos.columns = [c.strip() for c in df_cultos.columns]
except:
    df_cultos = pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Tema_Culto", "Musicas"])

# Abas de gerenciamento
tab_cadastro, tab_historico = st.tabs(["📅 Agendar Culto / Ensaio", "📋 Ver Agendas Salvas"])

with tab_cadastro:
    st.subheader("Nova Escala de Louvor")
    
    tipo_evento = st.selectbox("Selecione o Tipo de Evento:", ["Culto de Celebração", "Ensaio do Grupo", "Culto de Doutrina", "Vigília", "Festividade"])
    data_evento = st.date_input("Data marcada:", date.today())
    tema_evento = st.text_input("Tema Central ou Palavra da Noite:", placeholder="Ex: Gratidão, Fé, Santidade...")
    
    # Seleção múltipla baseada nas músicas existentes na planilha
    if not df_louvores.empty and 'Musica' in df_louvores.columns:
        lista_opcoes = sorted(df_louvores['Musica'].dropna().tolist())
        setlist = st.multiselect("Selecione as músicas para este dia:", options=lista_opcoes)
    else:
        st.warning("Nenhum louvor encontrado no repertório geral para seleção.")
        setlist = []
        
    st.write("---")
    
    if st.button("💾 SALVAR ESCALA NA PLANILHA", use_container_width=True):
        if tipo_evento and setlist:
            data_formatada = data_evento.strftime('%d/%m/%Y')
            m_juntas = ", ".join(setlist)
            
            # Monta a nova linha
            nova_linha = pd.DataFrame([[data_formatada, tipo_evento, tema_evento, m_juntas]], 
                                       columns=["Data_Culto", "Nome_Culto", "Tema_Culto", "Musicas"])
            
            # Une os dados antigos com o novo cadastro
            df_final_cultos = pd.concat([df_cultos, nova_linha], ignore_index=True)
            
            # Envia diretamente para a worksheet "Cultos" do Google Sheets
            conn.update(worksheet="Cultos", data=df_final_cultos)
            st.success("🎉 Escala gravada com sucesso no Google Sheets!")
            
            # Gera o texto formatado para o WhatsApp
            texto_formatado = f"*🛡️ GRUPO SHEKINÁ - NOVA ESCALA*\n\n"
            texto_formatado += f"📅 *Data:* {data_formatada}\n"
            texto_formatado += f"⛪ *Evento:* {tipo_evento}\n"
            texto_formatado += f"📖 *Tema:* {tema_evento}\n\n"
            texto_formatado += f"🎶 *REPERTÓRIO:*\n"
            for idx, musica in enumerate(setlist, 1):
                texto_formatado += f" {idx}. {musica}\n"
            texto_formatado += f"\n_Acedam ao nosso App para consultar os tons e as cifras!_"
            
            # Link de envio direto
            link_whatsapp = f"https://wa.me/?text={urllib.parse.quote(texto_formatado)}"
            st.markdown(f'''
                <a href="{link_whatsapp}" target="_blank">
                    <button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:8px; font-weight:bold; cursor:pointer;">
                        📢 COMPARTILHAR ESCALA NO WHATSAPP DO GRUPO
                    </button>
                </a>
            ''', unsafe_allow_html=True)
        else:
            st.error("Por favor, selecione pelo menos uma música para salvar a escala.")

with tab_historico:
    st.subheader("Histórico de Escalas Gravadas")
    if not df_cultos.empty:
        st.dataframe(df_cultos.iloc[::-1], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma escala gravada na tabela 'Cultos' até ao momento.")
