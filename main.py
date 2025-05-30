import streamlit as st
from state_manager import reset_game_state
from game_logic import gerar_caso
from interface import mostrar_tela_inicial, mostrar_caso
import time

# Inicialização
if 'caso' not in st.session_state:
    reset_game_state()

# Fluxo principal
if st.session_state.caso is None:
    if st.session_state.get('modo_jogo') is not None:
        try:
            with st.spinner("🧠 Criando um mistério único..."):
                st.session_state.caso = gerar_caso(
                    st.session_state.modo_jogo,
                    st.session_state.jogadores
                )
                st.session_state.fim_jogo = False
            st.rerun()
        except Exception as e:
            st.error(f"🔍 Erro ao gerar caso: {str(e)}")
            st.button("🔄 Tentar novamente", on_click=lambda: st.session_state.update(caso=None))
    else:
        mostrar_tela_inicial()
else:
    if st.session_state.fim_jogo:
        st.success("🎉 Caso resolvido com sucesso!")
        st.write(st.session_state.resultado_acusacao)
        st.button("🔄 Novo Jogo", on_click=reset_game_state)
    else:
        mostrar_caso(st.session_state.caso)