# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.4
#   kernelspec:
#     display_name: .venv (3.14.5.final.0)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # SRM Melhoria de Processo

# %% [markdown]
#

# %% [markdown]
# ## Bibliotecas Usadas

# %%
import pandas as pd
import time
import numpy as np

 # %%
 # Parametros

periodo = 3
ano = 2026

# %% [markdown]
# ## Schema

# %%
"""
Definição dos Esquemas (Schemas) de Dados do SRM Valoração.

Este módulo centraliza todas as configurações de leitura das fontes de dados
(planilhas de entrada). Ele define as regras de cabeçalho, tipagem de colunas
críticas e validações necessárias para garantir a integridade do processamento.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Type, Optional, Tuple

dataclass
class MappingRule:
    """
    Define uma regra de composição de chaves para buscar valores em tabelas ZP.
    
    Attributes:
        target_column (str): Nome da coluna resultante onde o valor mapeado será salvo.
        key_components (List[str]): Lista de colunas do DataFrame principal que formam a chave.
        slice_limits (Optional[Dict[str, int]]): Dicionário para limitar caracteres de colunas (ex: {'Hierarquia': 10})
    """
    target_column: str
    key_components: List[str]
    slice_limits: Optional[Dict[str, int]] = None

    def __init__(self, target_column: str, key_components: List[str], slice_limits: Optional[Dict[str, int]] = None):
        self.target_column = target_column
        self.key_components = key_components
        self.slice_limits = slice_limits


@dataclass
class ExcelSheetSchema:
    """
    Representa a definição estrutural (schema) de leitura de uma planilha de entrada.

    Esta classe encapsula metadados necessários para que o Pandas leia a planilha
    corretamente, garantindo tipagem forte e validação de colunas obrigatórias.

    Attributes:
        display_name (str): Nome amigável da planilha para exibição em caixas de log.
        header_row (int): Linha onde se localiza o cabeçalho no Excel (0-indexed).
        engine (str): Motor de leitura que o Pandas utilizará (padrão: "openpyxl").
        dtypes (Dict[str, Type]): Dicionário mapeando colunas críticas a seus tipos corretos (ex: str).
        required_columns (List[str]): Lista com o nome das colunas que devem obrigatoriamente existir.
    """
    display_name: str
    header_row: int = 0
    engine: str = "openpyxl"
    dtypes: Dict[str, Type] = field(default_factory=dict)
    required_columns: List[str] = field(default_factory=list)
    mapping_rules: List[MappingRule] = field(default_factory=list)

    def get_missing_columns(self, df_columns: List[str]) -> List[str]:
        """
        Analisa as colunas de um DataFrame e retorna as colunas obrigatórias que estão ausentes.

        Args:
            df_columns (List[str]): Lista de colunas reais encontradas no DataFrame carregado.

        Returns:
            List[str]: Lista contendo os nomes das colunas obrigatórias que não foram encontradas.
        """
        return [col for col in self.required_columns if col not in df_columns]


CICLO_N13_SCHEMA = ExcelSheetSchema(
    display_name="Ciclo N13",
    header_row=3, 
    engine="openpyxl",
    dtypes={
        "EAN": str,
        "EAN Espelho": str,
        "COD_CLIENTE": str,
        "Company Code": str,
        "CD": str,
        "SKU": str
    },
    required_columns=[
        "Regional", "GP", "Gerente", "Rede", "COD_CLIENTE", 
        "Company Code", "CD", "NOME_CLIENTE", "UF", "Região", 
        "EAN", "SKU", "Desc. SKU", "Classificação", "Marca"
    ]
)

BASE_CLIENTES_SCHEMA = ExcelSheetSchema(
    display_name="Base de Clientes",
    header_row=0,  
    engine="openpyxl",
    dtypes={
        "COD_CLIENTE": str,
        'COD REDE': str,
        'COD SUBREDE': str,
        'COND. PAG': str,
        'CÓD GP': str,

    },
    required_columns=[
        "COD_CLIENTE", "NOME_CLIENTE", "REGIONAL", "UF"
    ]
)

BASE_PRODUTOS_SCHEMA = ExcelSheetSchema(
    display_name="Base de Produtos",
    header_row=0,  
    engine="openpyxl",
    dtypes={
        'EAN': str, 
        'Descrição': str,
        'SKU': str,
        'Family Price': str,
        'Ton/CDA': float, 
        'Unid/\nCX	': float, 
        'Origem': str,
        'Hierarquia': str,
        'NCM': str,
        'kg/Un': float,
        'Class.': str,
        'H05': str,
        'LSV': float
    },
    required_columns=[
        "EAN", "SKU", "Descrição", "Family Price", "Class.",
        "Ton/CDA", "Unid/\nCX	", "Origem", "Hierarquia", "NCM",
        "kg/Un", "H05", "LSV"
    ]
)


BASE_ZP55_SCHEMA = ExcelSheetSchema(
    display_name="Base de ZP55",
    header_row=1,
    engine="openpyxl",
    dtypes={
        'CHAVE': str,
        'Cadastro': float,
    },
    required_columns=[
        "CHAVE", "Cadastro"
    ],
    mapping_rules=[
        MappingRule(
            target_column = 'CLIENTE',
            key_components = ['Company Code', 'COD_CLIENTE', 'Hierarquia']
        ),
        MappingRule(
            target_column = 'CLIENTE_H10',
            key_components = ['Company Code', 'COD_CLIENTE', 'Hierarquia'],
            slice_limits={"Hierarquia": 10}
        ), 
        MappingRule(
            target_column = 'CD + UF DESTINO + Importação',
            key_components = ['CD', 'UF', 'Origem']
        ), 
        MappingRule(
            target_column = 'CD + UF DESTINO + NCM',
            key_components = ['CD', 'UF', 'NCM']
        ), 
        MappingRule(
            target_column = 'CD + UF DESTINO + H05',
            key_components = ['CD', 'UF', 'Hierarquia'],
            slice_limits={"Hierarquia": 10}
        ), 
    ]
)

BASE_ZP54_SCHEMA = ExcelSheetSchema(
    display_name="Base de ZP54",
    header_row=1,
    engine="openpyxl",
    dtypes={
        'CHAVE': str,
        'Cadastro': float,
    },
    required_columns=[
        "CHAVE", "Cadastro"
    ],
    mapping_rules=[
        MappingRule(
            target_column = '1. CLIENTE',
            key_components = ['Company Code', 'COD_CLIENTE', 'Hierarquia']
        ),
        MappingRule(
            target_column = '1. REDE',
            key_components = ['Company Code', 'COD SUBREDE', 'Hierarquia'],
        ), 
        MappingRule(
            target_column = '1. GP UF HIER 6',
            key_components = ['Company Code', 'CÓD GP', ' ','UF', 'Hierarquia'],
        ), 
        MappingRule(
            target_column = '1. GP UF HIER 5',
            key_components = ['Company Code', 'CÓD GP', ' ','UF', 'Hierarquia'],
            slice_limits={"Hierarquia": 10}
        ), 
    ]
)

BASE_ZP53_SCHEMA = ExcelSheetSchema(
    display_name="Base de ZP53",
    header_row=1,
    engine="openpyxl",
    dtypes={
        'CHAVE': str,
        'Cadastro': str,
        'P\'ANO_FIM': str,
    },
    required_columns=[
        "CHAVE", "Cadastro", "P'ANO_FIM"
    ]
)

BASE_ZP52_SCHEMA = ExcelSheetSchema(
    display_name="Base de ZP52",
    header_row=1,
    engine="openpyxl",
    dtypes={
        'CHAVE': str,
        'Cadastro': str,
    },
    required_columns=[
        "CHAVE", "Cadastro"
    ]
)

BASE_ZP73_SCHEMA = ExcelSheetSchema(
    display_name="Base de ZP73",
    header_row=1,
    engine="openpyxl",
    dtypes={
        'CHAVE': str,
        'Cadastro': str,
    },
    required_columns=[
        "CHAVE", "Cadastro"
    ]
)

BASE_ZP70_SCHEMA = ExcelSheetSchema(
    display_name="Base de ZP70",
    header_row=1,
    engine="openpyxl",
    dtypes={
        'CONDICAO DE PAGAMENTO': str,
        'Desconto' : float,
    },
    required_columns=[
        'CONDICAO DE PAGAMENTO', 'Desconto'
    ]
)

BASE_ZP39_SCHEMA = ExcelSheetSchema(
    display_name="Base de ZP39",
    header_row=1,
    engine="openpyxl",
    dtypes={
        'CHAVE': str,
        'Cadastro': str,
        'P\'ANO_FIM': str,
    },
    required_columns=[
        "CHAVE", "Cadastro", "P'ANO_FIM"
    ]
)


# %% [markdown]
# ## Montagem da Base N13P

# %%
# df_ciclo_n13 = pd.read_excel(f'../data/BASE PRODUTOS.xlsx', header=0,
#                              engine='calamine')

# df_ciclo_n13.columns

            

# %%
colunas_ordem = ['Tipo 1', 'Tipo 2', 'Tipo 3', 'Regional', 'GP', 'Vend.', 'Gerente',
                 'Rede', 'COD_CLIENTE', 'Company Code', 'CD', 'NOME_CLIENTE', 'UF', 
                 'Região', 'EAN', 'SKU', 'Desc. SKU', 'Classificação', 'Tech', 'Tech 2',       
                 'Subbrand', 'Size', 'Nivel 3 HieraR', 'Marca',

                 'kg/Un', 'Prazo de Pagamento', 'COD_REDE', 'COD_SUBREDE', 
                 'UF ORIGEM', 'Cód GP', 'EAN ESPELHO', 'Family Price', 'Hierarquia',
                 'Class.', 'NCM', 'Origem', 'Tons/CDA', 'UN/CDA', 'LSV', 
                 
                 'ZP55', 'CLIENTE', 'CD + UF DESTINO + Importação', 'CD + UF DESTINO  NCM', 'CD + UF DESTINO + H05',
                 'ZP54', '1. CLIENTE', '1. REDE', '1. GP UF HIER 6', '1. GP UH HIER 5',
                 
                 'GSV/CDA', 'GSV/TON',

                 'ZP53', 'EMISSOR', 'REDE', 'GP UF', 'GP',
                 'ZP52', 'H04', 'H01', 
                 'ZP73',
                 'ZP70',
                 'ZP39',

                 'NIV/CDA', 'NIV/TON'
                 ]

# %%
#-#-#-# Inicio da contagem do tempo de execução #-#-#-#
inicio_total = time.time()
inicio_ciclo = time.time()


# Ciclo

colunas_base = ['Tipo 1', 'Tipo 2', 'Tipo 3', 'Regional', 'GP', 'Vend.', 'Gerente',
                 'Rede', 'COD_CLIENTE', 'Company Code', 'CD', 'NOME_CLIENTE', 'UF', 
                 'Região', 'EAN', 'SKU', 'Desc. SKU', 'Classificação', 'Tech', 'Tech 2',       
                 'Subbrand', 'Size', 'Nivel 3 HieraR', 'Marca']

colunas_periodos = [f'P{i:02d}-{ano}' for i in range(periodo, 14)]

colunas_ciclo = colunas_base + colunas_periodos

tipos_colunas ={'EAN': str, 
                'COD_CLIENTE': str,
                'Company Code': str, 
                'CD': str, 
                'SKU': str}

df_ciclo_n13 = pd.read_excel(f'../data/Ciclo_P{periodo:02d} N13P {ano} - envio.xlsx', header=3, usecols=colunas_ciclo,
                             dtype=tipos_colunas,
                             engine='calamine')

# df_ciclo_n13 = df_ciclo_n13.rename(columns={'UF': 'UF DESTINO'})




# Clientes

tipos_colunas_clientes = {'COD_CLIENTE': str, 'NOME_CLIENTE': str, 'COD REDE': str, 'COD SUBREDE': str, 'COND. PAG': str}

df_clientes = pd.read_excel('../data/BASE CLIENTES.xlsx', 
                            dtype=tipos_colunas_clientes,
                            engine='calamine')



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

df_produtos = pd.read_excel('../data/BASE PRODUTOS.xlsx', 
                            dtype=tipos_colunas,
                            engine='calamine')

df_produtos = df_produtos.rename(columns={'Unid/\nCX': 'Unid/CDA', 'kg/Un': 'kg/UN'})

df_produtos['kg/UN'] = df_produtos['kg/UN'].round(4)

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

df_produtos['kg/UN']

# %%
# for col in df_ciclo_n13.columns:
#     print(f"{col}: {df_ciclo_n13[col].dtype}")

# %% [markdown]
# ## Calculos

# %% [markdown]
# ### ZP55

# %%
inicio_zp55 = time.time()

df_zp55 = pd.read_excel('../data/ZP55.xlsx', 
                        header=BASE_ZP55_SCHEMA.header_row,
                        usecols=BASE_ZP55_SCHEMA.required_columns,
                        dtype=BASE_ZP55_SCHEMA.dtypes,
                        engine=BASE_ZP55_SCHEMA.engine)

df_zp55['Cadastro'] = df_zp55['Cadastro'].round(4)
df_zp55['CHAVE'] = df_zp55['CHAVE'].astype(str).str.strip()


dic_zp55 = df_zp55.drop_duplicates(subset=['CHAVE'], keep='first').set_index('CHAVE')['Cadastro'].to_dict()

colunas_calculadas = []

for rule in BASE_ZP55_SCHEMA.mapping_rules:
    key_series_list = []
    
    for col in rule.key_components:
        if col in df_ciclo_n13.columns:

            serie = df_ciclo_n13[col].astype(str).str.strip()
            
            if rule.slice_limits and col in rule.slice_limits:
                limit = rule.slice_limits[col]
                serie = serie.str[:limit]
        else:
            serie = pd.Series([col] * len(df_ciclo_n13), index=df_ciclo_n13.index)
            
            
        key_series_list.append(serie)
    
    chave_composta = key_series_list[0]
    
    for i in range(1, len(key_series_list)):
        componente_atual = rule.key_components[i]
        componente_anterior = rule.key_components[i - 1]
        
        if componente_atual == " " or componente_anterior == " ":
            chave_composta = chave_composta + key_series_list[i]
        else:
            chave_composta = chave_composta + '_' + key_series_list[i]
        
    df_ciclo_n13[rule.target_column] = (chave_composta.map(dic_zp55) / 100)
    colunas_calculadas.append(rule.target_column)

df_ciclo_n13['ZP55'] = df_ciclo_n13[colunas_calculadas[0]]

for col in colunas_calculadas[1:]:
    df_ciclo_n13['ZP55'] = df_ciclo_n13['ZP55'].fillna(df_ciclo_n13[col])

df_ciclo_n13['ZP55'] = df_ciclo_n13['ZP55'].round(4)

tempo_zp55 = time.time() - inicio_zp55


# %% [markdown]
# ### ZP 54

# %%
inicio_zp54 = time.time()

# Importação

df_zp54 = pd.read_excel('../data/ZP54.xlsx', 
                        header=BASE_ZP54_SCHEMA.header_row,
                        usecols=BASE_ZP54_SCHEMA.required_columns,
                        dtype=BASE_ZP54_SCHEMA.dtypes,
                        engine=BASE_ZP54_SCHEMA.engine)

df_zp54['Cadastro'] = df_zp54['Cadastro'].round(4)
df_zp54['CHAVE'] = df_zp54['CHAVE'].astype(str).str.strip()

# Chaves

dic_zp54 = df_zp54.drop_duplicates(subset=['CHAVE'], keep='first').set_index('CHAVE')['Cadastro'].to_dict()

colunas_calculadas = []

for rule in BASE_ZP54_SCHEMA.mapping_rules:
    key_series_list = []
    
    for col in rule.key_components:
        if col in df_ciclo_n13.columns:

            serie = df_ciclo_n13[col].astype(str).str.strip()
            
            if rule.slice_limits and col in rule.slice_limits:
                limit = rule.slice_limits[col]
                serie = serie.str[:limit]
        else:
            serie = pd.Series([col] * len(df_ciclo_n13), index=df_ciclo_n13.index)
            
            
        key_series_list.append(serie)
    
    chave_composta = key_series_list[0]
    
    for i in range(1, len(key_series_list)):
        componente_atual = rule.key_components[i]
        componente_anterior = rule.key_components[i - 1]
        
        if componente_atual == " " or componente_anterior == " ":
            chave_composta = chave_composta + key_series_list[i]
        else:
            chave_composta = chave_composta + '_' + key_series_list[i]
        
    df_ciclo_n13[rule.target_column] = (chave_composta.map(dic_zp54) / 100)
    colunas_calculadas.append(rule.target_column)

df_ciclo_n13['ZP54'] = df_ciclo_n13[colunas_calculadas[0]]

for col in colunas_calculadas[1:]:
    df_ciclo_n13['ZP54'] = df_ciclo_n13['ZP54'].fillna(df_ciclo_n13[col])

df_ciclo_n13['ZP54'] = df_ciclo_n13['ZP54'].round(4)

tempo_zp54 = time.time() - inicio_zp54

# %%
df_ciclo_n13['ZP54']

# %% [markdown]
# ### GSVs

# %%
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

# %% [markdown]
# ### Projeções

# %%
inicio_projecao = time.time()

for p in colunas_periodos:
    nome_coluna_projecao = f'GSV R$ {p} - {ano}'

    df_ciclo_n13[nome_coluna_projecao] = df_ciclo_n13[p] * df_ciclo_n13['GSV/TON']

fim_projecao = time.time()
tempo_projecao = fim_projecao - inicio_projecao

# %% [markdown]
# ### ZP53

# %%
inicio_zp53 = time.time()

# Importação

tipos_colunas = {'CHAVE' : str, 'Cadastro': float, 'P\'ANO_FIM' : str}

colunas = ['CHAVE', 'Cadastro', 'P\'ANO_FIM']

df_zp53 = pd.read_excel('../data/ZP53.xlsx', 
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
chave_4 = df_ciclo_n13['Company Code'].astype(str).str.strip() + '_' + df_ciclo_n13['CÓD GP'].astype(str).str.strip() + '_' + df_ciclo_n13['Hierarquia'].astype(str).str.strip().str[:10] 

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

df_ciclo_n13['ZP53d'] = (df_ciclo_n13['2. EMISSOR']
                        .fillna(df_ciclo_n13['2. REDE'])
                        .fillna(df_ciclo_n13['2. GP UF'])
                        .fillna(df_ciclo_n13['2. GP'])
                    )

df_ciclo_n13['ZP53'] = df_ciclo_n13['ZP53'].round(4)

fim_zp53 = time.time()
tempo_zp53 = fim_zp53 - inicio_zp53

# %% [markdown]
# ### ZP52

# %%
inicio_zp52 = time.time()

# Importação

tipos_colunas = {'CHAVE' : str, 'Cadastro': float}

colunas = ['CHAVE', 'Cadastro']

df_zp52 = pd.read_excel('../data/ZP52.xlsx', 
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

# %% [markdown]
# ### ZP73

# %%
inicio_zp73 = time.time()

# Importação

tipos_colunas = {'CHAVE' : str, 'Cadastro': float}

colunas = ['CHAVE', 'Cadastro']

df_zp73 = pd.read_excel('../data/ZP73.xlsx', 
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

# %% [markdown]
# ### ZP70

# %%
inicio_zp70 = time.time()

# Importação

tipos_colunas = {'CONDICAO DE PAGAMENTO' : str, 'Desconto': float}

colunas = ['CONDICAO DE PAGAMENTO', 'Desconto']

df_zp70 = pd.read_excel('../data/ZP70.xlsx', 
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

# %% [markdown]
# ### ZP39

# %%
inicio_zp39 = time.time()

# Importação

tipos_colunas = {'CHAVE' : str, 'Cadastro': float, 'P\'ANO_FIM': str}

colunas = ['CHAVE', 'Cadastro', 'P\'ANO_FIM']

df_zp39 = pd.read_excel('../data/ZP39.xlsx', 
                        header=1,
                        usecols=colunas,
                        dtype=tipos_colunas,
                        engine='calamine')

df_zp39['Cadastro'] = df_zp39['Cadastro'].round(4)

# Busca

dic_zp391 = df_zp39.set_index('CHAVE')['Cadastro'].to_dict()
dic_zp392 = df_zp39.set_index('CHAVE')['P\'ANO_FIM'].to_dict()

chave_1 = df_ciclo_n13['Company Code'].astype(str) + '_' + df_ciclo_n13['COD_CLIENTE'].astype(str) + '_' + df_ciclo_n13['Hierarquia'].astype(str)
chave_2 = df_ciclo_n13['Company Code'].astype(str) + '_' + df_ciclo_n13['COD_CLIENTE'].astype(str) + '_' + df_ciclo_n13['Hierarquia'].astype(str).str[:10]
chave_3 = df_ciclo_n13['Company Code'].astype(str) + '_' + df_ciclo_n13['COD SUBREDE'].astype(str) + '_' + df_ciclo_n13['Hierarquia'].astype(str)
chave_4 = df_ciclo_n13['Company Code'].astype(str) + '_' + df_ciclo_n13['CÓD GP'].astype(str) + ' ' + df_ciclo_n13['UF'].astype(str) + '_' + df_ciclo_n13['Hierarquia'].astype(str)

df_ciclo_n13['39. Emissor H12'] = chave_1.map(dic_zp391)
df_ciclo_n13['39. Emissor H10'] = chave_2.map(dic_zp391)
df_ciclo_n13['39. Subrede H12'] = chave_3.map(dic_zp391)
df_ciclo_n13['39. GP UF H12'] = chave_4.map(dic_zp391)

df_ciclo_n13['39d. Emissor H12'] = chave_1.map(dic_zp392)
df_ciclo_n13['39d. Emissor H10'] = chave_2.map(dic_zp392)
df_ciclo_n13['39d. Subrede H12'] = chave_3.map(dic_zp392)
df_ciclo_n13['39d. GP UF H12'] = chave_4.map(dic_zp392)

df_ciclo_n13['1. ZP39'] = (df_ciclo_n13['39. Emissor H12']
                           .fillna(df_ciclo_n13['39. Emissor H10'])
                           .fillna(df_ciclo_n13['39. Subrede H12'])
                           .fillna(df_ciclo_n13['39. GP UF H12'])
                        )

df_ciclo_n13['2. ZP39'] = (df_ciclo_n13['39d. Emissor H12']
                           .fillna(df_ciclo_n13['39d. Emissor H10'])
                           .fillna(df_ciclo_n13['39d. Subrede H12'])
                           .fillna(df_ciclo_n13['39d. GP UF H12'])
                        )

df_ciclo_n13['1. ZP39'] = df_ciclo_n13['1. ZP39'].round(4)

fim_zp39 = time.time()
tempo_zp39 = fim_zp39 - inicio_zp39

# %% [markdown]
# ### NIV

# %%
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

# %% [markdown]
# ### Importação dos impostos

# %%
# pis = 0.0165
# cofins = 0.076
# ipi = 0.0

tipos_colunas = {
    'CHAVE_1' : str,
    'CHAVE_2' : str,
    'Aliq_COFINS': float,
    'Aliq_PIS': float,
    # 'CBS': float,
    # 'IBS 27': float,
    'ICMS_O': float,
    # 'MVA': float
                }

colunas = ['CHAVE_1', 'CHAVE_2', 'Aliq_COFINS', 'Aliq_PIS', 'ICMS_O',
            # 'CBS', 'IBS 27',  'MVA'
            ]

df_impostos = pd.read_excel('../data/SPIM - MacGyver v102.xlsm', 
                        header=2,
                        usecols=colunas,
                        dtype=tipos_colunas,
                        engine='calamine',
                        sheet_name='BD_Impostos_Oficial')

df_spim_clientes = pd.read_excel('../data/SPIM - MacGyver v102.xlsm', 
                        header=1,
                        usecols=['EMISSOR', 'MODELO RE'],
                        dtype={ 'EMISSOR': str, 'MODELO RE': str},
                        engine='calamine',
                        sheet_name='BD_Clientes')

df_impostos['Aliq_COFINS'] = df_impostos['Aliq_COFINS'].round(4)
df_impostos['Aliq_PIS'] = df_impostos['Aliq_PIS'].round(4)
# df_impostos['CBS'] = df_impostos['CBS'].round(4)
# df_impostos['IBS 27'] = df_impostos['IBS 27'].round(4)
# df_impostos['ICMS_O'] = df_impostos['ICMS_O'].round(4)
# df_impostos['MVA'] = df_impostos['MVA'].round(4)

df_impostos['CHAVE_1'] = df_impostos['CHAVE_1'].astype(str).str.strip()
df_impostos['CHAVE_2'] = df_impostos['CHAVE_2'].astype(str).str.strip()

# df_impostos.head(50)

# %% [markdown]
# ### PIS/COFINS

# %%
dic_chave_1_impostos_cofins = df_impostos.drop_duplicates(subset=['CHAVE_1'], keep='first').set_index('CHAVE_1')["Aliq_COFINS"].to_dict()
dic_chave_1_impostos_pis = df_impostos.drop_duplicates(subset=['CHAVE_1'], keep='first').set_index('CHAVE_1')["Aliq_PIS"].to_dict()

dic_chave_2_impostos_cofins = df_impostos.drop_duplicates(subset=['CHAVE_2'], keep='first').set_index('CHAVE_2')["Aliq_COFINS"].to_dict()
dic_chave_2_impostos_pis = df_impostos.drop_duplicates(subset=['CHAVE_2'], keep='first').set_index('CHAVE_2')["Aliq_PIS"].to_dict()


chave_1 = df_ciclo_n13['Subbrand'].astype(str).str.strip() + df_ciclo_n13['UF ORIGEM'].astype(str).str.strip() + df_ciclo_n13['UF'].astype(str).str.strip()
chave_2 = df_ciclo_n13['UF ORIGEM'].astype(str).str.strip() + df_ciclo_n13['UF'].astype(str).str.strip()


df_ciclo_n13['PIS'] = (chave_1.map(dic_chave_1_impostos_pis).fillna(chave_2.map(dic_chave_2_impostos_pis)))
df_ciclo_n13['COFINS'] = (chave_1.map(dic_chave_1_impostos_cofins).fillna(chave_2.map(dic_chave_2_impostos_cofins)))



# df_ciclo_n13['Pis', 'Cofins'] = df_ciclo_n13['Pis', 'Cofins'].round(4)

# df_ciclo_n13['Pis', 'Cofins'] = df_ciclo_n13['Pis', 'Cofins'].fillna(0)

df_ciclo_n13[['Subbrand', 'UF ORIGEM', 'UF','PIS', 'COFINS']].head()


# %%
# inicio_pis_cofins = time.time()

# # Importação

# df_ciclo_n13['BASE CALCULO PIS/COFINS'] = df_ciclo_n13['NIV/CDA'] / (1 - pis - cofins)

# df_ciclo_n13['PIS/COFINS ABS'] = df_ciclo_n13['BASE CALCULO PIS/COFINS'] * (pis + cofins)

# print(df_ciclo_n13[['NIV/CDA','BASE CALCULO PIS/COFINS', 'PIS/COFINS ABS']].head())

# fim_pis_cofins = time.time()
# tempo_pis_cofins = fim_pis_cofins - inicio_pis_cofins



# %% [markdown]
# ### ICMS
#

# %%
dic_chave_1_impostos_icms = df_impostos.drop_duplicates(subset=['CHAVE_1'], keep='first').set_index('CHAVE_1')["ICMS_O"].to_dict()
dic_chave_2_impostos_icms = df_impostos.drop_duplicates(subset=['CHAVE_2'], keep='first').set_index('CHAVE_2')["ICMS_O"].to_dict()


chave_1 = df_ciclo_n13['Subbrand'].astype(str).str.strip() + df_ciclo_n13['UF ORIGEM'].astype(str).str.strip() + df_ciclo_n13['UF'].astype(str).str.strip()
chave_2 = df_ciclo_n13['UF ORIGEM'].astype(str).str.strip() + df_ciclo_n13['UF'].astype(str).str.strip()


df_ciclo_n13['ICMS'] = (chave_1.map(dic_chave_1_impostos_icms).fillna(chave_2.map(dic_chave_2_impostos_icms)))

# df_ciclo_n13['BASE CALCULO ICMS'] = (df_ciclo_n13['BASE CALCULO PIS/COFINS'] + df_ciclo_n13['CBS ABS'] + df_ciclo_n13['IBS ABS']) / (1 - df_ciclo_n13['ICMS'])
# df_ciclo_n13['ICMS ABS'] = df_ciclo_n13['BASE CALCULO ICMS'] * df_ciclo_n13['ICMS']

df_ciclo_n13[['Subbrand', 'UF ORIGEM', 'UF', 'ICMS', 'PIS', 'COFINS']].head()

# %% [markdown]
# ## Exportação

# %% [markdown]
# ### Ordem das Planilhas

# %%
# Ordem de Exportação das Colunas
ordem_primaria = [
    # Ciclo N13
    'Tipo 1', 'Tipo 2', 'Tipo 3', 'Regional', 'GP', 'Vend.', 'Gerente', 'Rede', 'COD_CLIENTE', 
    'Company Code', 'CD', 'NOME_CLIENTE', 'UF', 'Região', 'EAN', 'SKU', 'Desc. SKU', 'Classificação', 
    'Tech', 'Tech 2', 'Subbrand', 'Size', 'Nivel 3 HieraR', 'Marca',
    
    # Produtos
    'kg/UN', 'COND. PAG', 'COD REDE', 'COD SUBREDE', 'UF ORIGEM', 'CÓD GP', 'EAN Espelho', 'Family Price',
    'Hierarquia', 'Class.', 'NCM', 'Origem', 'kg/UN', 'Ton/CDA', 'Unid/CDA', 'LSV',

    # ZPs
    'ZP55','CLIENTE', 'CLIENTE_H10', 'CD + UF DESTINO + Importação', 'CD + UF DESTINO + NCM', 'CD + UF DESTINO + H05',
 
    'ZP54', '1. CLIENTE', '1. REDE', '1. GP UF HIER 6', '1. GP UF HIER 5',

    'ZP53', '1. EMISSOR', '1. GP UF', '1. GP', 
    'ZP53d', '2. EMISSOR', '2. REDE', '2. GP UF', '2. GP',

    'ZP52', 'H04', 'H01',
    
    'ZP73',
    'ZP70',

    '1. ZP39', '39. Emissor H12', '39. Emissor H10', '39. Subrede H12', '39. GP UF H12',
    '2. ZP39', '39d. Emissor H12', '39d. Emissor H10', '39d. Subrede H12', '39d. GP UF H12',
    
    # GSVs e NIVs
    'GSV/CDA', 'GSV/TON', 'NIV/CDA', 'NIV/TON',
    
]

colunas_dinamicas = [col for col in df_ciclo_n13.columns if 
                col.startswith("TON") or 
                col.startswith("GSV R$") or 
                col.startswith("Base Imposto")]

ordem_secundaria = [
    'PIS', 'COFINS', 'ICMS'

]

colunas_ordenadas = ordem_primaria + colunas_dinamicas + ordem_secundaria


colunas_existentes = [col for col in colunas_ordenadas if col in df_ciclo_n13.columns]

colunas_faltantes = [col for col in df_ciclo_n13.columns if col not in colunas_existentes]

ordem_final = colunas_existentes + colunas_faltantes


df_ciclo_n13 = df_ciclo_n13[ordem_final]

# %% [markdown]
# ### Formatação
#

# %%
# import time

inicio_export = time.time()





















cols_base = ['Tipo 1',
            'Tipo 2',
            'Tipo 3',
            'Regional',
            'GP',
            'Vend.',
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
            'Tech',
            'Tech 2',
            'Subbrand',
            'Size',
            'Nivel 3 HieraR',
            'Marca'] 

cols_produtos = ['kg/UN', 
'COND. PAG', 
'COD REDE',
'COD SUBREDE',
 'UF ORIGEM',
 'CÓD GP',
 'EAN Espelho',
 'Family Price',
 'Hierarquia',
 'Class.',
 'NCM',
 'Origem',
 'kg/UN',
 'Ton/CDA',
 'Unid/CDA',
 'LSV',]

col_ean = 'EAN Espelho'

cols_zps = ['ZP55', 'ZP54', 'ZP52', 'ZP52', 'ZP53', 'ZP53D', '1. ZP39', '2. ZP39', 'ZP70', 'ZP73', 'PIS',
 'COFINS',
 'ICMS']
cols_financeiras = ['GSV/CDA', 'GSV/TON', 'NIV/CDA', 'NIV/TON']
cols_chaves = [ 'CLIENTE',
 'CLIENTE_H10',
 'CD + UF DESTINO + Importação',
 'CD + UF DESTINO + NCM',
 'CD + UF DESTINO + H05','1. CLIENTE',
 '1. REDE',
 '1. GP UF HIER 6',
 '1. GP UF HIER 5', '1. EMISSOR',
 '1. GP UF',
 '1. GP',
 '2. EMISSOR',
 '2. REDE',
 '2. GP UF',
 '2. GP', 'H04',
 'H01', '39. Emissor H12',
 '39. Emissor H10',
 '39. Subrede H12',
 '39. GP UF H12',
 '39d. Emissor H12',
 '39d. Emissor H10',
 '39d. Subrede H12',
 '39d. GP UF H12',]

cols_4_decimals = ['kg/UN', 'Ton/CDA', 'Unid/CDA', 'LSV']


writer = pd.ExcelWriter('N13_Final_O.xlsx', engine='xlsxwriter')
df_ciclo_n13.to_excel(writer, sheet_name='Valoracao', index=False)

workbook  = writer.book
worksheet = writer.sheets['Valoracao']

# Estilos
estilo_header = {'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter'}

fmt_padrao   = workbook.add_format({**estilo_header, 'bg_color': '#FFFFFF'}) 
fmt_roxo     = workbook.add_format({**estilo_header, 'bg_color': "#7E306A", 'font_color': "#FFFFFF"})
fmt_vermelho = workbook.add_format({**estilo_header, 'bg_color': "#DF3416", 'font_color': "#FFFFFF"})
fmt_azul     = workbook.add_format({**estilo_header, 'bg_color': "#0753A5", 'font_color': "#FFFFFF"})
fmt_cinza    = workbook.add_format({**estilo_header, 'bg_color': "#808080", 'font_color': "#FFFFFF"})
fmt_agua     = workbook.add_format({**estilo_header, 'bg_color': "#00FFFF", 'font_color': "#000000"})
fmt_verde     = workbook.add_format({**estilo_header, 'bg_color': "#06E92C", 'font_color': "#000000"})

fmt_decimal_4 = workbook.add_format({'num_format': '0.0000'})


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

# %% [markdown]
# ## Métricas

# %%
fim_total = time.time()
tempo_total = fim_total - inicio_total


print('# # # Tempos de Execução # # #\n\n'
'Ciclo: {:.2f} segundos\n'
'ZP55: {:.2f} segundos\n'
'ZP54: {:.2f} segundos\n'
'GSV: {:.2f} segundos\n'
'Projeção: {:.2f} segundos\n'
'ZP53: {:.2f} segundos\n'
'ZP52: {:.2f} segundos\n'
'ZP73: {:.2f} segundos\n'
'ZP70: {:.2f} segundos\n'
'ZP39: {:.2f} segundos\n'
'NIV: {:.2f} segundos\n'
'Exportação: {:.2f} segundos\n'
'Total: {:.2f} segundos'
.format(tempo_ciclo, tempo_zp55, tempo_zp54, tempo_gsv, tempo_projecao, tempo_zp53, tempo_zp52, tempo_zp73, tempo_zp70, tempo_zp39, tempo_niv, tempo_exportacao, tempo_total))

print('')

num_linhas = len(df_ciclo_n13)
print(f'Número de linhas do df_ciclo_n13: {num_linhas}')

numeric_sums = df_ciclo_n13.select_dtypes(include=['number']).sum(numeric_only=True)
for coluna, soma in numeric_sums.items():
    print(f'{coluna}: {soma:.4f}')

