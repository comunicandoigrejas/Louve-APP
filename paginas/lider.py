import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse

# Botão de retorno no topo
if st.button("⬅️ Voltar para a Página Inicial"):
    st.switch_page("paginas/inicial.py")

st.title("🛠️ Painel de Controle do Líder")

conn = st.session_state.conn
client = st.session_state.openai_client

try:
    df_l = conn.read(worksheet="Louvores", ttl=0)
    df_l.columns = [c.strip() for c in df_l.columns]
    df_l['Musica_Busca'] = df_l['Musica'].fillna('').astype(str).str.lower().str.strip()
except: df_l = pd.DataFrame(columns=["Musica", "Artista", "Tom", "Andamento", "Categoria", "Musica_Busca"])

try:
    df_h = conn.read(worksheet="Cultos", ttl=0)
    df_h.columns = [c.strip() for c in df_h.columns]
except: df_h = pd.DataFrame(columns=["Data_Culto", "Nome_Culto", "Tema_Culto", "Musicas"])

t1, t2, t3, t4, t5 = st.tabs(["🎸 Montar Escala", "➕ Cadastrar Louvor", "🗑️ Excluir Louvor", "📜 Histórico de Cultos", "🌅 Devocional IA"])

# (O restante do código da aba do Líder permanece igual ao anterior)
with t1:
    st.subheader("Montar Nova Programação")
    busca_lider = st.text_input("🔍 Pesquisar louvor para adicionar:").lower()
    df_f_lider = df_l[df_l['Musica_Busca'].str.contains(busca_lider)] if busca_lider else df_l
    sel = st.dataframe(df_f_lider[["Musica", "Artista"]], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
    
    st.write("---")
    c1, c2 = st.columns(2)
    with c1:
        nome_c = st.text_input("Tipo de Culto / Compromisso:")
        data_c = st.date_input("Data do Evento:", date.today())
    with c2:
        tema_c = st.text_input("Tema Central:")
        if 'cart' not in st.session_state: st.session_state.cart = []
        if sel.selection.rows:
            for m in df_f_lider.iloc[sel.selection.rows]['Musica'].tolist():
                if m not in st.session_state.cart: st.session_state.cart.append(m)
        final_list = st.multiselect("Setlist Confirmada:", options=sorted(df_l['Musica'].tolist()), default=[m for m in st.session_state.cart if m in df_l['Musica'].tolist()])
        st.session_state.cart = final_list

    if nome_c and final_list:
        dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        data_f = data_c.strftime('%d-%m-%y')
        dia_nome = dias[data_c.weekday()]
        msg_wa = f"A paz do senhor grupo segue os louvores do culto *{nome_c}* .......\n\n📅 *Data:* {data_f} ({dia_nome})\n📖 *Tema:* {tema_c}\n\n🎶 *LOUVORES:*\n"
        for i, m in enumerate(final_list, 1): msg_wa += f"{i}. {m}\n"
        msg_wa += "\n🔧 _By Comunicando Igrejas_"
        col_save, col_wa = st.columns(2)
        with col_save:
            if st.button("💾 PUBLICAR E SALVAR PROGRAMAÇÃO"):
                novo = pd.DataFrame([[data_f, nome_c, tema_c, ", ".join(final_list)]], columns=["Data_Culto", "Nome_Culto", "Tema_Culto", "Musicas"])
                conn.update(worksheet="Cultos", data=pd.concat([df_h, novo], ignore_index=True))
                st.success("✅ Programação gravada!")
        with col_wa:
            link_wa = f"https://wa.me/?text={urllib.parse.quote(msg_wa)}"
            st.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">📢 ENVIAR NO WHATSAPP</button></a>', unsafe_allow_html=True)

with t2:
    st.subheader("Cadastrar Novo Louvor no Repertório")
    with st.form("form_cad", clear_on_submit=True):
        nm, art, tom = st.text_input("Música:"), st.text_input("Artista:"), st.text_input("Tom:")
        if st.form_submit_button("Salvar Música"):
            if nm and art:
                df_atual = df_l.drop(columns=['Musica_Busca'], errors='ignore')
                novo_df = pd.DataFrame([[nm, art, tom, "Médio", "Geral"]], columns=["Musica", "Artista", "Tom", "Andamento", "Categoria"])
                conn.update(worksheet="Louvores", data=pd.concat([df_atual, novo_df], ignore_index=True))
                st.success("✅ Música cadastrada!")

with t3:
    st.subheader("🗑️ Remover Louvor do Repertório")
    excluir = st.selectbox("Selecione para remover:", [""] + sorted(df_l['Musica'].tolist()))
    if excluir and st.button("Confirmar Exclusão"):
        df_restante = df_l[df_l['Musica'] != excluir].drop(columns=['Musica_Busca'], errors='ignore')
        conn.update(worksheet="Louvores", data=df_restante)
        st.success(f"Música '{excluir}' removida.")
        st.rerun()

with t4:
    st.subheader("📜 Histórico de Escalas Publicadas")
    st.dataframe(df_h.iloc[::-1], use_container_width=True, hide_index=True)

with t5:
    st.subheader("🌅 Gerador de Reflexões com IA")
    if st.button("✨ Gerar Reflexão Pastoral") and client:
        with st.spinner("Escrevendo..."):
            p = f"Escreva um devocional pentecostal de 200 palavras sobre o tema. Use a linguagem cristã carinhosa 'irmãos, benção, vindo da parte do Senhor'. Use emojis: 🙏, ✨, 📖."
            res = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": p}])
            st.session_state.dev_final = res.choices[0].message.content
    if 'dev_final' in st.session_state:
        st.write(st.session_state.dev_final)
        link_dev = f"https://wa.me/?text={urllib.parse.quote(st.session_state.dev_final + '\n\n🔧 _By Comunicando Igrejas_')}"
        st.markdown(f'<a href="{link_dev}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:8px; font-weight:bold; cursor:pointer;">📢 ENVIAR DEVOCIONAL</button></a>', unsafe_allow_html=True)
