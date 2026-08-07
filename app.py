# app.py

import streamlit as st
import pandas as pd
from components.header import render_header
from components.uploader import render_uploader
from components.downloader import render_downloader
from motor_valoracao import executar_motor_valoracao

# Inicializa o session_state se ele não existir
if 'df_resultado' not in st.session_state:
    st.session_state['df_resultado'] = None

render_header()
pronto, arquivos, ciclo = render_uploader()
st.markdown("---")

if pronto:
    if st.button("🚀 Processar e Calcular Dados", type="primary", use_container_width=True):
        try:
            with st.spinner("Motor de valoração em execução... Isso pode levar alguns minutos."):
                # Executa o motor e SALVA O RESULTADO NO SESSION_STATE
                st.session_state['df_resultado'] = executar_motor_valoracao(arquivos, ciclo)

            st.balloons()
            st.success("🎉 Processamento do motor concluído com sucesso!")
        except Exception as e:
            st.error(f"❌ Ocorreu um erro crítico durante o processamento: {str(e)}")
            st.session_state['df_resultado'] = None # Limpa em caso de erro

# -------------------------------------------------------------------
# LÓGICA DE EXIBIÇÃO E DOWNLOAD (AGORA FORA DO BOTÃO)
# -------------------------------------------------------------------
# Se o resultado já foi calculado e está na memória, mostra a prévia e o downloader
if st.session_state['df_resultado'] is not None:
    st.markdown("### 📊 Amostra dos Dados Processados")
    st.dataframe(st.session_state['df_resultado'].head(50), use_container_width=True)
    st.markdown("---")
    
    # Chama o componente de download, que também usará o session_state
    render_downloader(st.session_state['df_resultado'], ciclo)

elif pronto:
    # Mensagem para guiar o usuário se os arquivos estão prontos, mas o processamento não foi rodado
    st.info("💡 Tudo pronto! Clique no botão acima para iniciar os cálculos.")
else:
    # Mensagem inicial
    st.info("💡 Por favor, carregue todos os arquivos necessários na dashboard acima.")
