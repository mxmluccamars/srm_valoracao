# app.py

import streamlit as st

# Importa os componentes que vamos (re)construir
from components.config_styles import apply_global_styles
from components.header import render_header
from components.uploader import render_uploader
from components.actions import render_action_buttons
from motor_valoracao import executar_fluxo_completo
from components.downloader import render_download_section
# Futuramente, importaremos outros componentes aqui

# --- 1. CONFIGURAÇÃO INICIAL E MÁQUINA DE ESTADOS ---

# Aplica os estilos globais (fundo, fontes) e a configuração da página.
# Esta deve ser a PRIMEIRA chamada do Streamlit no seu script.
apply_global_styles()

# Inicializa o st.session_state na primeira vez que o app é executado
if 'app_state' not in st.session_state:
    st.session_state.app_state = 'INITIAL'      # Nosso estado inicial
    st.session_state.df_resultado = None      # Placeholder para os dados calculados
    st.session_state.excel_data = None        # Placeholder para o arquivo Excel final
    st.session_state.error_message = None     # Placeholder para mensagens de erro

# --- 2. RENDERIZAÇÃO DA INTERFACE (VERSÃO INICIAL) ---

# Desenha o header (próximo componente que vamos refazer)
render_header()

# Desenha a seção de upload de arquivos
# A função render_uploader() futuramente nos dirá se está tudo pronto para processar
pronto_para_processar, arquivos_carregados, ciclo_definido = render_uploader()

# Futuramente, aqui entrará a lógica de botões e transição de estados
# Por enquanto, apenas para teste, podemos mostrar o estado atual
st.write(f"Estado Atual da Página: **{st.session_state.app_state}**")

# Atualiza o estado quando os arquivos estão prontos
if  pronto_para_processar and st.session_state.app_state == 'INITIAL':
    st.session_state.app_state = 'READY_TO_PROCESS'
    st.rerun() # Força a atualização para habilitar o botão

# Renderiza os botões e captura se o de processar foi clicado
if render_action_buttons():
    # Se o botão foi clicado, muda o estado para PROCESSING
    st.session_state.app_state = 'PROCESSING'
    # O st.rerun() aqui é crucial para que na próxima execução,
    # o app entre na lógica de processamento.
    st.rerun()


# --- LÓGICA DE PROCESSAMENTO (será implementada a seguir) ---
if st.session_state.app_state == 'PROCESSING':
    try:
        with st.spinner("Executando fluxo completo... (Cálculos e Formatação do Relatório)"):
            # A função agora retorna AMBOS: o df para preview e o excel para download
            df_calculado, excel_final = executar_fluxo_completo(arquivos_carregados, ciclo_definido)
            st.session_state.df_resultado = df_calculado
            st.session_state.excel_data = excel_final
        
        st.session_state.app_state = 'DOWNLOAD_READY'
        st.rerun()
    except Exception as e:
        st.session_state.error_message = str(e)
        st.session_state.app_state = 'ERROR'
        st.rerun()


# --- 4. RENDERIZAÇÃO DAS SEÇÕES DE RESULTADO ---

# Se o download está pronto, chama o componente de download
if st.session_state.app_state == 'DOWNLOAD_READY':
    render_download_section(
        df_resultado=st.session_state.df_resultado,
        excel_data=st.session_state.excel_data,
        ciclo=ciclo_definido
    )

# Se deu erro, mostra a mensagem
if st.session_state.app_state == 'ERROR':
    st.error(f"❌ Ocorreu um erro crítico: {st.session_state.error_message}")











