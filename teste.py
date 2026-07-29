# Célula 16 - Exportação Avançada 3.0 (Bordas Customizadas, Chunks e Fontes Mars Centra)
inicio_export = time.time()

# ==============================================================================
# 1. CATEGORIAS DE COLUNAS PARA ESTILIZAÇÃO
# ==============================================================================
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

col_azul = ['ZP55', 'ZP54', 'ZP53', 'ZP53d', 'ZP52', 'ZP73', 'ZP70', 'ZP39', 'ZP39d']

col_agua = ['GSV/CDA', 'GSV/TON', 'NIV/CDA', 'NIV/TON']

col_cinza = [
    'ZP55 CLIENTE', 'ZP55 CLIENTE H05', 'ZP55 CD + UF DESTINO + Importação', 'ZP55 CD + UF DESTINO + NCM', 'ZP55 CD + UF DESTINO + H05',
    'ZP54 CLIENTE', 'ZP54 REDE', 'ZP54 GP UF HIER 6', 'ZP54 GP UF HIER 5'
]

col_c_escuro = [
    'ZP53 EMISSOR', 'ZP53 REDE', 'ZP53 GP UF', 'ZP53 GP', 'ZP53d EMISSOR', 'ZP53d REDE', 'ZP53d GP UF', 'ZP53d GP',
    'ZP52 H04', 'ZP52 H01',
    'ZP73 CLIENTE', 'ZP73 REDE',
    'ZP39 Emissor H12', 'ZP39 Emissor H10', 'ZP39 Subrede H12', 'ZP39 GP UF H12',
    'ZP39d Emissor H12', 'ZP39d Emissor H10', 'ZP39d Subrede H12', 'ZP39d GP UF H12'
]

col_int = ['Unid/CX']
col_2d = ['kg/Un', 'LSV'] + col_cinza + col_c_escuro + col_azul
col_8d = col_agua


# ==============================================================================
# 2. ESCRITA EM CHUNKS (Rápida e Segura)
# ==============================================================================
nome_arquivo_formatado = 'N13_Final_2.0.xlsx'
writer = pd.ExcelWriter(nome_arquivo_formatado, engine='xlsxwriter')

total_linhas = len(df_n13p_ordenado)
print(f"📊 Total de linhas a serem salvas: {total_linhas:,}")

tamanho_chunk = 25000
for i in range(0, total_linhas, tamanho_chunk):
    chunk = df_n13p_ordenado.iloc[i : i + tamanho_chunk]
    if i == 0:
        chunk.to_excel(writer, sheet_name='Valoracao', index=False, startrow=0, header=True)
    else:
        chunk.to_excel(writer, sheet_name='Valoracao', index=False, startrow=i + 1, header=False)

workbook  = writer.book
worksheet = writer.sheets['Valoracao']


# ==============================================================================
# 3. CRIAÇÃO DE ESTILOS E FONTES CORPORATIVAS (Mars Centra)
# ==============================================================================
# Base de Estilos dos Cabeçalhos (sem bordas laterais por padrão para visual limpo)
estilo_header = {'bold': True, 'top': 1, 'bottom': 1, 'align': 'center', 'valign': 'vcenter', 'font_name': 'Mars Centra'}

# Cabeçalhos Coloridos
fmt_branco   = workbook.add_format({**estilo_header, 'bg_color': '#FFFFFF', 'font_color': '#000000'}) 
fmt_roxo     = workbook.add_format({**estilo_header, 'bg_color': "#A02B93", 'font_color': "#FFFFFF"})
fmt_vermelho = workbook.add_format({**estilo_header, 'bg_color': "#FF0000", 'font_color': "#FFFFFF"})
fmt_azul     = workbook.add_format({**estilo_header, 'bg_color': "#0070C0", 'font_color': "#FFFFFF"})
fmt_cinza    = workbook.add_format({**estilo_header, 'bg_color': "#D9D9D9", 'font_color': "#000000"})
fmt_c_escuro = workbook.add_format({**estilo_header, 'bg_color': "#808080", 'font_color': "#FFFFFF"})
fmt_agua     = workbook.add_format({**estilo_header, 'bg_color': "#CAEDFB", 'font_color': "#000000"})
fmt_verde    = workbook.add_format({**estilo_header, 'bg_color': "#06E92C", 'font_color': "#000000"})

# Formatos de Borda de Cabeçalho Especiais para o "Box" do N13P
fmt_header_n13p_inicio = workbook.add_format({**estilo_header, 'bg_color': '#FFFFFF', 'font_color': '#000000', 'left': 1})
fmt_header_n13p_meio   = workbook.add_format({**estilo_header, 'bg_color': '#FFFFFF', 'font_color': '#000000'})
fmt_header_n13p_fim    = workbook.add_format({**estilo_header, 'bg_color': '#FFFFFF', 'font_color': '#000000', 'right': 1})

