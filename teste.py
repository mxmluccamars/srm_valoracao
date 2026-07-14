import os
import time
from typing import List, Callable
import pandas as pd

# Supondo que as suas listas de colunas (cols_base, cols_produtos, etc.) estejam definidas aqui...

class DataProcessor:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    def process(self, file_paths: List[str], ano: int, periodo: int, progress_callback: Callable[[int, str], None]) -> bool:
        try:
            # [Seus passos anteriores de cálculo e leitura aqui...]
            # Digamos que ao chegar na exportação, já tenhamos corrido até 50% do progresso geral.
            
            progress_callback(50, "Cálculos concluídos! Preparando exportação formatada para o Excel...")
            
            # DataFrame final que você gerou
            df_ciclo_n13 = ... 

            # Definindo o nome do arquivo final de saída
            output_file = os.path.join(self.output_dir, f"RESULTADO_VALORACAO_P{periodo}_{ano}.xlsx")
            
            # Iniciando o temporizador igual ao seu código
            inicio_export = time.time()

            # Criamos o writer do pandas/xlsxwriter
            writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
            
            # --- NOVIDADE: EXPORTAÇÃO EM PEDAÇOS (CHUNKS) ---
            total_linhas = len(df_ciclo_n13)
            tamanho_chunk = 5000  # Gravamos de 5 em 5 mil linhas por vez
            
            # O processo de salvar no Excel vai ocupar dos 50% aos 90% da barra de progresso da tela
            progresso_inicial = 50
            progresso_final = 90
            margem_progresso = progresso_final - progresso_inicial

            for i in range(0, total_linhas, tamanho_chunk):
                # Corta o dataframe no pedaço atual
                chunk = df_ciclo_n13.iloc[i : i + tamanho_chunk]
                
                # Se for o primeiro pedaço, grava com cabeçalho. 
                # Se forem os próximos, começamos na linha abaixo (i + 1) e pulamos o cabeçalho (header=False)
                if i == 0:
                    chunk.to_excel(writer, sheet_name='Valoracao', index=False, startrow=0, header=True)
                else:
                    chunk.to_excel(writer, sheet_name='Valoracao', index=False, startrow=i + 1, header=False)
                
                # Calcula o progresso dinâmico das linhas salvas
                linhas_processadas = min(i + tamanho_chunk, total_linhas)
                porcentagem_linhas = linhas_processadas / total_linhas
                
                # Transforma isso na escala de 50% a 90% da barra
                progresso_atual = int(progresso_inicial + (porcentagem_linhas * margem_progresso))
                
                # Atualiza a tela do usuário!
                progress_callback(
                    progresso_atual, 
                    f"Salvando linhas no Excel: {linhas_processadas:,} de {total_linhas:,} concluídas..."
                )

            # -----------------------------------------------------------------
            # APLICAÇÃO DOS SEUS ESTILOS (Cabeçalhos e Largura de Coluna)
            # -----------------------------------------------------------------
            progress_callback(92, "Aplicando formatação de cores e auto-ajuste de colunas...")
            
            workbook  = writer.book
            worksheet = writer.sheets['Valoracao']

            # Estilos que você definiu
            estilo_header = {'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter'}
            fmt_padrao   = workbook.add_format({**estilo_header, 'bg_color': '#FFFFFF'}) 
            fmt_roxo     = workbook.add_format({**estilo_header, 'bg_color': "#7E306A", 'font_color': "#FFFFFF"})
            fmt_vermelho = workbook.add_format({**estilo_header, 'bg_color': "#DF3416", 'font_color': "#FFFFFF"})
            fmt_azul     = workbook.add_format({**estilo_header, 'bg_color': "#0753A5", 'font_color': "#FFFFFF"})
            fmt_cinza    = workbook.add_format({**estilo_header, 'bg_color': "#5A5A5A", 'font_color': "#FFFFFF"})
            fmt_agua     = workbook.add_format({**estilo_header, 'bg_color': "#00FFFF", 'font_color': "#000000"})
            fmt_verde    = workbook.add_format({**estilo_header, 'bg_color': "#06E92C", 'font_color': "#000000"})

            # Seu loop original de aplicação de cores nas colunas
            for col_num, col_nome in enumerate(df_ciclo_n13.columns):
                if col_nome in cols_base:
                    formato = fmt_padrao
                elif col_nome in cols_produtos:
                    formato = fmt_roxo
                elif col_nome == col_ean:
                    formato = fmt_vermelho
                elif col_nome in cols_zps:
                    formato = fmt_azul
                elif col_nome in cols_financeiras:
                    formato = fmt_agua
                elif col_nome in cols_chaves:
                    formato = fmt_cinza
                elif col_nome in cols_financeiras or col_nome.startswith(('GSV R$', 'TON P')):
                    formato = fmt_verde
                else:
                    formato = fmt_padrao

                # Aplica o estilo na linha 0 (cabeçalho)
                worksheet.write(0, col_num, col_nome, formato)
                
                # Auto-ajuste de largura
                largura = max(len(col_nome), 10) + 2
                worksheet.set_column(col_num, col_num, largura)

            # -----------------------------------------------------------------
            # FINALIZAÇÃO DO ARQUIVO (O fechamento física do arquivo no disco)
            # -----------------------------------------------------------------
            progress_callback(95, "Finalizando gravação do arquivo físico no disco...")
            writer.close()

            fim_export = time.time()
            tempo_exportacao = fim_export - inicio_export
            
            progress_callback(100, f"Sucesso! Exportação concluída em {tempo_exportacao:.1f}s.")
            return True

        except Exception as e:
            progress_callback(100, f"Erro inesperado no processamento: {str(e)}")
            return False



