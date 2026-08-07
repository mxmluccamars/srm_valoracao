# components/downloader.py

import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime

def _formatar_e_gerar_excel(df_n13p, ciclo):
    """
    Motor de formatação e geração de Excel, baseado na sua lógica.
    Recebe o DataFrame final e retorna os dados binários do arquivo .xlsx.
    """
    try:
        periodo = int(ciclo['periodo'])
        ano = int(ciclo['ano'])
            
        
        # --- ETAPA 1: ORDENAÇÃO DAS COLUNAS ---
        ordem_desejada_colunas = [
            # Colunas do Ciclo N13P
            'Tipo 1', 'Tipo 2', 'Tipo 3', 'Regional', 'GP', 'Vend.', 'Gerente', 'Rede', 'COD_CLIENTE',
            'Company Code', 'CD', 'NOME_CLIENTE', 'UF DESTINO', 'Região', 'EAN', 'SKU', 'Desc. SKU', 'Classificação',
            'Tech', 'Tech 2', 'Subbrand', 'Size', 'Nivel 3 HieraR', 'Marca',

            # Colunas de Produtos e Clientes
            'kg/Un',  'COND. PAG', 'COD REDE', 'COD SUBREDE', 'UF ORIGEM', 'COD GP', 'EAN Espelho', 'Family Price', 'Hierarquia', 'Class.', 'NCM', 'Origem', 
            'Ton/CDA', 'Unid/CX', 'LSV',

            # ZP55 
            'ZP55', 'ZP55 CLIENTE', 'ZP55 CLIENTE H05', 'ZP55 CD + UF DESTINO + Importação', 'ZP55 CD + UF DESTINO + NCM', 'ZP55 CD + UF DESTINO + H05',

            # ZP54 
            'ZP54', 'ZP54 CLIENTE', 'ZP54 REDE', 'ZP54 GP UF HIER 6', 'ZP54 GP UF HIER 5', 

            # GSV
            'GSV/CDA', 'GSV/TON',
            
            # ZP53
            'ZP53', 'ZP53 EMISSOR', 'ZP53 REDE', 'ZP53 GP UF', 'ZP53 GP', 
            'ZP53d','ZP53d EMISSOR', 'ZP53d REDE', 'ZP53d GP UF', 'ZP53d GP',

            # ZP52 
            'ZP52', 'ZP52 H04', 'ZP52 H01',

            # ZP73 e ZP70
            'ZP73', 'ZP73 CLIENTE', 'ZP73 REDE', 'ZP70',

            # ZP39
            'ZP39', 'ZP39 Emissor H12', 'ZP39 Emissor H10', 'ZP39 Subrede H12', 'ZP39 GP UF H12', 
            'ZP39d','ZP39d Emissor H12', 'ZP39d Emissor H10', 'ZP39d Subrede H12', 'ZP39d GP UF H12',

            # NIV
            'NIV/CDA', 'NIV/TON',

            # Impostos
            'ICMS', 'PIS', 'COFINS', 'NF PRAZO/CDA', 'NF PRAZO/TON'
        ]

        df_n13p_exportar = df_n13p.copy()

        colunas_presentes = [col for col in ordem_desejada_colunas if col in df_n13p_exportar.columns]
        colunas_faltantes = [col for col in df_n13p_exportar.columns if col not in colunas_presentes]

        ordem_final_colunas = colunas_presentes + colunas_faltantes
        df_n13p_ordenado = df_n13p_exportar[ordem_final_colunas]

    except Exception as e:
        raise Exception(f"Erro ao ordenar as colunas: {str(e)}")

    # --- ETAPA 2: DEFINIÇÃO DAS CATEGORIAS DE ESTILO ---
    try:
        # Categorias de colunas para estilização
        col_branco = [
            'Tipo 1', 'Tipo 2', 'Tipo 3', 'Regional', 'GP', 'Vend.', 'Gerente', 'Rede', 'COD_CLIENTE',
            'Company Code', 'CD', 'NOME_CLIENTE', 'UF DESTINO', 'Região', 'EAN', 'SKU', 'Desc. SKU', 'Classificação',
            'Tech', 'Tech 2', 'Subbrand', 'Size', 'Nivel 3 HieraR', 'Marca'
        ]
        col_roxo = [
            'COND. PAG', 'COD REDE', 'COD SUBREDE', 'COD GP', 'Family Price', 'Hierarquia', 
            'Class.', 'NCM', 'Origem', 'kg/Un', 'Ton/CDA', 'Unid/CX', 'LSV', 'UF ORIGEM'
        ]
        col_vermelho = 'EAN Espelho'

        col_azul = ['ZP55', 'ZP54', 'ZP53', 'ZP53d', 'ZP52', 'ZP73', 'ZP70', 'ZP39', 'ZP39d', 'ICMS', 'PIS', 'COFINS', 'NF PRAZO/CDA', 'NF PRAZO/TON']

        col_agua = ['GSV/CDA', 'GSV/TON', 'NIV/CDA', 'NIV/TON']

        col_cinza = [
            # ZP55
            'ZP55 CLIENTE', 'ZP55 CLIENTE H05', 'ZP55 CD + UF DESTINO + Importação', 'ZP55 CD + UF DESTINO + NCM', 'ZP55 CD + UF DESTINO + H05',
            # ZP54
            'ZP54 CLIENTE', 'ZP54 REDE', 'ZP54 GP UF HIER 6', 'ZP54 GP UF HIER 5',
        ]
        col_c_escuro = [
            # ZP53
            'ZP53 EMISSOR', 'ZP53 REDE', 'ZP53 GP UF', 'ZP53 GP', 'ZP53d EMISSOR', 'ZP53d REDE', 'ZP53d GP UF', 'ZP53d GP',
            # ZP52
            'ZP52 H04', 'ZP52 H01',
            # ZP73
            'ZP73 CLIENTE', 'ZP73 REDE',
            # ZP39
            'ZP39 Emissor H12', 'ZP39 Emissor H10', 'ZP39 Subrede H12', 'ZP39 GP UF H12',
            'ZP39d Emissor H12', 'ZP39d Emissor H10', 'ZP39d Subrede H12', 'ZP39d GP UF H12']

        col_int = ['Unid/CX',]
        col_2d = ['kg/Un', 'LSV',]
        col_2d = col_2d + col_cinza + col_c_escuro + col_azul
        col_8d = col_agua
    except Exception as e:
        raise Exception(f"Erro ao definir as categorias de estilo: {str(e)}")

    
    # --- ETAPA 3: GERAÇÃO DO EXCEL EM MEMÓRIA ---
    try:
        # nome do arquivo final
        nome_arquivo_formatado = f'N13_P{periodo:02d}_{ano}.xlsx'

        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        
        total_linhas = len(df_n13p_ordenado)
        tamanho_chunk = 50000

        # Feedback visual para o usuário
        st.write(f"Iniciando a formatação de {total_linhas:,} linhas...")
        progress_bar = st.progress(0)
        status_text = st.empty()

        # --- ETAPA 4: ESCRITA EM CHUNKS (COM BARRA DE PROGRESSO) ---
        for i in range(0, total_linhas, tamanho_chunk):
            chunk = df_n13p_ordenado.iloc[i : i + tamanho_chunk]
            if i == 0:
                chunk.to_excel(writer, sheet_name='Valoracao', index=False, startrow=8, header=True)
            else:
                chunk.to_excel(writer, sheet_name='Valoracao', index=False, startrow=i + 9, header=False)
            
            # Atualiza a barra de progresso
            linhas_processadas = min(i + tamanho_chunk, total_linhas)
            porcentagem = int((linhas_processadas / total_linhas) * 100)
            progress_bar.progress(porcentagem)
            status_text.text(f"Formatando linhas: {linhas_processadas:,} de {total_linhas:,} ({porcentagem}%)")

    except Exception as e:
        raise Exception(f"Erro ao processar os dados em chunks: {str(e)}")
    
    # --- ETAPA 5: APLICAÇÃO DOS ESTILOS (SEU CÓDIGO) ---
    try:
        workbook  = writer.book
        worksheet = writer.sheets['Valoracao']

        # adiciona linhas vazias acima da planilha
        worksheet.autofilter(8, 0, total_linhas + 8, len(df_n13p_ordenado.columns) - 1)

        # esconde as linhas verticais
        worksheet.hide_gridlines(2)

        # estilos de formatação
        estilo_header = {
            'bold': True, 'top': 1, 'top_color': '#000000', 
            'align': 'left', 'valign': 'vcenter', 
            'font_name': 'Mars Centra'}

        # estilos de formatação de colunas
        fmt_branco   = workbook.add_format({**estilo_header, 'bg_color': '#FFFFFF', 'font_color': '#000000'})
        fmt_roxo     = workbook.add_format({**estilo_header, 'bg_color': "#A02B93", 'font_color': "#FFFFFF"})
        fmt_vermelho = workbook.add_format({**estilo_header, 'bg_color': "#FF0000", 'font_color': "#FFFFFF"})
        fmt_azul     = workbook.add_format({**estilo_header, 'bg_color': "#0070C0", 'font_color': "#FFFFFF"})
        fmt_cinza    = workbook.add_format({**estilo_header, 'bg_color': "#D9D9D9", 'font_color': "#000000"})
        fmt_c_escuro = workbook.add_format({**estilo_header, 'bg_color': "#808080", 'font_color': "#FFFFFF"})
        fmt_agua     = workbook.add_format({**estilo_header, 'bg_color': "#CAEDFB", 'font_color': "#000000"})
        fmt_verde    = workbook.add_format({**estilo_header, 'bg_color': "#06E92C", 'font_color': "#000000"})

        # divisão dos dados de base ciclo N13P
        col_n13p_fim = 'Marca'
        fmt_header_n13p_fim    = workbook.add_format({**estilo_header, 'bg_color': '#FFFFFF', 'font_color': '#000000', 'right': 1, 'right_color': '#000000'})
        fmt_n13p_fim           = workbook.add_format({'right': 1, 'right_color': '#000000'})

        # formatação das linhas
        fmt_texto_padrao   = workbook.add_format({'font_name': 'Aptos Narrow'})
        fmt_integer_2 = workbook.add_format({'font_name': 'Aptos Narrow', 'num_format': '0'})
        fmt_decimal_2 = workbook.add_format({'font_name': 'Aptos Narrow', 'num_format': '0.00'})
        fmt_decimal_8 = workbook.add_format({'font_name': 'Aptos Narrow', 'num_format': '0.00000000'})

        for col_num, col_nome in enumerate(df_n13p_ordenado.columns):
            if col_nome in col_branco:
                formato = fmt_branco
            elif col_nome in col_roxo:
                formato = fmt_roxo
            elif col_nome == col_vermelho:
                formato = fmt_vermelho
            elif col_nome in col_azul:
                formato = fmt_azul
            elif col_nome in col_agua:
                formato = fmt_agua
            elif col_nome in col_cinza:
                formato = fmt_cinza
            elif col_nome in col_c_escuro:
                formato = fmt_c_escuro
            elif col_nome.startswith('GSV R$'):
                formato = fmt_branco
            elif col_nome == col_n13p_fim:
                formato = fmt_header_n13p_fim
            else:
                formato = fmt_branco

            worksheet.write(8, col_num, col_nome, formato)

            # largura da coluna
            max_comprimento_dados = df_n13p_ordenado[col_nome].head(30000).astype(str).str.len().max()
            largura = max(len(col_nome), max_comprimento_dados) + 5
            largura = min(largura, 50)
            largura = max(largura, 12)

            # formatação de numeros
            if col_nome in col_2d and df_n13p_ordenado[col_nome].dtype in [np.float64, np.float32]:
                worksheet.set_column(col_num, col_num, largura, fmt_decimal_2)
            elif col_nome in col_8d and df_n13p_ordenado[col_nome].dtype in [np.float64, np.float32]:
                worksheet.set_column(col_num, col_num, largura, fmt_decimal_8)
            elif col_nome in col_int and df_n13p_ordenado[col_nome].dtype in [np.int64, np.int32]:
                worksheet.set_column(col_num, col_num, largura, fmt_integer_2)
            elif col_nome == col_n13p_fim:
                worksheet.set_column(col_num, col_num, largura, fmt_n13p_fim)
            else:
                worksheet.set_column(col_num, col_num, largura, fmt_texto_padrao)


        status_text.text("✅ Planilha formatada com sucesso!")

    except Exception as e:
        raise Exception(f"Erro ao aplicar os estilos: {str(e)}")
    
    try:
        writer.close()
    except Exception as e:
        raise Exception(f"Erro ao fechar o arquivo .xlsx: {str(e)}")



    try:
        return output.getvalue()
    except Exception as e:
        raise Exception(f"Erro ao gerar o arquivo .xlsx: {str(e)}")
def render_downloader(df_resultado, ciclo):
    """
    Componente principal que chama o motor de formatação e mostra o botão.
    """
    st.subheader("📥 Download do Resultado")
    st.write("Clique no botão abaixo para baixar a planilha final com formatação executiva.")

    # Usamos um 'placeholder' para o botão, que só aparecerá depois de gerado o arquivo
    download_placeholder = st.empty()

    if st.button("Preparar Arquivo para Download", type="primary", use_container_width=True):
        with st.spinner("Motor de formatação em execução... Este processo pode ser demorado."):
            # Chama o motor de formatação
            excel_data = _formatar_e_gerar_excel(df_resultado, ciclo)

            # Define o nome do arquivo dinamicamente
            nome_arquivo = f"Resultado SPIM - P{ciclo['periodo']}_{ciclo['ano']}.xlsx"
            
            # Renderiza o botão de download real no placeholder
            download_placeholder.download_button(
                label="Clique Aqui para Baixar Agora",
                data=excel_data,
                file_name=nome_arquivo,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