# Formatos para Células de Dados (Corpo da Planilha)
fmt_texto_padrao   = workbook.add_format({'font_name': 'Mars Centra'})
fmt_integer_2      = workbook.add_format({'num_format': '0', 'font_name': 'Mars Centra'})
fmt_decimal_2      = workbook.add_format({'num_format': '0.00', 'font_name': 'Mars Centra'})
fmt_decimal_8      = workbook.add_format({'num_format': '0.00000000', 'font_name': 'Mars Centra'})

# FORMATO DA DIVISÓRIA VERTICAL MESTRE (Aplica uma linha à direita até o final)
fmt_divisao_coluna = workbook.add_format({'font_name': 'Mars Centra', 'right': 1})


# ==============================================================================
# 4. MAPEAMENTO DE ÍNDICE DE TRANSIÇÃO (N13P para Produtos)
# ==============================================================================
# Unimos as colunas básicas brancas e as dinâmicas de períodos (que formam o grupo N13P)
colunas_n13p_totais = col_branco + colunas_periodos
indices_n13p = [df_n13p_ordenado.columns.get_loc(col) for col in colunas_n13p_totais if col in df_n13p_ordenado.columns]
idx_divisao = max(indices_n13p) if indices_n13p else -1


# ==============================================================================
# 5. APLICAÇÃO DOS FORMATOS, BORDAS E LARGURAS INTELIGENTES
# ==============================================================================
print("\n🎨 Aplicando estilos de bordas, cores e fontes corporativas...")
for col_num, col_nome in enumerate(df_n13p_ordenado.columns):
    
    # 1. Definição do formato visual do cabeçalho (Box do N13P vs Outras colunas)
    if col_num in indices_n13p:
        if col_num == 0:
            formato_cabecalho = fmt_header_n13p_inicio
        elif col_num == idx_divisao:
            formato_cabecalho = fmt_header_n13p_fim
        else:
            formato_cabecalho = fmt_header_n13p_meio
    else:
        # Outras Colunas (Sem bordas laterais nos cabeçalhos)
        if col_nome in col_roxo:
            formato_cabecalho = fmt_roxo
        elif col_nome == col_vermelho:
            formato_cabecalho = fmt_vermelho
        elif col_nome in col_azul:
            formato_cabecalho = fmt_azul
        elif col_nome in col_agua:
            formato_cabecalho = fmt_agua
        elif col_nome in col_cinza:
            formato_cabecalho = fmt_cinza
        elif col_nome in col_c_escuro:
            formato_cabecalho = fmt_c_escuro
        elif col_nome.startswith('GSV R$'):
            formato_cabecalho = fmt_verde
        else:
            formato_cabecalho = fmt_branco
        
    # Escreve o cabeçalho estilizado
    worksheet.write(0, col_num, col_nome, formato_cabecalho)
    
    # 2. Auto-ajuste de largura baseado na amostra de dados
    max_comprimento_dados = df_n13p_ordenado[col_nome].head(30000).astype(str).str.len().max()
    largura = max(len(col_nome), max_comprimento_dados) + 3
    largura = min(largura, 50)
    
    # 3. Aplicação do formato de dados das células do corpo
    # Se for a coluna divisória mestre, aplica a borda direita até o final
    if col_num == idx_divisao:
        worksheet.set_column(col_num, col_num, largura, fmt_divisao_coluna)
    # Formatação numérica padrão para as demais colunas
    elif col_nome in col_2d and df_n13p_ordenado[col_nome].dtype in [np.float64, np.float32]:
        worksheet.set_column(col_num, col_num, largura, fmt_decimal_2)
    elif col_nome in col_8d and df_n13p_ordenado[col_nome].dtype in [np.float64, np.float32]:
        worksheet.set_column(col_num, col_num, largura, fmt_decimal_8)
    elif col_nome in col_int and df_n13p_ordenado[col_nome].dtype in [np.int64, np.int32]:
        worksheet.set_column(col_num, col_num, largura, fmt_integer_2)
    else:
        worksheet.set_column(col_num, col_num, largura, fmt_texto_padrao)

# Fecha e salva a planilha finalizada
writer.close()

fim_export = time.time()
tempo_exportacao = fim_export - inicio_export

print("\n===== 🏆 ARQUIVO ESTILIZADO SALVO COM SUCESSO! =====")
print(f"⏱️ Tempo total de processamento: {tempo_exportacao:.2f} segundos")
print(f"💾 Arquivo salvo como: {Path(nome_arquivo_formatado).resolve()}")
