import streamlit as st
import pandas as pd

# Botão de retorno no topo
if st.button("⬅️ Voltar para a Página Inicial"):
    st.switch_page("paginas/inicial.py")

st.title("📜 Biblioteca de Cifras e Links")

conn = st.session_state.conn

try:
    df_cifras = conn.read(worksheet="Cifras", ttl=0)
    df_cifras.columns = [c.strip() for c in df_cifras.columns]
except: df_cifras = pd.DataFrame(columns=["Musica", "Artista", "Tom_Padrao", "Tipo_Arquivo", "Link_Cifra"])

if not df_cifras.empty:
    musica_sel = st.selectbox("Escolha a música para abrir a cifra:", [""] + sorted(df_cifras['Musica'].tolist()))
    
    if musica_sel:
        dados_cifra = df_cifras[df_cifras['Musica'] == musica_sel].iloc[0]
        st.success(f"🎶 **Música:** {dados_cifra['Musica']} | 🎤 **Artista:** {dados_cifra['Artista']} | 🎹 **Tom Padrão:** {dados_cifra['Tom_Padrao']}")
        
        link = dados_cifra['Link_Cifra']
        tipo = dados_cifra['Tipo_Arquivo']
        
        st.markdown(f'''
            <a href="{link}" target="_blank">
                <button style="background-color: #9b59b6; color: white; border: none; padding: 15px 32px; text-align: center; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 10px; font-weight: bold;">
                    📂 Abrir Cifra ({tipo})
                </button>
            </a>
        ''', unsafe_allow_html=True)
else:
    st.info("Nenhuma cifra cadastrada ainda na aba 'Cifras' do Google Sheets.")
