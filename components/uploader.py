# components/uploader.py

import streamlit as st
import re
from datetime import datetime

def _desenhar_card_compacto(descricao, arquivo_encontrado=None):
    """Função auxiliar para desenhar um card de status menor e mais limpo."""
    if arquivo_encontrado:
        cor_borda = "#28A745"; icone = "✅"; nome_arquivo = f"`{arquivo_encontrado.name}`"
    else:
        cor_borda = "#FF1414"; icone = "❌"; nome_arquivo = "Aguardando..."
    st.markdown(f'<div style="border-left: 4px solid {cor_borda}; border-radius: 4px; padding: 8px 12px; background-color: #F8F9FA; font-family: sans-serif; margin-bottom: 10px; height: 75px; display: flex; flex-direction: column; justify-content: center;"><p style="margin: 0; padding: 0; font-weight: 600; color: #343A40; font-size: 14px;">{icone} {descricao}</p><small style="color: #6C757D; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{nome_arquivo}</small></div>', unsafe_allow_html=True)

def render_uploader():
    """
    Desenha uma dashboard de status com um grid 3x3 e uma fileira final com 2 cards centralizados.
    """
    ARQUIVOS_ESPERADOS = {'N13P': 'Ciclo N13P',
                        'BASE CLIENTES': 'Base de Dados de Clientes',
                        'BASE PRODUTOS': 'Base de Dados de Produtos',
                        'BASE IMPOSTOS': 'Base de Dados de Impostos',
                        'ZP55': 'ZP55',
                        'ZP54': 'ZP54',
                        'ZP53': 'ZP53',
                        'ZP52': 'ZP52',
                        'ZP73': 'ZP73',
                        'ZP70': 'ZP70',
                        'ZP39': 'ZP39',
                        }

    st.subheader("📂 Dashboard de Carregamento")
    arquivos_carregados = st.file_uploader("Selecione os arquivos...", type=["xlsx", "csv"], accept_multiple_files=True)
    st.markdown("---")

    # --- Lógica de Processamento e Extração de Dados (sem renderização) ---
    arquivos_encontrados = {}
    ciclo_final = None
    if arquivos_carregados:
        for nome_esperado in ARQUIVOS_ESPERADOS:
            for arquivo in arquivos_carregados:
                if nome_esperado in arquivo.name.upper():
                    arquivos_encontrados[nome_esperado] = arquivo
                    if nome_esperado == "N13P":
                        match = re.search(r'P(\d{2})', arquivo.name.upper())
                        if match:
                            periodo = match.group(1)
                            ano_atual = str(datetime.now().year)
                            ciclo_final = {"periodo": periodo, "ano": ano_atual}
                    break

    # --- Renderização do Grid 3x3 (os 9 primeiros cards) ---
    num_colunas_grid = 3
    colunas_grid = st.columns(num_colunas_grid)
    lista_arquivos_grid = list(ARQUIVOS_ESPERADOS.items())[:9]

    for i, (nome_esperado, descricao) in enumerate(lista_arquivos_grid):
        coluna_atual = colunas_grid[i % num_colunas_grid]
        with coluna_atual:
            _desenhar_card_compacto(descricao, arquivos_encontrados.get(nome_esperado))

    # --- Renderização da Fileira Final (os 2 últimos cards, centralizados) ---
    lista_arquivos_final = list(ARQUIVOS_ESPERADOS.items())[9:]
    if lista_arquivos_final:
        # Criamos colunas "falsas" nas laterais para empurrar as colunas reais para o centro
        col_vazia1, col_card1, col_card2, col_vazia2 = st.columns([0.5, 1.5, 1.5, 0.5])
        
        with col_card1:
            nome_esperado, descricao = lista_arquivos_final[0]
            _desenhar_card_compacto(descricao, arquivos_encontrados.get(nome_esperado))
        
        if len(lista_arquivos_final) > 1:
            with col_card2:
                nome_esperado, descricao = lista_arquivos_final[1]
                _desenhar_card_compacto(descricao, arquivos_encontrados.get(nome_esperado))

    # --- Status Final e Feedback ---
    pronto_para_processar = len(arquivos_encontrados) == len(ARQUIVOS_ESPERADOS) and ciclo_final is not None
    
    if arquivos_carregados or pronto_para_processar:
        if ciclo_final:
            st.success(f"Ciclo de processamento definido: **Período {ciclo_final['periodo']} / Ano {ciclo_final['ano']}**")
        elif "N13P" in arquivos_encontrados:
            st.error("Arquivo N13P carregado, mas não foi possível detectar o período (ex: P08) no nome.")

    return pronto_para_processar, arquivos_encontrados, ciclo_final

