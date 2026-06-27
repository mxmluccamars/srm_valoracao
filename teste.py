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








result = [
    'col1' =  keys: 'uf', 'ano';
    'col2' = keys: 'ncm', 'uf'
]