# Dicionário de busca rápida
dic_zp = df_zp55.drop_duplicates(subset=['CHAVE'], keep='first').set_index('CHAVE')['Cadastro'].to_dict()

# 2. LOOP MÁGICO: Cria as colunas de resultados de forma totalmente automatizada!
colunas_calculadas = []

for rule in BASE_ZP55_SCHEMA.mapping_rules:
    # Cria uma lista temporária para guardar as séries de strings tratadas
    key_series_list = []
    
    for col in rule.key_components:
        # Garante que a coluna no DataFrame principal é lida como String limpa
        serie = df_ciclo_n13[col].astype(str).str.strip()
        
        # Se houver limite de fatiamento para esta coluna (ex: [:10]), aplica o slice
        if rule.slice_limits and col in rule.slice_limits:
            limit = rule.slice_limits[col]
            serie = serie.str[:limit]
            
        key_series_list.append(serie)
    
    # Concatena todas as colunas da chave usando '_' como separador
    # Ex: 'Company Code' + '_' + 'COD_CLIENTE' + '_' + 'Hierarquia'
    chave_composta = key_series_list[0]
    for serie_adicional in key_series_list[1:]:
        chave_composta = chave_composta + '_' + serie_adicional
        
    # Mapeia contra o dicionário da ZP e divide por 100
    df_ciclo_n13[rule.target_column] = (chave_composta.map(dic_zp) / 100)
    colunas_calculadas.append(rule.target_column)

# 3. RESOLUÇÃO HIERÁRQUICA AUTOMÁTICA (Usando as colunas calculadas no loop)
# Iniciamos a nossa coluna final da ZP vazia
df_ciclo_n13['ZP55'] = df_ciclo_n13[colunas_calculadas[0]]

# Fazemos o fillna em cascata de forma dinâmica para todas as outras colunas geradas pelo loop!
for col in colunas_calculadas[1:]:
    df_ciclo_n13['ZP55'] = df_ciclo_n13['ZP55'].fillna(df_ciclo_n13[col])

df_ciclo_n13['ZP55'] = df_ciclo_n13['ZP55'].round(4)

# Como o 'CLIENTE_FALLBACK' foi uma coluna intermediária de teste, podemos deletá-la se quiser:
df_ciclo_n13.drop(columns=['CLIENTE_FALLBACK'], inplace=True, errors='ignore')

