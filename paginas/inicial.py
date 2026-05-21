import streamlit as st

st.title("🏠 Página Inicial - Grupo Shekiná")
st.markdown(f"### Paz do Senhor, irmão {st.session_state.user_nome}! Benção ter você aqui conosco.")

# --- BOTÕES DE NAVEGAÇÃO RÁPIDA (CARDS) ---
st.markdown("### 🚀 Atalhos Rápidos")
col_prog, col_repertorio, col_cifras = st.columns(3)

with col_prog:
    st.markdown("""
    <div style="background-color: #2e3b4e; padding: 15px; border-radius: 10px; text-align: center; border-left: 5px solid #3498db;">
        <h4>📅 PROGRAMAÇÃO</h4>
        <p style="font-size: 13px; color: #cccccc;">Escalas dos próximos cultos e ensaios</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ver Próximos Cultos", use_container_width=True):
        st.switch_page("paginas/programacao.py")

with col_repertorio:
    st.markdown("""
    <div style="background-color: #2e3b4e; padding: 15px; border-radius: 10px; text-align: center; border-left: 5px solid #2ecc71;">
        <h4>🎵 REPERTÓRIO</h4>
        <p style="font-size: 13px; color: #cccccc;">Lista completa de músicas do grupo</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Consultar Músicas", use_container_width=True):
        st.switch_page("paginas/lista_musicas.py")

with col_cifras:
    st.markdown("""
    <div style="background-color: #2e3b4e; padding: 15px; border-radius: 10px; text-align: center; border-left: 5px solid #9b59b6;">
        <h4>📜 CIFRAS</h4>
        <p style="font-size: 13px; color: #cccccc;">Links de cifras e tons para os músicos</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Abrir Biblioteca de Cifras", use_container_width=True):
        st.switch_page("paginas/cifras.py")

st.write("---")

# --- CONTEÚDO INFORMATIVO ---
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

st.write("---")

# --- BOTÃO DE SAIR (LOGOUT) ---
st.markdown("### 🚪 Segurança")
col_logout, col_vazio = st.columns([1, 2])

with col_logout:
    if st.button("🔴 Sair do Aplicativo", use_container_width=True):
        # Limpa as variáveis de autenticação da sessão
        st.session_state.auth = False
        st.session_state.user_funcao = "Integrante"
        st.session_state.user_nome = ""
        # Limpa o carrinho de músicas se houver
        if 'cart' in st.session_state:
            st.session_state.cart = []
        
        st.success("Sessão encerrada com sucesso! Redirecionando...")
        st.rerun()
