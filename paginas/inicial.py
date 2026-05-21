import streamlit as st

st.title("🏠 Página Inicial - Grupo Shekiná")
st.markdown(f"### Paz do Senhor, irmão {st.session_state.user_nome}! Benção ter você aqui conosco.")

# --- BOTÕES DE NAVEGAÇÃO RÁPIDA (CARDS NO MEIO DA TELA) ---
st.markdown("### 🚀 Atalhos Rápidos")

# Verificação de Perfil para saber quantas colunas criar no meio da tela
funcao_usuario = st.session_state.get('user_funcao', 'Integrante').lower().strip()

if funcao_usuario in ["líder", "lider", "leader"]:
    # Se for Líder, divide a tela em 4 colunas para caber o novo botão no meio
    col_prog, col_repertorio, col_cifras, col_lider = st.columns(4)
else:
    # Se for integrante comum, mantém as 3 colunas padrão
    col_prog, col_repertorio, col_cifras = st.columns(3)
    col_lider = None

# CARD 1: PROGRAMAÇÃO
with col_prog:
    st.markdown("""
    <div style="background-color: #0d47a1; padding: 15px; border-radius: 10px; text-align: center; border-left: 5px solid #ff6d00; min-height: 120px;">
        <h4 style="color: white; margin: 0;">📅 PROGRAMAÇÃO</h4>
        <p style="font-size: 13px; color: #e0e0e0; margin-top: 5px;">Escalas dos próximos cultos e ensaios</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("") 
    if st.button("Ver Próximos Cultos", use_container_width=True):
        st.switch_page("paginas/programacao.py")

# CARD 2: REPERTÓRIO
with col_repertorio:
    st.markdown("""
    <div style="background-color: #0d47a1; padding: 15px; border-radius: 10px; text-align: center; border-left: 5px solid #ffd600; min-height: 120px;">
        <h4 style="color: white; margin: 0;">🎵 REPERTÓRIO</h4>
        <p style="font-size: 13px; color: #e0e0e0; margin-top: 5px;">Lista completa de músicas do grupo</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("") 
    if st.button("Abrir Repertório Geral", use_container_width=True):
        st.switch_page("paginas/lista_musicas.py")

# CARD 3: CIFRAS
with col_cifras:
    st.markdown("""
    <div style="background-color: #0d47a1; padding: 15px; border-radius: 10px; text-align: center; border-left: 5px solid #1b5e20; min-height: 120px;">
        <h4 style="color: white; margin: 0;">📜 CIFRAS</h4>
        <p style="font-size: 13px; color: #e0e0e0; margin-top: 5px;">Links de cifras e tons para os músicos</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("") 
    if st.button("Abrir Biblioteca de Cifras", use_container_width=True):
        st.switch_page("paginas/cifras.py")

# CARD 4 EXCLUSIVO DO LÍDER (Só aparece no meio da tela para o seu perfil)
if col_lider is not None:
    with col_lider:
        st.markdown("""
        <div style="background-color: #4a148c; padding: 15px; border-radius: 10px; text-align: center; border-left: 5px solid #ff6d00; min-height: 120px;">
            <h4 style="color: white; margin: 0;">🛠️ GERENCIAR</h4>
            <p style="font-size: 13px; color: #e0e0e0; margin-top: 5px;">Cadastrar novos cultos e ensaios</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("") 
        if st.button("⚙️ Painel do Líder", use_container_width=True):
            st.switch_page("paginas/lider.py")

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
        st.session_state.auth = False
        st.session_state.user_nome = ""
        st.session_state.user_funcao = "Integrante"
        st.rerun()