tempo_zp55 = time.time() - inicio_zp55
print(f"✅ ZP55 processed dynamically in {tempo_zp55:.2f}s!")




result = [
    'col1' =  keys: 'uf', 'ano';
    'col2' = keys: 'ncm', 'uf'
]

inicio_zp54 = time.time()

# 1. Importação da ZP54 usando o Schema
df_zp54 = pd.read_excel(
    '../data/ZP54.xlsx', 
    header=BASE_ZP54_SCHEMA.header_row,
    usecols=BASE_ZP54_SCHEMA.required_columns,
    dtype=BASE_ZP54_SCHEMA.dtypes,
    engine=BASE_ZP54_SCHEMA.engine
)

df_zp54['Cadastro'] = pd.to_numeric(df_zp54['Cadastro'], errors='coerce').fillna(0.0)
df_zp54['Cadastro'] = df_zp54['Cadastro'].round(4)
df_zp54['CHAVE'] = df_zp54['CHAVE'].astype(str).str.strip()

# Dicionário de busca rápida
dic_zp54 = df_zp54.drop_duplicates(subset=['CHAVE'], keep='first').set_index('CHAVE')['Cadastro'].to_dict()

colunas_calculadas = []

# 2. Loop Dinâmico com suporte a caracteres de espaçamento
for rule in BASE_ZP54_SCHEMA.mapping_rules:
    key_series_list = []
    
    for col in rule.key_components:
        # --- NOVIDADE: VERIFICAÇÃO INTELIGENTE DE COLUNA VS CONSTANTE ---
        if col in df_ciclo_n13.columns:
            # Se for uma coluna real, puxa os dados e trata
            serie = df_ciclo_n13[col].astype(str).str.strip()
            
            # Aplica fatiamento de caracteres se definido (ex: [:10])
            if rule.slice_limits and col in rule.slice_limits:
                limit = rule.slice_limits[col]
                serie = serie.str[:limit]
        else:
            # Se não for uma coluna (como ' ' ou '_'), cria uma série com o caractere repetido para cada linha
            # Isso impede o KeyError de acontecer!
            serie = pd.Series([col] * len(df_ciclo_n13), index=df_ciclo_n13.index)
            
        key_series_list.append(serie)
    
    # Concatena os componentes da chave usando '_' como separador
    chave_composta = key_series_list[0]
    for serie_adicional in key_series_list[1:]:
        chave_composta = chave_composta + '_' + serie_adicional
        
    # Mapeia contra o dicionário da ZP e divide por 100
    df_ciclo_n13[rule.target_column] = (chave_composta.map(dic_zp54).fillna(0.0) / 100)
    colunas_calculadas.append(rule.target_column)

# 3. Resolução hierárquica automática
df_ciclo_n13['ZP54'] = df_ciclo_n13[colunas_calculadas[0]]

for col in colunas_calculadas[1:]:
    df_ciclo_n13['ZP54'] = df_ciclo_n13['ZP54'].fillna(df_ciclo_n13[col])

df_ciclo_n13['ZP54'] = df_ciclo_n13['ZP54'].round(4)

tempo_zp54 = time.time() - inicio_zp54
print(f"✅ ZP54 processed dynamically with separator-safety in {tempo_zp54:.2f}s!")






    # -------------------------------------------------------------------------
    # CONCATENAÇÃO INTELIGENTE DE CHAVES (Evita sublinhados duplos ao redor de espaços)
    # -------------------------------------------------------------------------
    chave_composta = key_series_list[0]
    
    for i in range(1, len(key_series_list)):
        componente_atual = rule.key_components[i]
        componente_anterior = rule.key_components[i - 1]
        
        # Regra: Se o componente atual ou o anterior for apenas um espaço em branco " ",
        # nós juntamos eles DIRETAMENTE (sem adicionar o sublinhado "_")
        if componente_atual == " " or componente_anterior == " ":
            chave_composta = chave_composta + key_series_list[i]
        else:
            # Caso contrário, junta usando o sublinhado padrão
            chave_composta = chave_composta + '_' + key_series_list[i]
