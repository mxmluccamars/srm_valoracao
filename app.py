# app.py

import streamlit as st

# Importamos as funções que criamos dentro da pasta components
from components.header import render_header
from components.uploader import render_uploader

# 1. Renderiza o cabeçalho (Título, regras, etc)
render_header()

# 2. Renderiza a área de upload de arquivos e captura a lista de arquivos enviados
pronto, arquivos, ciclo  = render_uploader()

# 3. Lógica do Botão de Processamento
st.markdown("---") # Linha divisória

# O botão só aparecerá se 'pronto' for True
if pronto:
    if st.button("🚀 Processar e Calcular Dados", type="primary"):
        st.write(f"Iniciando processamento para o Período {ciclo['periodo']} do Ano {ciclo['ano']}")
        # ... lógica de cálculo ...
else:
    st.info("Por favor, carregue os arquivos e garanta que o nome do arquivo principal contenha o período (ex: 'Ciclo P08 N13P.xlsx').")