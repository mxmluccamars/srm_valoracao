import os
import time
from typing import List, Callable
import pandas as pd
import numpy as np

class DataProcessor:
    """
    Classe responsável por aplicar as regras de negócio de valoração sobre as planilhas.
    
    Esta classe deve ser estendida com as fórmulas e cruzamentos de dados
    herdados do Jupyter Notebook de protótipo.
    """

    def __init__(self, output_dir: str):
        """
        Inicializa o processador de dados.

        Args:
            output_dir (str): Diretório onde o arquivo de resultado final será salvo.
        """
        self.output_dir = output_dir

    def process(self, file_paths: List[str], ano: int, periodo: int, progress_callback: Callable[[int, str], None]) -> bool:
        """
        Executa o processamento dos arquivos de valoração.

        Esta versão é simplificada para permitir o desenvolvimento da interface.
        Ela simula as etapas de processamento e atualiza a barra de progresso.

        Args:
            file_paths (List[str]): Lista de caminhos completos dos arquivos validados.
            ano (int): Ano de referência.
            periodo (int): Período de referência.
            progress_callback (Callable[[int, str], None]): Função de retorno (callback) para 
                atualizar a barra de progresso e enviar mensagens de log para a interface. 
                Recebe (porcentagem_inteira, mensagem_de_log).

        Returns:
            bool: True se o processamento foi concluído com sucesso, False caso contrário.
        """
        try:

            progress_callback(0, "Iniciando processamento...")

            # Importação do Ciclo, Clientes e Produtos

            inicio_total = time.time()

            # Ciclo

            inicio_ciclo = time.time()

            colunas_base = ['Regional', 'GP', 'Gerente', 'Rede', 'COD_CLIENTE', 'Company Code','CD',
            'NOME_CLIENTE', 'UF', 'Região', 'EAN', 'SKU', 'Desc. SKU', 'Classificação', 'Subbrand','Marca']

            colunas_periodos = [f'P{i:02d}-{ano}' for i in range(periodo, 14)]

            colunas = colunas_base + colunas_periodos

            tipos_colunas ={'EAN': str, 
                            'COD_CLIENTE': str,
                            'Company Code': str, 
                            'CD': str, 
                            'SKU': str}

            df_ciclo_n13 = pd.read_excel(f'Ciclo_P{periodo:02d} N13P {ano} - envio.xlsx', header=3, usecols=colunas,
                                        dtype=tipos_colunas,
                                        engine='calamine')

            progress_callback(6, "Lendo Ciclo N13P.")

            # Clientes

            tipos_colunas_clientes = {'COD_CLIENTE': str, 'NOME_CLIENTE': str, 'COD REDE': str, 'COD SUBREDE': str, 'COND. PAG': str}

            df_clientes = pd.read_excel('BASE CLIENTES.xlsx', 
                                        dtype=tipos_colunas_clientes,
                                        engine='calamine')

            progress_callback(12, "Lendo Base de Clientes.")

            # Produtos

            tipos_colunas ={'EAN': str, 
                            'SKU': str,
                            'Ton/CDA': float, 
                            'Unid/\nCX	': float, 
                            'Hierarquia': str,
                            'NCM': str,
                            'kg/Un': float,
                            'H05': str,
                            'LSV': float}

            df_produtos = pd.read_excel('BASE PRODUTOS.xlsx', 
                                        dtype=tipos_colunas,
                                        engine='calamine')

            df_produtos = df_produtos.rename(columns={'Unid/\nCX': 'Unid/CDA', 'kg/Un': 'kg/UN'})

            progress_callback(18, "Lendo Base de Produtos.")

            #-#-#-# Colunas especificas #-#-#-#

            #  UF Origem

            dicionario_uf = {
                'BR01': 'SP',
                'BR03': 'PE',
                'BR30': 'SP',
                'BR31': 'MG',
            }

            df_ciclo_n13['UF ORIGEM'] = df_ciclo_n13['CD'].map(dicionario_uf)

            df_ciclo_n13[['CD', 'UF ORIGEM']].head(10)

            # COD GP

            dicionario_gp = {
                'ATACADO CASH & CARRY': 'AG',
                'GPA': 'AH',
                "SAM'S CLUB": 'AM',
                'GROCERY': 'AL',
                'ASSAI': 'AX',
                'Atacadão': 'TA',
                'DIST. MISTO': 'BI',
                'ESPECIALISTA DIRETO': 'AD',
                'DIA %': 'AF',
                'DIST. ALIMENTAR': 'AI',
                'DIST. ESPECIALISTA': 'AJ',
                'CENCOSUD': 'BJ',
                'CARREFOUR': 'AE',
                'ECOMMERCE': 'BO',
                'KA ESPECIALISTA': 'AQ',
                'PETZ': 'BL',
                'ATACADOS': 'AB',
                'MARTINS': 'BK',
                'COBASI': 'BM',
                'ATACADOS ESPECIAIS': 'BT',
                'CONVENIENCIAS': 'BP'
            }

            df_ciclo_n13['CÓD GP'] = df_ciclo_n13['GP'].map(dicionario_gp)

            df_ciclo_n13['GP'] = df_ciclo_n13['GP'].str.strip()

            # EAN Espelho

            search_ean = df_produtos.set_index('EAN', drop=False)['EAN'].to_dict()
            df_ciclo_n13['EAN Espelho'] = df_ciclo_n13['EAN'].map(search_ean)

            search_desc = df_produtos.set_index('Descrição', drop=False)['EAN'].to_dict()
            secondary_search = df_ciclo_n13['Desc. SKU'].map(search_desc)
            df_ciclo_n13['EAN Espelho'] = df_ciclo_n13['EAN Espelho'].fillna(secondary_search)

            # SKU

            colunas_produtos = ['EAN', 'SKU', 'Family Price', 'Hierarquia', 'Class.', 'NCM', 
                                'Origem', 'kg/UN', 'Ton/CDA', 'Unid/CDA', 'LSV']

            df_prod_exato = df_produtos[colunas_produtos].drop_duplicates(subset=['EAN', 'SKU'], keep='first')
            df_prod_resgate = df_produtos[colunas_produtos].drop(columns=['SKU']).drop_duplicates(subset=['EAN'], keep='first')

            df_ciclo_n13 = pd.merge(df_ciclo_n13,
                                    df_prod_exato,
                                    left_on=['EAN Espelho', 'SKU'],
                                    right_on=['EAN', 'SKU'],
                                    how='left')

            df_ciclo_n13 = df_ciclo_n13.drop(columns=['EAN_y'], errors='ignore')
            df_ciclo_n13 = df_ciclo_n13.rename(columns={'EAN_x': 'EAN'})

            df_ciclo_n13 = pd.merge(df_ciclo_n13,
                                    df_prod_resgate,
                                    left_on='EAN Espelho',
                                    right_on='EAN',
                                    how='left',
                                    suffixes=('', '_resgate'))

            colunas_preencher = ['Family Price', 'Hierarquia', 'Class.', 'NCM', 'Origem', 'kg/UN', 'Ton/CDA', 'Unid/CDA', 'LSV']

            for col in colunas_preencher:
                df_ciclo_n13[col] = df_ciclo_n13[col].fillna(df_ciclo_n13[f'{col}_resgate'])

            colunas_lixo = [f'{col}_resgate' for col in colunas_preencher] + ['EAN_resgate']
            df_ciclo_n13 = df_ciclo_n13.drop(columns=colunas_lixo, errors='ignore')

            # Codigo Subrede

            df_clientes_limpo = df_clientes[['COD_CLIENTE', 'COD REDE','COD SUBREDE', 'COND. PAG']].drop_duplicates(subset=['COD_CLIENTE'], keep='first')

            df_ciclo_n13 = pd.merge(
                df_ciclo_n13,
                df_clientes_limpo, 
                on='COD_CLIENTE',
                how='left'
            )

            fim_ciclo = time.time()
            tempo_ciclo = fim_ciclo - inicio_ciclo


            # ZP55 e ZP54
            progress_callback(21, "Calculando ZP55.")
            
            inicio_zp55 = time.time()

            # Importação

            tipos_colunas = {'CHAVE' : str, 'Cadastro': float}

            colunas = ['CHAVE', 'Cadastro']

            df_zp55 = pd.read_excel('ZP55.xlsx', 
                                    header=1,
                                    usecols=colunas,
                                    dtype=tipos_colunas,
                                    engine='calamine')

            df_zp55['Cadastro'] = df_zp55['Cadastro'].round(4)

            # Busca

            df_zp55['CHAVE'] = df_zp55['CHAVE'].astype(str).str.strip()
            dic_zp55 = df_zp55.drop_duplicates(subset=['CHAVE'], keep='first').set_index('CHAVE')['Cadastro'].to_dict()


            chave_1_full = df_ciclo_n13['Company Code'].astype(str).str.strip() + '_' + df_ciclo_n13['COD_CLIENTE'].astype(str).str.strip() + '_' + df_ciclo_n13['Hierarquia'].astype(str).str.strip()
            chave_1_10 = df_ciclo_n13['Company Code'].astype(str).str.strip() + '_' + df_ciclo_n13['COD_CLIENTE'].astype(str).str.strip() + '_' + df_ciclo_n13['Hierarquia'].astype(str).str.strip().str[:10]

            chave_2 = df_ciclo_n13['CD'].astype(str).str.strip() + '_' + df_ciclo_n13['UF'].astype(str).str.strip() + '_' + df_ciclo_n13['Origem'].astype(str).str.strip()
            chave_3 = df_ciclo_n13['CD'].astype(str).str.strip() + '_' + df_ciclo_n13['UF'].astype(str).str.strip() + '_' + df_ciclo_n13['NCM'].astype(str).str.strip()
            chave_4 = df_ciclo_n13['CD'].astype(str).str.strip() + '_' + df_ciclo_n13['UF'].astype(str).str.strip() + '_' + df_ciclo_n13['Hierarquia'].astype(str).str.strip().str[:10]

            df_ciclo_n13['CLIENTE'] = (chave_1_full.map(dic_zp55).fillna(chave_1_10.map(dic_zp55)) / 100)
            df_ciclo_n13['CD + UF DESTINO + Importação'] = (chave_2.map(dic_zp55) / 100)
            df_ciclo_n13['CD + UF DESTINO + NCM'] = (chave_3.map(dic_zp55) / 100)
            df_ciclo_n13['CD + UF DESTINO + H05'] = (chave_4.map(dic_zp55) / 100)

            df_ciclo_n13['ZP55'] = (df_ciclo_n13['CLIENTE']
                                    .fillna(df_ciclo_n13['CD + UF DESTINO + Importação'])
                                    .fillna(df_ciclo_n13['CD + UF DESTINO + NCM'])
                                    .fillna(df_ciclo_n13['CD + UF DESTINO + H05'])
                                    )

            df_ciclo_n13['ZP55'] = df_ciclo_n13['ZP55'].round(4)

            fim_zp55 = time.time()
            tempo_zp55 = fim_zp55 - inicio_zp55

            progress_callback(24, "Calculando ZP54.")
            
            inicio_zp54 = time.time()

            # Importação

            tipos_colunas = {'CHAVE' : str, 'Cadastro': float}

            colunas = ['CHAVE', 'Cadastro']

            df_zp54 = pd.read_excel('ZP54.xlsx', 
                                    header=1,
                                    usecols=colunas,
                                    dtype=tipos_colunas,
                                    engine='calamine')

            df_zp54['Cadastro'] = df_zp54['Cadastro'].round(4)

            # Chaves

            dic_zp54 = df_zp54.set_index('CHAVE')['Cadastro'].to_dict()

            chave_1_12 = df_ciclo_n13['Company Code'].astype(str) + '_' + df_ciclo_n13['COD_CLIENTE'].astype(str) + '_' + df_ciclo_n13['Hierarquia'].astype(str).str[:12]
            chave_2 = df_ciclo_n13['Company Code'].astype(str) + '_' + df_ciclo_n13['COD SUBREDE'].astype(str) + '_' + df_ciclo_n13['Hierarquia'].astype(str).str[:12]
            chave_3 = df_ciclo_n13['Company Code'].astype(str) + '_' + df_ciclo_n13['CÓD GP'].astype(str) + ' ' + df_ciclo_n13['UF'].astype(str) + '_' + df_ciclo_n13['Hierarquia'].astype(str).str[:12]
            chave_4 = df_ciclo_n13['Company Code'].astype(str) + '_' +df_ciclo_n13['CÓD GP'].astype(str) + ' ' + df_ciclo_n13['UF'].astype(str) + '_' + df_ciclo_n13['Hierarquia'].astype(str).str[:10]

            # Busca

            df_ciclo_n13['1. CLIENTE'] = (chave_1_12.map(dic_zp54) / 100).round(4)
            df_ciclo_n13['1. REDE'] = (chave_2.map(dic_zp54) / 100).round(4)
            df_ciclo_n13['1. GP UF HIER 6'] = (chave_3.map(dic_zp54) / 100).round(4)
            df_ciclo_n13['1. GP UF HIER 5'] = (chave_4.map(dic_zp54) / 100).round(4)

            df_ciclo_n13['ZP54'] = (df_ciclo_n13['1. CLIENTE']
                                    .fillna(df_ciclo_n13['1. REDE'])
                                    .fillna(df_ciclo_n13['1. GP UF HIER 6'])
                                    .fillna(df_ciclo_n13['1. GP UF HIER 5'])
                                    )

            df_ciclo_n13['ZP54'] = df_ciclo_n13['ZP54'].round(4)

            fim_zp54 = time.time()
            tempo_zp54 = fim_zp54 - inicio_zp54

            # GSV

            progress_callback(29, "Calculando GSVs.")
            inicio_gsv = time.time()

            # GSV/CDA

            df_ciclo_n13['GSV/CDA'] = df_ciclo_n13['LSV'] * (1 + df_ciclo_n13['ZP55']) * (1 + df_ciclo_n13['ZP54'])

            df_ciclo_n13['GSV/CDA'] = df_ciclo_n13['GSV/CDA'].round(4)

            # GSV/TON

            coluna_BA = df_ciclo_n13['GSV/CDA'] 
            coluna_AA = df_ciclo_n13['kg/UN'] 
            coluna_AO = df_ciclo_n13['Unid/CDA'] 

            denominador = coluna_AA * coluna_AO

            df_ciclo_n13['GSV/TON'] = np.where(
                (denominador == 0) | (denominador.isna()),
                np.nan,                                   
                (coluna_BA / denominador) * 1000           
            )

            df_ciclo_n13['GSV/TON'] = df_ciclo_n13['GSV/TON'].round(4)


            fim_gsv = time.time()
            tempo_gsv = fim_gsv - inicio_gsv

            # Projeções

            progress_callback(35, "Calculando Projeções.")
            
            inicio_projecao = time.time()

            for p in colunas_periodos:
                nome_coluna_projecao = f'GSV R$ {p} - {ano}'

                df_ciclo_n13[nome_coluna_projecao] = df_ciclo_n13[p] * df_ciclo_n13['GSV/TON']

            fim_projecao = time.time()
            tempo_projecao = fim_projecao - inicio_projecao

            # ZP53, ZP52, ZP73, ZP70 e ZP39

            progress_callback(37, "Calculando ZP53.")
            
            inicio_zp53 = time.time()

            # Importação

            tipos_colunas = {'CHAVE' : str, 'Cadastro': float, 'P\'ANO_FIM' : str}

            colunas = ['CHAVE', 'Cadastro', 'P\'ANO_FIM']

            df_zp53 = pd.read_excel('ZP53.xlsx', 
                                    header=1,
                                    usecols=colunas,
                                    dtype=tipos_colunas,
                                    engine='calamine')

            df_zp53['Cadastro'] = df_zp53['Cadastro'].round(2)

            df_zp53['CHAVE'] = df_zp53['CHAVE'].astype(str).str.strip()

            # Chaves

            dic_zp531 = df_zp53.drop_duplicates(subset=['CHAVE'], keep='first').set_index('CHAVE')['Cadastro'].to_dict()
            dic_zp532 = df_zp53.drop_duplicates(subset=['CHAVE'], keep='first').set_index('CHAVE')['P\'ANO_FIM'].to_dict()

            chave_1 = df_ciclo_n13['Company Code'].astype(str).str.strip() + '_' + df_ciclo_n13['COD_CLIENTE'].astype(str).str.strip() + '_' + df_ciclo_n13['Hierarquia'].astype(str).str.strip()
            chave_2 = df_ciclo_n13['Company Code'].astype(str).str.strip() + '_' + df_ciclo_n13['COD SUBREDE'].astype(str).str.strip() + '_' + df_ciclo_n13['Hierarquia'].astype(str).str.strip()
            chave_3 = df_ciclo_n13['Company Code'].astype(str).str.strip() + '_' + df_ciclo_n13['CÓD GP'].astype(str).str.strip() + ' ' + df_ciclo_n13['UF'].astype(str).str.strip() + '_' + df_ciclo_n13['Hierarquia'].astype(str).str.strip()
            chave_4 = df_ciclo_n13['Company Code'].astype(str).str.strip() + '_' + df_ciclo_n13['CÓD GP'].astype(str).str.strip() + '_' + df_ciclo_n13['Hierarquia'].astype(str).str.strip().str[:10] # <-- CORREÇÃO AQUI!

            # Busca
            df_ciclo_n13['1. EMISSOR'] = chave_1.map(dic_zp531) / 100
            df_ciclo_n13['1. REDE'] = chave_2.map(dic_zp531) / 100
            df_ciclo_n13['1. GP UF'] = chave_3.map(dic_zp531) / 100
            df_ciclo_n13['1. GP'] = chave_4.map(dic_zp531) / 100

            df_ciclo_n13['2. EMISSOR'] = chave_1.map(dic_zp532)
            df_ciclo_n13['2. REDE'] = chave_2.map(dic_zp532)
            df_ciclo_n13['2. GP UF'] = chave_3.map(dic_zp532)
            df_ciclo_n13['2. GP'] = chave_4.map(dic_zp532)

            df_ciclo_n13['ZP53'] = (df_ciclo_n13['1. EMISSOR']
                                    .fillna(df_ciclo_n13['1. REDE'])
                                    .fillna(df_ciclo_n13['1. GP UF'])
                                    .fillna(df_ciclo_n13['1. GP'])
                                    .fillna(0) 
                                )

            df_ciclo_n13['ZP53'] = df_ciclo_n13['ZP53'].round(4)

            fim_zp53 = time.time()
            tempo_zp53 = fim_zp53 - inicio_zp53

            progress_callback(39, "Calculando ZP52.")
            
            inicio_zp52 = time.time()

            # Importação

            tipos_colunas = {'CHAVE' : str, 'Cadastro': float}

            colunas = ['CHAVE', 'Cadastro']

            df_zp52 = pd.read_excel('ZP52.xlsx', 
                                    header=1,
                                    usecols=colunas,
                                    dtype=tipos_colunas,
                                    engine='calamine')

            df_zp52['Cadastro'] = df_zp52['Cadastro'].round(2)

            df_zp52['CHAVE'] = df_zp52['CHAVE'].astype(str).str.strip()

            # Chaves

            dic_zp52 = df_zp52.set_index('CHAVE')['Cadastro'].to_dict()

            chave_1 = df_ciclo_n13['Company Code'].astype(str) + '_' + df_ciclo_n13['COD_CLIENTE'].astype(str) + '_' + df_ciclo_n13['Hierarquia'].astype(str).str[:8]
            chave_2 = df_ciclo_n13['Company Code'].astype(str) + '_' + df_ciclo_n13['COD SUBREDE'].astype(str) + '_' + df_ciclo_n13['Hierarquia'].astype(str).str[:2]

            # Busca
            df_ciclo_n13['H04'] = (chave_1.map(dic_zp52) / 100).round(4)
            df_ciclo_n13['H01'] = (chave_2.map(dic_zp52) / 100).round(4)

            df_ciclo_n13['ZP52'] = (df_ciclo_n13['H04']
                                    .fillna(df_ciclo_n13['H01'])
                                    .fillna(0)
                                    )
                                    
            df_ciclo_n13['ZP52'] = df_ciclo_n13['ZP52'].round(4)

            fim_zp52 = time.time()
            tempo_zp52 = fim_zp52 - inicio_zp52

            progress_callback(41, "Calculando ZP73.")
             
            inicio_zp73 = time.time()

            # Importação

            tipos_colunas = {'CHAVE' : str, 'Cadastro': float}

            colunas = ['CHAVE', 'Cadastro']

            df_zp73 = pd.read_excel('ZP73.xlsx', 
                                    header=1,
                                    usecols=colunas,
                                    dtype=tipos_colunas,
                                    engine='calamine')

            df_zp73['Cadastro'] = df_zp73['Cadastro'].round(2)

            df_zp73['CHAVE'] = df_zp73['CHAVE'].astype(str).str.strip()

            # Chaves

            dic_zp73 = df_zp73.set_index('CHAVE')['Cadastro'].to_dict()

            chave_1 = df_ciclo_n13['Company Code'].astype(str) + '_' + df_ciclo_n13['COD_CLIENTE'].astype(str)
            chave_2 = df_ciclo_n13['Company Code'].astype(str) + '_' + df_ciclo_n13['COD SUBREDE'].astype(str)

            df_ciclo_n13['ZP73'] = ((chave_1.map(dic_zp73) / 100).round(4)
                                    .fillna((chave_2.map(dic_zp73) / 100).round(4))
                                    .fillna(0)
                                    )
                                    
            df_ciclo_n13['ZP73'] = df_ciclo_n13['ZP73'].round(4)

            fim_zp73 = time.time()
            tempo_zp73 = fim_zp73 - inicio_zp73

            progress_callback(43, "Calculando ZP70.")
            inicio_zp70 = time.time()

            # Importação

            tipos_colunas = {'CONDICAO DE PAGAMENTO' : str, 'Desconto': float}

            colunas = ['CONDICAO DE PAGAMENTO', 'Desconto']

            df_zp70 = pd.read_excel('ZP70.xlsx', 
                                    header=0,
                                    usecols=colunas,
                                    dtype=tipos_colunas,
                                    engine='calamine')

            df_zp70['Desconto'] = df_zp70['Desconto'].round(4)

            # Busca

            dic_zp70 = df_zp70.set_index('CONDICAO DE PAGAMENTO')['Desconto'].to_dict()

            chave_1 = df_ciclo_n13['COND. PAG'].astype(str)

            df_ciclo_n13['ZP70'] = ((chave_1.map(dic_zp70)).round(4)
                                    .fillna(0)
                                    )
                                    
            df_ciclo_n13['ZP70'] = df_ciclo_n13['ZP70'].round(4)

            fim_zp70 = time.time()
            tempo_zp70 = fim_zp70 - inicio_zp70

            progress_callback(45, "Calculando ZP39.")
            inicio_zp39 = time.time()

            # Importação

            tipos_colunas = {'CHAVE' : str, 'Cadastro': float, 'P\'ANO_FIM': str}

            colunas = ['CHAVE', 'Cadastro', 'P\'ANO_FIM']

            df_zp39 = pd.read_excel('ZP39.xlsx', 
                                    header=1,
                                    usecols=colunas,
                                    dtype=tipos_colunas,
                                    engine='calamine')

            df_zp39['Cadastro'] = df_zp39['Cadastro'].round(4)

            # Busca

            dic_zp391 = df_zp39.set_index('CHAVE')['Cadastro'].to_dict()
            dic_zp392 = df_zp39.set_index('CHAVE')['P\'ANO_FIM'].to_dict()

            chave_1 = df_ciclo_n13['Company Code'].astype(str) + '_' + df_ciclo_n13['COD_CLIENTE'].astype(str) + '_' + df_ciclo_n13['Hierarquia'].astype(str).str[:10]

            df_ciclo_n13['1. ZP39'] = ((chave_1.map(dic_zp391) / 100).round(4)
                                    .fillna(0)
                                    )

            df_ciclo_n13['2. ZP39'] = chave_1.map(dic_zp392)

            df_ciclo_n13['1. ZP39'] = df_ciclo_n13['1. ZP39'].round(4)

            fim_zp39 = time.time()
            tempo_zp39 = fim_zp39 - inicio_zp39


            # NIV

            progress_callback(50, "Calculando NIV.")
            
            inicio_niv = time.time()

            # NIV/CDA

            df_ciclo_n13['NIV/CDA'] = df_ciclo_n13['GSV/CDA'] * (1 + df_ciclo_n13['ZP53']) * (1 + df_ciclo_n13['ZP52']) * (1 + df_ciclo_n13['ZP73']) * (1 + df_ciclo_n13['ZP70']) * (1 + df_ciclo_n13['1. ZP39']) 

            df_ciclo_n13['NIV/CDA'] = df_ciclo_n13['NIV/CDA'].round(4)

            # NIV/TON

            coluna_BA = df_ciclo_n13['NIV/CDA']
            coluna_AA = df_ciclo_n13['kg/UN'] 
            coluna_AO = df_ciclo_n13['Unid/CDA'] 

            denominador = coluna_AA * coluna_AO

            df_ciclo_n13['NIV/TON'] = np.where(
                (denominador == 0) | (denominador.isna()),
                np.nan,                                   
                (coluna_BA / denominador) * 1000           
            )

            df_ciclo_n13['NIV/TON'] = df_ciclo_n13['NIV/TON'].round(4)


            fim_niv = time.time()
            tempo_niv = fim_niv - inicio_niv


            # Exportação

            output_file = os.path.join(self.output_dir, f"RESULTADO_VALORACAO_P{periodo:02d}_{ano}.xlsx")

            inicio_export = time.time()

            # Criamos o writer do pandas/xlsxwriter
            writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
            
            total_linhas = len(df_ciclo_n13)
            print(f"Total de linhas a serem salvas: {total_linhas}")
            tamanho_chunk = 10000  # Gravamos de 5 em 5 mil linhas por vez
            
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
            
            
            
            progress_callback(92, "Aplicando formatação de cores e auto-ajuste de colunas...")


            cols_base = ['Regional',
                        'GP',
                        'Gerente',
                        'Rede',
                        'COD_CLIENTE',
                        'Company Code',
                        'CD',
                        'NOME_CLIENTE',
                        'UF',
                        'Região',
                        'EAN',
                        'SKU',
                        'Desc. SKU',
                        'Classificação',
                        'Marca',
                        'LSV'] 

            cols_produtos = ['UF ORIGEM',
                            'CÓD GP',
                            'Family Price',
                            'Hierarquia',
                            'Class.',
                            'NCM',
                            'Origem',
                            'kg/UN',
                            'Ton/CDA',
                            'Unid/CDA',]

            col_ean = 'EAN Espelho'

            cols_zps = ['ZP55', 'ZP54', 'ZP52', 'ZP52', 'ZP53', 'ZP39', 'ZP70', 'ZP73']
            cols_financeiras = ['GSV/CDA', 'GSV/TON', 'NIV/CDA', 'NIV/TON']
            cols_chaves = ['CLIENTE',
                        'CD + UF DESTINO + Importação',
                        'CD + UF DESTINO + NCM',
                        'CD + UF DESTINO + H05',
                        '1. CLIENTE',
                        '1. REDE',
                        '1. GP UF HIER 6',
                        '1. GP UF HIER 5', 
                        '1. EMISSOR',
                        '1. GP UF',
                        '1. GP',
                        '2. EMISSOR',
                        '2. REDE',
                        '2. GP UF',
                        '2. GP',
                        'H04',
                        'H01',]
            
            workbook  = writer.book
            worksheet = writer.sheets['Valoracao']

            # Estilos
            estilo_header = {'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter'}

            fmt_padrao   = workbook.add_format({**estilo_header, 'bg_color': '#FFFFFF'}) 
            fmt_roxo     = workbook.add_format({**estilo_header, 'bg_color': "#7E306A", 'font_color': "#FFFFFF"})
            fmt_vermelho = workbook.add_format({**estilo_header, 'bg_color': "#DF3416", 'font_color': "#FFFFFF"})
            fmt_azul     = workbook.add_format({**estilo_header, 'bg_color': "#0753A5", 'font_color': "#FFFFFF"})
            fmt_cinza    = workbook.add_format({**estilo_header, 'bg_color': "#5A5A5A", 'font_color': "#FFFFFF"})
            fmt_agua     = workbook.add_format({**estilo_header, 'bg_color': "#00FFFF", 'font_color': "#000000"})
            fmt_verde     = workbook.add_format({**estilo_header, 'bg_color': "#06E92C", 'font_color': "#000000"})


            for col_num, col_nome in enumerate(df_ciclo_n13.columns):
    
                # Escolhe o formato baseado na lista
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

                # Aplica a cor no cabeçalho (linha 0)
                worksheet.write(0, col_num, col_nome, formato)
                
                # Auto-ajuste de largura simples
                largura = max(len(col_nome), 10) + 2
                worksheet.set_column(col_num, col_num, largura)

            # Finaliza
            writer.close()

            fim_export = time.time()
            tempo_exportacao = fim_export - inicio_export
            progress_callback(100, f"Sucesso! Planilha Salva!")
            return True

        except Exception as e:
            progress_callback(100, f"Erro inesperado durante o processamento: {str(e)}")
            return False
