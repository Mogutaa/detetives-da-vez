import streamlit as st

def init_session_state():
    return {
        'caso': None,
        'pistas_descobertas': [],
        'interrogatorios': {},
        'local_atual': None,
        'suspeito_atual': None,
        'modo_jogo': 'normal',
        'jogadores': [],
        'fim_jogo': False,
        'dica': None,
        'resumo': None,
        'resultado_acusacao': None
    }

def reset_game_state():
    # Lista de chaves a preservar (se necessário)
    chaves_preservar = []
    
    # Limpa todas as chaves exceto as especificadas
    for key in list(st.session_state.keys()):
        if key not in chaves_preservar:
            del st.session_state[key]
    
    # Inicializa o estado
    for key, value in init_session_state().items():
        st.session_state[key] = value