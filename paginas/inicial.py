import streamlit as st

st.title("🏠 Página Inicial - Grupo Shekiná")
st.markdown(f"### Paz do Senhor, irmão {st.session_state.user_nome}! Benção ter você aqui conosco.")

col_info, col_devocional = st.columns([1, 1])

with col_info:
    st.info("""
    📢 **Avisos Importantes:**
    * Mantenham o repertório ensaiado e fiquem atentos às escalas na aba **Programação**.
    * Qualquer alteração de tom, comunique o instrumental com antecedência.
    * Deus abençoe o seu ministério! 🙏
    """)
    
with col_devocional:
    st.subheader("🌅 Palavra Devocional")
    if 'dev_final' in st.session_state:
        st.write(st.session_state.dev_final)
    else:
        st.write("O líder ainda não gerou a palavra oficial para a próxima escala. Fique conectado!")
