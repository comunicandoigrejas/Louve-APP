import streamlit as st
import pandas as pd

# Botão de retorno no topo com estilo roxo
if st.button("⬅️ Voltar para a Página Inicial"):
    st.switch_page("paginas/inicial.py")

st.title("📅 Programação de Cultos e Ensaios")

# Estilização local para garantir os tons da identidade visual
st.markdown("""
    <style>
    .stSelectbox div[data-baseweb="select"] {
        border: 2px solid #0d47a1 !important; /* Azul Marinho */
    }
    div[data-testid="stExpander"] {
        border: 1px solid #4a148c !important; /* Roxo */
    }
    </style>
    """, unsafe_allow_html=True)

conn = st.session_state.conn

# Carrega os dados dos cultos salvos pelo líder
try:
    hist = conn.read(worksheet="Cultos", ttl=0)
    hist.columns = [c.strip() for c in hist.columns]
except: 
    hist = pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Tema_Culto", "Musicas"])

# Carrega o repertório de louvores para cruzar as informações
try:
    df_full = conn.read(worksheet="Louvores", ttl=0)
    df_full.columns = [c.strip() for c in df_full.columns]
except: 
    df_full = pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento"])

if not hist.empty:
    st.markdown("### 🔍 Selecione a Escala")
    op = (hist['Data_Culto'].astype(str) + " | " + hist['Nome_Culto']).tolist()[::-1]
    escolha = st.selectbox("Escolha o Culto ou Ensaio para ver o repertório:", op, label_visibility="collapsed")
    
    if escolha:
        dt, nm = escolha.split(" | ")
        reg = hist[(hist['Data_Culto'].astype(str) == dt) & (hist['Nome_Culto'] == nm)].iloc[0]
        
        # Card informativo em Azul com borda Laranja
        st.markdown(f"""
        <div style="background-color: #0d47a1; padding: 20px; border-radius: 10px; border-left: 6px solid #ff6d00; color: white; margin-bottom: 20px;">
            <h3 style='margin:0; color: white;'>⛪ {nm}</h3>
            <p style='margin: 5px 0 0 0; font-size: 16px;'>📅 <b>Data:</b> {dt} &nbsp;|&nbsp; 📖 <b>Tema Central:</b> {reg['Tema_Culto']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Exibição da lista de louvores
        m_list = [m.strip() for m in str(reg['Musicas']).split(", ")]
        st.markdown("### 🎶 Louvores Escalados")
        
        df_escala = df_full[df_full['Musica'].isin(m_list)][["Musica", "Artista", "Tom", "Andamento"]]
        
        if not df_escala.empty:
            st.dataframe(df_escala, use_container_width=True, hide_index=True)
        else:
            st.info("As músicas dessa escala ainda não foram detalhadas no repertório geral.")
            
        # Alerta em tom Verde abençoado lembrando os músicos
        st.markdown("""
        <div style="background-color: #1b5e20; padding: 12px; border-radius: 8px; color: white; text-align: center; font-weight: bold; margin-top: 15px;">
            📢 Atenção instrumental e vozes: Ensaiarem os tons marcados acima! Deus abençoe. 🙏
        </div>
        """, unsafe_allow_html=True)
else:
    # Mensagem em Amarelo caso não haja cultos lançados
    st.markdown("""
    <div style="background-color: #ffd600; padding: 15px; border-radius: 8px; color: black; font-weight: bold;">
        ⚠️ Nenhuma programação ou ensaio foi publicado pelo Líder no momento.
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# Devocional da Palavra usando a versão ARA pedida pelo irmão
st.subheader("📖 Palavra de Fortalecimento para o Grupo")
st.markdown("""
*Reflexão Baseada na Versão Bíblica ARA (Almeida Revista e Atualizada):* > **"Portanto, meus amados irmãos, sede firmes, inabaláveis e sempre abundantes na obra do Senhor, sabendo que, no Senhor, o vosso trabalho não é vão."** — *1 Coríntios 15:58*
""")
