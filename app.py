# app.py

import streamlit as st

# Importa os componentes que vamos (re)construir
from components.config_styles import apply_global_styles
from components.header import render_header
from components.uploader import render_uploader
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

# Exemplo de como o estado mudará no futuro:
# if pronto_para_processar and st.session_state.app_state == 'INITIAL':
    # st.session_state.app_state = 'READY_TO_PROCESS'
    # st.rerun() # O st.rerun() força a atualização da página para refletir o novo estado










