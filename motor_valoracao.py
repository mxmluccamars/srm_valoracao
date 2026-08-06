# motor_valoracao.py

import pandas as pd
import numpy as np

def carregar_e_validar_dados(arquivos_carregados, ciclo):

    periodo = ciclo['periodo']
    ano = ciclo['ano']

    # Leitura N13P
    try:
        colunas_n13p = {
                    'Tipo 1': str,
                    'Tipo 2': str,
                    'Tipo 3': str,
                    'Regional': str,
                    'GP': str,
                    'Vend.': str,
                    'Gerente': str,
                    'Rede': str,
                    'COD_CLIENTE': str,
                    'Company Code': str,
                    'CD': str,
                    'NOME_CLIENTE': str,
                    'UF': str,
                    'Região': str,
                    'EAN': str,
                    'SKU': str,
                    'Desc. SKU': str,
                    'Classificação': str,
                    'Tech': str,
                    'Tech 2': str,
                    'Subbrand': str,
                    'Size': str,
                    'Nivel 3 HieraR': str,
                    'Marca': str
        }
        
        # colunas dinamicas de projeção
        colunas_periodos = [f'P{i:02d}-{ano}' for i in range(periodo, 14)]

        for col_periodo in colunas_periodos:
            colunas_n13p[col_periodo] = float    

        # carregar 
        df_n13p = pd.read_excel(arquivos_carregados['N13P'], engine='calamine', header=3, usecols=colunas_n13p.keys(), dtype=colunas_n13p)

        # renomear
        df_n13p.rename(columns={'UF': 'UF DESTINO'}, inplace=True)


    except FileNotFoundError:
        raise Exception("Arquivo N13P não encontrado.")
    except ValueError:
        raise Exception("Estrutura do arquivo N13P inválida Verifique o cabeçalho e as colunas.")
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo N13P: {str(e)}")


    # Produtos
    try:
        colunas_produtos = {
            'EAN': str,
            'Descrição': str,
            'SKU': str,
            'Family Price': str,
            'Categoria': str,
            'Brand': str,
            'Sub Brand': str,
            'Ton/CDA': float,
            'Unid/\nCX': float, # originalmente é 'Unid/\nCX	': float
            'Origem': str,
            'Hierarquia': str,
            'NCM': str,
            'Tipo': str,
            'Promoção': str,
            'Class.': str,
            'kg/Un': float,
            'H05': str,
            'LSV': float,
        }

        df_produtos = pd.read_excel(arquivos_carregados['BASE PRODUTOS'], engine='calamine', header=0, usecols=colunas_produtos.keys(), dtype=colunas_produtos)
        df_produtos.rename(columns={'Unid/\nCX': 'Unid/CX'}, inplace=True)

    except FileNotFoundError:
        raise Exception("Arquivo BASE PRODUTOS não encontrado.")
    except ValueError:
        raise Exception("Estrutura do arquivo BASE PRODUTOS inválida Verifique o cabeçalho e as colunas.")
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo BASE PRODUTOS: {str(e)}")


    # Clientes
    try:
        colunas_clientes = {
            'COD_CLIENTE': str,
            'NOME_CLIENTE': str,
            'UF': str,
            'Rede': str,
            'COD REDE': str,
            'COD SUBREDE': str,
            'COND. PAG': str,
            'GP': str,
            'COD GP': str
        }

        df_clientes = pd.read_excel(arquivos_carregados['BASE CLIENTES'], engine='calamine', header=0, usecols=colunas_clientes.keys(), dtype=colunas_clientes)

    except FileNotFoundError:
        raise Exception("Arquivo BASE CLIENTES não encontrado.")
    except ValueError:
        raise Exception("Estrutura do arquivo BASE CLIENTES inválida Verifique o cabeçalho e as colunas.")
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo BASE CLIENTES: {str(e)}")

    # coluna de UF Origem
    try:
        dicionario_uf = {
            'BR01': 'SP',
            'BR03': 'PE',
            'BR30': 'SP',
            'BR31': 'MG',
        }
        df_n13p['UF ORIGEM'] = df_n13p['CD'].map(dicionario_uf)
    except Exception as e:
        raise Exception(f"Erro ao gerar coluna UF ORIGEM: {str(e)}")

    # Ean Espelho
    try:
        search_ean = df_produtos.set_index('EAN', drop=False)['EAN'].to_dict()
        df_n13p['EAN Espelho'] = df_n13p['EAN'].map(search_ean)

        search_desc = df_produtos.set_index('Descrição', drop=False)['EAN'].to_dict()
        secondary_search = df_n13p['Desc. SKU'].map(search_desc)
        df_n13p['EAN Espelho'] = df_n13p['EAN Espelho'].fillna(secondary_search)
    except Exception as e:
        raise Exception(f"Erro ao gerar coluna EAN Espelho: {str(e)}")

    # merge de produtos na base
    try:
        # colunas selecionadas
        colunas_produtos_selecionadas = [
            'EAN', 'SKU', 'Family Price', 'Hierarquia', 'Class.', 'NCM', 
            'Origem', 'kg/Un', 'Ton/CDA', 'Unid/CX', 'LSV'
        ]

        # base para cruzamento exato (EAN + SKU)
        df_prod_exato = df_produtos[colunas_produtos_selecionadas].drop_duplicates(subset=['EAN', 'SKU'], keep='first')

        # base de resgate (apenas por EAN, removendo a coluna SKU)
        df_prod_resgate = df_produtos[colunas_produtos_selecionadas].drop(columns=['SKU']).drop_duplicates(subset=['EAN'], keep='first')

        # prieiro merge: cruzamento exato
        df_n13p = pd.merge(
            df_n13p,
            df_prod_exato,
            left_on=['EAN Espelho', 'SKU'],
            right_on=['EAN', 'SKU'],
            how='left'
        )

        # Ajuste pos merge
        df_n13p = df_n13p.drop(columns=['EAN_y'], errors='ignore')
        df_n13p = df_n13p.rename(columns={'EAN_x': 'EAN'})

        # segundo merge: resgate pelo EAN espelho
        df_n13p = pd.merge(
            df_n13p,
            df_prod_resgate,
            left_on='EAN Espelho',
            right_on='EAN',
            how='left',
            suffixes=('', '_resgate')
        )

        # preenchendo dados faltantes
        colunas_preencher = ['Family Price', 'Hierarquia', 'Class.', 'NCM', 'Origem', 'kg/Un', 'Ton/CDA', 'Unid/CX', 'LSV']
        for col in colunas_preencher:
            df_n13p[col] = df_n13p[col].fillna(df_n13p[f'{col}_resgate'])

        # limpeza dasd colunas temporárias de resgate
        colunas_lixo = [f'{col}_resgate' for col in colunas_preencher] + ['EAN_resgate']
        df_n13p = df_n13p.drop(columns=colunas_lixo, errors='ignore')

    except Exception as e:
        raise Exception(f"Erro ao juntar dados dos produtos: {str(e)}")

    # merge de clientes na base
    try:
        # colunas selecionadas
        df_clientes_limpo = df_clientes[['COD_CLIENTE', 'COD REDE', 'COD SUBREDE', 'COND. PAG', 'COD GP']].drop_duplicates(subset=['COD_CLIENTE'], keep='first')

        # merge
        df_n13p = pd.merge(
            df_n13p,
            df_clientes_limpo, 
            on='COD_CLIENTE',
            how='left'
        )

    except Exception as e:
        raise Exception(f"Erro ao juntar dados dos clientes: {str(e)}")

    # zp55
    try:
        colunas_zp55 = {
            'CHAVE': str,
            'Cadastro SAP': str,
            'Org. Vendas': str,
            'Emissor': str,
            'País': str,
            'Centro': str,
            'UF': str,
            'NCM': str,
            'H01': str,
            'H02': str,
            'H03': str,
            'H04': str,
            'H05': str,
            'H06': str,
            'Cadastro': float,
        }

        df_zp55 = pd.read_excel(arquivos_carregados['ZP55'], 
                                engine='calamine', 
                                header=1, 
                                usecols=colunas_zp55.keys(), 
                                dtype=colunas_zp55)

    except FileNotFoundError:
        raise Exception("Arquivo ZP55 não encontrado.")
    except ValueError:
        raise Exception("Estrutura do arquivo ZP55 inválida Verifique o cabeçalho e as colunas.")
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo ZP55: {str(e)}")

    # zp54
    try:
        colunas_zp54 = {
            'CHAVE': str,
            'Cadastro SAP': str,
            'Org. Vendas': str,
            'Emissor': str,
            'Rede': str,
            'GP': str,
            'UF': str,
            'H01': str,
            'H02': str,
            'H03': str,
            'H04': str,
            'H05': str,
            'H06': str,
            'Cadastro': float,
        }

        df_zp54 = pd.read_excel(arquivos_carregados['ZP54'], 
                                engine='calamine', 
                                header=1, 
                                usecols=colunas_zp54.keys(), 
                                dtype=colunas_zp54)

    except FileNotFoundError:
        raise Exception("Arquivo ZP54 não encontrado.")
    except ValueError:
        raise Exception("Estrutura do arquivo ZP54 inválida Verifique o cabeçalho e as colunas.")
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo ZP54: {str(e)}")

    # zp53
    try:

        colunas_zp53 = {
            'Chaves': str,
            'Cadastro SAP': str,
            'Org. Vendas': str,
            'Emissor': str,
            'Rede': str,
            'GP': str,
            'UF': str,
            'H01': str,
            'H02': str,
            'H03': str,
            'H04': str,
            'H05': str,
            'H06': str,
            'Cadastro': float,
            'Validade': str,
            'Fim': str,
        }

        df_zp53 = pd.read_excel(
            arquivos_carregados['ZP53'],
            engine='calamine', 
            header=1,
            usecols=colunas_zp53.keys(), 
            dtype=colunas_zp53
        )

    except FileNotFoundError:
        raise Exception("Arquivo ZP53 não encontrado.")
    except ValueError:
        raise Exception("Estrutura do arquivo ZP53 inválida Verifique o cabeçalho e as colunas.")
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo ZP53: {str(e)}")

    # zp52
    try: 
        colunas_zp52 = {
            'Chaves': str,
            'Cadastro SAP': str,
            'Org. Vendas': str,
            'Rede': str,
            'H01': str,
            'Cadastro': float,
            'x': str,
        }

        df_zp52 = pd.read_excel(
            arquivos_carregados['ZP52'],
            engine='calamine', 
            header=1,
            usecols=colunas_zp52.keys(), 
            dtype=colunas_zp52
        )

    except FileNotFoundError:
        raise Exception("Arquivo ZP52 não encontrado.")
    except ValueError:
        raise Exception("Estrutura do arquivo ZP52 inválida Verifique o cabeçalho e as colunas.")
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo ZP52: {str(e)}")

    # zp73
    try: 
        colunas_zp73 = {
            'CHAVE': str,
            'Cadastro SAP': str,
            'Org. Vendas': str,
            'Emissor': str,
            'Rede': str,
            'H01': str,
            'Cadastro': float,
            'x': str,
        }

        df_zp73 = pd.read_excel(
            arquivos_carregados['ZP73'],
            engine='calamine', 
            header=2,
            usecols=colunas_zp73.keys(), 
            dtype=colunas_zp73
        )

    except FileNotFoundError:
        raise Exception("Arquivo ZP73 não encontrado.")
    except ValueError:
        raise Exception("Estrutura do arquivo ZP73 inválida Verifique o cabeçalho e as colunas.")
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo ZP73: {str(e)}")

    # zp70
    try: 
        colunas_zp70 = {
            'CONDICAO DE PAGAMENTO': str,
            'Desconto': float,
        }

        df_zp70 = pd.read_excel(
            arquivos_carregados['ZP70'],
            engine='calamine', 
            header=0,
            usecols=colunas_zp70.keys(), 
            dtype=colunas_zp70
        )

    except FileNotFoundError:
        raise Exception("Arquivo ZP70 não encontrado.")
    except ValueError:
        raise Exception("Estrutura do arquivo ZP70 inválida Verifique o cabeçalho e as colunas.")
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo ZP70: {str(e)}")

    # zp39
    try:
        colunas_zp39 = {
            'CHAVE': str,
            'Cadastro SAP': str,
            'Org. Vendas': str,
            'Emissor': str,
            'H01': str,
            'H02': str,
            'H03': str,
            'H04': str,
            'H05': str,
            'Cadastro': float,
            'Fim': str,
        }

        df_zp39 = pd.read_excel(
            arquivos_carregados['ZP39'],
            engine='calamine',
            header=1,
            usecols=colunas_zp39.keys(), 
            dtype=colunas_zp39
        )

    except FileNotFoundError:
        raise Exception("Arquivo ZP39 não encontrado.")
    except ValueError:
        raise Exception("Estrutura do arquivo ZP39 inválida Verifique o cabeçalho e as colunas.")
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo ZP39: {str(e)}")



    # Carregamento de impostos
    try:
        # aqui levos sem declarar as colunas por ter varias com nomes diferentes
        df_impostos = pd.read_excel(
            arquivos_carregados['BASE IMPOSTOS'],
            engine='calamine', 
            header=1,
            dtype={'COD EMISSOR': str, 'VENCIMENTO.1': str},
        )

        # colunas da tabela de ALC_ZF
        colunas_alc_zc = {
            'CHAVE EMISSOR': str,
            'Regra': float,
        }

        df_alc_zf = pd.read_excel(
            arquivos_carregados['BASE IMPOSTOS'],
            engine='calamine', 
            header=2,
            usecols=colunas_alc_zc.keys(),
            dtype=colunas_alc_zc,
        )

        # organização e renomeação das colunas das tabelas de impostos

        mapa_renomeacao = {
            'Chave.1': 'exc_Chave',
            'Sub Brand': 'exc_Sub_Brand',
            'UF_Origem.1': 'exc_UF_Origem',
            'UF_Destino.1': 'exc_UF_Destino',
            'Aliq_ICMS.1': 'exc_Aliq_ICMS',
            'Aliq_Cofins.1': 'exc_Aliq_Cofins',
            'Aliq_PIS.1': 'exc_Aliq_PIS',
            'MVA.1': 'exc_MVA'
        }

        df_impostos_limpo = df_impostos.rename(columns=mapa_renomeacao)


        # df com os impostos padrão

        colunas_padrao = [
            'Chave', 'UF_Origem', 'UF_Destino', 'Aliq_ICMS',
            'Aliq_Cofins', 'Aliq_PIS', 'Aliq_ICMS_ST', 'MVA'
        ]

        df_impostos_padrao = df_impostos_limpo[colunas_padrao].copy()
        df_impostos_padrao.dropna(subset=['Chave'], inplace=True)

        # df com os impostos de IPI

        colunas_NCM = ['NCM', 'Aliq_IPI']

        df_IPI = df_impostos_limpo[colunas_NCM].copy()
        df_IPI.dropna(subset=['NCM'], inplace=True)

        # df com os impostos de PMPF (imposto MG)

        colunas_PMPF = ['FAMILY PRICE', 'Size * CDA', 'PMPF/kg (R$)','PMPF (R$)']

        df_PMPF = df_impostos_limpo[colunas_PMPF].copy()
        df_PMPF.dropna(subset=['FAMILY PRICE'], inplace=True)

        # df com os impostos exceções
        colunas_excecao = [
            'exc_Chave', 'exc_Sub_Brand', 'exc_UF_Origem', 'exc_UF_Destino',
            'exc_Aliq_ICMS', 'exc_Aliq_Cofins', 'exc_Aliq_PIS', 'exc_MVA'
        ]
        df_impostos_excecao = df_impostos_limpo[colunas_excecao].copy()
        # Remove linhas onde a chave de exceção 'exc_Chave' é vazia
        df_impostos_excecao.dropna(subset=['exc_Chave'], inplace=True)

    except FileNotFoundError:
        raise Exception("Arquivo BASE IMPOSTOS não encontrado.")
    except ValueError:
        raise Exception("Estrutura do arquivo BASE IMPOSTOS inválida Verifique o cabeçalho e as colunas.")
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo BASE IMPOSTOS: {str(e)}")

    return df_n13p, df_produtos, df_clientes, df_zp55, df_zp54, df_zp53, df_zp52, df_zp73, df_zp70, df_zp39, df_impostos_padrao, df_IPI, df_PMPF, df_impostos_excecao
        