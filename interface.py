from datetime import timedelta
import streamlit as st
from game_logic import interrogar_personagem, gerar_resumo, avaliar_teoria
import random

# Estilos CSS personalizados
def aplicar_estilos():
    st.markdown("""
    <style>
    /* Tema escuro com toques de vermelho */
    :root {
        --primary: #ff4b4b;
        --secondary: #6d6d6d;
        --background: #121212;
        --card-bg: #1e1e1e;
        --text: #ffffff;
        --success: #4caf50;
        --warning: #ff9800;
        --danger: #f44336;
    }
    
    body {
        background-color: var(--background);
        color: var(--text);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Cabeçalhos */
    h1, h2, h3, h4, h5, h6 {
        color: var(--primary) !important;
        border-bottom: 1px solid var(--secondary);
        padding-bottom: 8px;
    }
    
    /* Botões */
    .stButton>button {
        background-color: var(--primary);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
        margin: 5px 0;
        width: 100%;
    }
    
    .stButton>button:hover {
        background-color: black;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: var(--card-bg);
        border-radius: 8px;
        padding: 10px 20px;
        margin: 0 2px;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #2a2a2a;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary);
        color: white !important;
    }
    
    /* Cards */
    .custom-card {
        background-color: var(--card-bg);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    
    
    /* Pistas */
    .pista-card {
        background: #2c2c54;
        border-left: 4px solid var(--primary);
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
    }
    
    /* Inputs */
    .stTextInput>div>div>input {
        background-color: #2d3436;
        color: white;
        border: 1px solid var(--secondary);
        border-radius: 8px;
    }
    
    /* Mensagens */
    .stAlert {
        border-radius: 8px;
    }
    
    .stSuccess {
        background-color: rgba(76, 175, 80, 0.2) !important;
        border-color: var(--success) !important;
    }
    
    .stError {
        background-color: rgba(244, 67, 54, 0.2) !important;
        border-color: var(--danger) !important;
    }
    
    .stInfo {
        background-color: rgba(33, 150, 243, 0.2) !important;
        border-color: #2196f3 !important;
    }
    
    .stWarning {
        background-color: rgba(255, 152, 0, 0.2) !important;
        border-color: var(--warning) !important;
    }
    
    /* Botões de ação */
    .action-button {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

def mostrar_tela_inicial():
    aplicar_estilos()
    
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.title("🕵️‍♂️ Detetives da Vez")
    st.markdown("""
    **Resolva um mistério único gerado por IA!**
    - Interrogue suspeitos
    - Colete pistas
    - Descubra o culpado
    """)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.image("https://images.unsplash.com/photo-1549082984-1323b94df9a6?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80", 
             caption="Cena do crime", use_column_width=True)
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("⚙️ Modo de Jogo")
            modo = st.radio("", ["Normal", "Rápido (10 min)", "Clássico"], label_visibility="collapsed")
        with col2:
            st.subheader("👤 Jogadores")
            nomes = st.text_input("Nomes (separados por vírgula):", label_visibility="collapsed")
    
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    if st.button("▶️ Começar Novo Caso", use_container_width=True, type="primary"):
        st.session_state.modo_jogo = "rapido" if "Rápido" in modo else "classico" if "Clássico" in modo else "normal"
        st.session_state.jogadores = [n.strip() for n in nomes.split(",")] if nomes else []
        st.session_state.caso = None  # Será gerado
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def mostrar_caso(caso):
    aplicar_estilos()
    
    # Cabeçalho do caso
    st.markdown(f"<div class='custom-card'><h1>🔍 Caso: {caso['titulo']}</h1></div>", unsafe_allow_html=True)
    
    with st.expander("ℹ️ Introdução do Caso", expanded=True):
        st.markdown(f"<div style='padding: 15px;'>{caso['introducao']}</div>", unsafe_allow_html=True)
    
    # Layout principal com abas
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Explorar Locais", "👥 Interrogar Suspeitos", "📝 Pistas Coletadas", "🧠 Painel do Detetive"])
    
    with tab1:
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.subheader("Locais para Investigar")
        st.caption("Clique em um local para explorar e procurar pistas.")
        
        cols = st.columns(2)
        for i, local in enumerate(caso['locais']):
            with cols[i % 2]:
                if st.button(f"🔍 {local['nome']}", key=f"loc_{local['nome']}", use_container_width=True):
                    st.session_state.local_atual = local
        st.markdown("</div>", unsafe_allow_html=True)
                
        if st.session_state.local_atual:
            st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
            st.subheader(f"🔎 {st.session_state.local_atual['nome']}")
            st.write(st.session_state.local_atual['descricao'])
            
            # Botões para ações no local
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔦 Procurar pistas", key="procurar_pistas", use_container_width=True):
                    # Encontra uma pista não descoberta associada a este local
                    pistas_local = [p for p in caso['pistas'] if p['local'] == st.session_state.local_atual['nome']]
                    if pistas_local:
                        pista = random.choice(pistas_local)
                        if pista not in st.session_state.pistas_descobertas:
                            st.session_state.pistas_descobertas.append(pista)
                            st.toast(f"🔎 Pista encontrada: {pista['descricao'][:50]}...")
                    else:
                        st.warning("Nenhuma pista encontrada aqui.")
            with col2:
                if st.button("↩️ Voltar", key="voltar_local", use_container_width=True):
                    st.session_state.local_atual = None
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.subheader("Lista de Suspeitos")
        st.caption("Clique em um suspeito para interrogar.")
        
        cols = st.columns(2)
        for i, personagem in enumerate(caso['personagens']):
            with cols[i % 2]:
                emoji = "👤"
                if personagem.get('culpado', False):
                    emoji = "🔪"
                elif "governant" in personagem['descricao'].lower():
                    emoji = "🧹"
                elif "jardineir" in personagem['descricao'].lower():
                    emoji = "🌿"
                    
                if st.button(f"{emoji} {personagem['nome']}", key=f"char_{personagem['nome']}", use_container_width=True):
                    st.session_state.suspeito_atual = personagem
        st.markdown("</div>", unsafe_allow_html=True)
                
        if st.session_state.suspeito_atual:
            st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
            p = st.session_state.suspeito_atual
            st.subheader(f"🎭 {p['nome']}")
            st.caption(p['descricao'])
            
            # Campo para perguntas
            pergunta = st.text_input("Faça uma pergunta:", key="pergunta_input", placeholder="Onde você estava na noite do crime?")
            
            if pergunta:
                with st.spinner(f"{p['nome']} está pensando..."):
                    resposta = interrogar_personagem(p['nome'], pergunta, caso)
                
                # Resposta com estilo
                st.markdown(f"""
                <div style="background: #2d3436; border-radius: 10px; padding: 15px; margin-top: 15px;">
                    <div style="color: var(--primary); font-weight: bold;">{p['nome']}:</div>
                    <div style="margin-top: 8px;">{resposta}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Registrar interrogatório
                if p['nome'] not in st.session_state.interrogatorios:
                    st.session_state.interrogatorios[p['nome']] = []
                st.session_state.interrogatorios[p['nome']].append({
                    "pergunta": pergunta,
                    "resposta": resposta
                })
                
            # Botão para voltar
            if st.button("↩️ Voltar para lista de suspeitos", key="voltar_suspeito", use_container_width=True):
                st.session_state.suspeito_atual = None
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.subheader("Pistas Encontradas")
        st.caption(f"Total de pistas: {len(st.session_state.pistas_descobertas)}")
        
        if not st.session_state.pistas_descobertas:
            st.info("🔍 Nenhuma pista encontrada ainda. Explore os locais!")
        else:
            for i, pista in enumerate(st.session_state.pistas_descobertas):
                emoji = "🔎"
                if not pista.get('verdadeira', True):
                    emoji = "❓"
                
                with st.expander(f"{emoji} Pista #{i+1}: {pista['descricao'][:50]}...", expanded=False):
                    st.markdown(f"**Local encontrado:** {pista.get('local', '?')}")
                    st.markdown(f"**Descrição completa:** {pista['descricao']}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab4:
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.subheader("Ferramentas do Detetive")
        
        # Resumo do caso
        with st.expander("📋 Solicitar Resumo do Caso", expanded=False):
            if st.button("🧠 Gerar Resumo", key="gerar_resumo", use_container_width=True):
                with st.spinner("Analisando o caso..."):
                    st.session_state.resumo = gerar_resumo(
                        caso, 
                        st.session_state.pistas_descobertas,
                        st.session_state.interrogatorios
                    )
            if "resumo" in st.session_state:
                st.subheader("Resumo do Caso")
                st.write(st.session_state.resumo)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Acusação
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        with st.expander("🚨 Fazer Acusação", expanded=False):
            st.warning("⚠️ Cuidado! Uma acusação incorreta pode custar o caso.")
            acusacao = st.text_input("Quem você acusa?", key="acusacao_input", placeholder="Nome do suspeito")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirmar Acusação", key="fazer_acusacao", type="primary", use_container_width=True):
                    if acusacao:
                        with st.spinner("Avaliando acusação..."):
                            st.session_state.resultado_acusacao = avaliar_teoria(acusacao, caso)
                    else:
                        st.error("Por favor, digite o nome do suspeito.")
            with col2:
                if st.button("❌ Cancelar", key="cancelar_acusacao", use_container_width=True):
                    st.session_state.resultado_acusacao = None
            
            if "resultado_acusacao" in st.session_state:
                st.divider()
                if "CORRETO" in st.session_state.resultado_acusacao:
                    st.success("🎉 Acusação Correta!")
                    st.session_state.fim_jogo = True
                else:
                    st.error("❌ Acusação Incorreta!")
                st.write(st.session_state.resultado_acusacao)
                
                if "CORRETO" in st.session_state.resultado_acusacao:
                    st.balloons()
        st.markdown("</div>", unsafe_allow_html=True)
        