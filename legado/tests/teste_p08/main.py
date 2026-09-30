# %% [markdown]
# # SRM Valoração

# %% [markdown]
# Projeto de Valoração
# 
# Esse projeto foi desenvolvido para a equipe de SRM, com o objetivo de melhorar o processo de valoração, e assim, reduzir o tempo gasto no processamento dos dados.
# 
# Feito por: 
#     - Juan Lucca
#     - Leonardo Barboza

# %% [markdown]
# ## Importação de bibliotecas

# %% [markdown]
# - Pandas para o processamento dos dados e exportação dos arquivos
# - Path para uma mrlhor organização do caminho dos arquivos
# - Time para o tempo de processamento
# - Numpy para logicas de processamento

# %%
import pandas as pd
from pathlib import Path
import time
import numpy as np
import re

# %% [markdown]
# ## Criação da Base N13P

# %% [markdown]
# Leitura dos arquivos que vão formar a base dos calculos
# 
# Arquivos: 
#     - Ciclo N13P
#     - Base de Clientes
#     - Base de Produtos

# %% [markdown]
# ### Configurações
# 

# %%
# configuração global pandas
pd.set_option('display.float_format', lambda x: f'{x:.4f}' if isinstance(x, (int, float)) else str(x))

# periodo e ano
period = 8
year = 2026

# caminhos dos arquivos
caminho_dados = Path('')

arquivo_n13p = caminho_dados / f"Ciclo P{period:02d} N13P - envio.xlsx"
arquivo_clientes = caminho_dados / 'BASE CLIENTES.xlsx'
arquivo_produtos = caminho_dados / 'BASE PRODUTOS.xlsx'
arquivos_gp = caminho_dados / 'BASE GRUPO DE CLIENTES.xlsx'


# colunas das bases

# n13p
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

# clientes
colunas_clientes = {
    'COD_CLIENTE': str,
    'NOME_CLIENTE': str,
    'UF': str,
    'Rede': str,
    'COD REDE': str,
    'COD SUBREDE': str,
    'COND. PAG': str,
}

# produtos
colunas_produtos = {
    'EAN': str,
    'Descrição': str,
    'SKU': str,
    'Family Price': str,
    'Categoria': str,
    'Brand': str,
    'Sub Brand': str,
    'Ton/CDA': float,
    'Unid/CX': float, # originalmente é 'Unid/\nCX	': float
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

# grupo de preço
colunas_GP = {
    'GP': str,
    'COD GP': str
}

# %% [markdown]
# ### Leitura dos arquivos

# %%
##### leitura dos arquivos #####
start_time = time.time()

# 1. Lemos o cabeçalho e forçamos IMEDIATAMENTE todas as colunas a serem strings
header_df = pd.read_excel(arquivo_n13p, engine='calamine', header=3, nrows=0)
todas_as_colunas_arquivo = [str(col).strip() for col in header_df.columns] # <--- CORREÇÃO: Força string e remove espaços

# Define os padrões (Regex) para encontrar as colunas dinâmicas (agora simples, sem barras extras do Jupyter)
padrao_mensal = re.compile(r'^P\d{2}-\d{4}$')
padrao_anual = re.compile(r'^\d{4}$')

# Filtra as colunas com base nos padrões (garantido que todas são strings)
colunas_periodos_mensais = [col for col in todas_as_colunas_arquivo if padrao_mensal.match(col)]
colunas_totais_anuais = [col for col in todas_as_colunas_arquivo if padrao_anual.match(col)]

print(f"   > Encontradas {len(colunas_periodos_mensais)} colunas de períodos mensais (ex: {colunas_periodos_mensais[:2]}...).")
print(f"   > Encontradas {len(colunas_totais_anuais)} colunas de totais anuais (ex: {colunas_totais_anuais[:2]}...).")

# Adiciona as colunas dinâmicas encontradas ao dicionário de leitura (todas como strings de texto)
for col in colunas_periodos_mensais + colunas_totais_anuais:
    colunas_n13p[col] = float

# n13p
colunas_fixas_normalizadas = {str(col).strip().lower() for col in colunas_n13p.keys() if not padrao_mensal.match(str(col)) and not padrao_anual.match(str(col))}

def checar_coluna_valida(nome_coluna):
    # Transforma o nome recebido da planilha em string limpa
    nome_str = str(nome_coluna).strip()
    
    # 1. Se for uma das colunas fixas que definimos, carrega!
    if nome_str.lower() in colunas_fixas_normalizadas:
        return True
    
    # 2. Se for um período mensal (ex: P03-2026), carrega!
    if padrao_mensal.match(nome_str):
        return True
        
    # 3. Se for um total anual (ex: 2026), carrega!
    if padrao_anual.match(nome_str):
        return True
        
    # Caso contrário, ignora a coluna
    return False


# %%
# n13p lido com filtro dinâmico funcional (Livre de qualquer erro de tipo ou caractere invisível!)
df_n13p = pd.read_excel(
    arquivo_n13p, 
    engine='calamine', 
    header=3, 
    usecols=checar_coluna_valida,
    dtype=colunas_n13p
)


# df_n13p = pd.read_excel(
#     arquivo_n13p, 
#     engine='calamine', 
#     header=3, 
#     usecols=list(colunas_n13p.keys()), 
#     dtype=colunas_n13p
# )
df_n13p.rename(columns={'UF': 'UF DESTINO'}, inplace=True)
df_n13p['COD_CLIENTE'] = df_n13p['COD_CLIENTE'].astype(str).str.strip()

df_n13p.columns = [str(col).strip() for col in df_n13p.columns]

df_n13p.columns.tolist()

# %%
df_n13p.head()

# %%
df_clientes = pd.read_excel(arquivo_clientes, engine='calamine', header=0, usecols=colunas_clientes.keys(), dtype=colunas_clientes)
df_clientes['COD_CLIENTE'] = df_clientes['COD_CLIENTE'].astype(str).str.strip()

df_clientes.head()

# %%
df_produtos = pd.read_excel(arquivo_produtos, engine='calamine', header=0, usecols=colunas_produtos.keys(), dtype=colunas_produtos)
df_produtos.head()

# %%
df_gp = pd.read_excel(arquivos_gp, engine='calamine', header=0, usecols=colunas_GP.keys(), dtype=colunas_GP)
df_gp.head(100)

# %%
df_n13p.dtypes

# %%
# coluna de UF Origem
dicionario_uf = {
    'BR01': 'SP',
    'BR03': 'PE',
    'BR30': 'SP',
    'BR31': 'MG',
}
df_n13p['UF ORIGEM'] = df_n13p['CD'].map(dicionario_uf)

# Ean Espelho
search_ean = df_produtos.set_index('EAN', drop=False)['EAN'].to_dict()
df_n13p['EAN Espelho'] = df_n13p['EAN'].map(search_ean)

search_desc = df_produtos.set_index('Descrição', drop=False)['EAN'].to_dict()
secondary_search = df_n13p['Desc. SKU'].map(search_desc)
df_n13p['EAN Espelho'] = df_n13p['EAN Espelho'].fillna(secondary_search)

# %%
df_n13p.head()

# %%
##### merge de produtos na base #####

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
df_n13p.head()
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

df_n13p.head()


# %%
##### merge de clientes na base #####

# colunas selecionadas
df_clientes_limpo = df_clientes[['COD_CLIENTE', 'COD REDE', 'COD SUBREDE', 'COND. PAG']].drop_duplicates(subset=['COD_CLIENTE'], keep='first')

# merge
df_n13p = pd.merge(
    df_n13p,
    df_clientes_limpo, 
    on='COD_CLIENTE',
    how='left'
)

# merge de grupo de preço na base
df_gp.drop_duplicates(subset=['GP'], keep='first', inplace=True)

df_n13p = pd.merge(
    df_n13p,
    df_gp[['GP', 'COD GP']],
    on='GP',
    how='left'
)

df_n13p.head()

# %% [markdown]
# ## Carregamento dos dados das ZPs

# %% [markdown]
# ZPs:
#      - ZP55 (Tático)
#      - ZP54 (Canal)
#      - ZP53 (P&L)
#      - ZP52 (Contrato)
#      - ZP73 (Logístico)
#      - ZP70 (Pagamento)
#      - ZP39 (Fixo)

# %%
# caminhos
path_zp55 = caminho_dados / 'ZP55.xlsx'
path_zp54 = caminho_dados / 'ZP54.xlsx'
path_zp53 = caminho_dados / 'ZP53.xlsx'
path_zp52 = caminho_dados / 'ZP52.xlsx'
path_zp73 = caminho_dados / 'ZP73.xlsx'
path_zp70 = caminho_dados / 'ZP70.xlsx'
path_zp39 = caminho_dados / 'ZP39.xlsx'

# colunas e tipos
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

colunas_zp52 = {
    'Chaves': str,
    'Cadastro SAP': str,
    'Org. Vendas': str,
    'Rede': str,
    'H01': str,
    'Cadastro': float,
    'Fim': str,
}

colunas_zp73 = {
    'CHAVE': str,
    'Cadastro SAP': str,
    'Org. Vendas': str,
    'Emissor': str,
    'Rede': str,
    'H01': str,
    'Cadastro': float,
    'Fim': str,
}

colunas_zp70 = {
    'CONDICAO DE PAGAMENTO': str,
    'Desconto': float,
}

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

##### LEITURA E TRATAMENTO #####

# uso da biblioteca calamine para ler os arquivos

df_zp55 = pd.read_excel(
    path_zp55, 
    engine='calamine', 
    header=1,
    usecols=colunas_zp55.keys(), 
    dtype=colunas_zp55
)

df_zp54 = pd.read_excel(
    path_zp54, 
    engine='calamine', 
    header=1,
    usecols=colunas_zp54.keys(), 
    dtype=colunas_zp54
)

df_zp53 = pd.read_excel(
    path_zp53, 
    engine='calamine', 
    header=1,
    usecols=colunas_zp53.keys(), 
    dtype=colunas_zp53
)

df_zp52 = pd.read_excel(
    path_zp52, 
    engine='calamine', 
    header=1,
    usecols=colunas_zp52.keys(), 
    dtype=colunas_zp52
)

df_zp73 = pd.read_excel(
    path_zp73, 
    engine='calamine', 
    header=2,
    usecols=colunas_zp73.keys(), 
    dtype=colunas_zp73
)

df_zp70 = pd.read_excel(
    path_zp70, 
    engine='calamine', 
    header=0,
    usecols=colunas_zp70.keys(), 
    dtype=colunas_zp70
)

df_zp39 = pd.read_excel(
    path_zp39, 
    engine='calamine', 
    header=1,
    usecols=colunas_zp39.keys(), 
    dtype=colunas_zp39
)


# %% [markdown]
# ## Carregamento da base de impostos

# %%
# caminho
path_impostos = caminho_dados / 'BASE IMPOSTOS.xlsx'

# aqui levos sem declarar as colunas por ter varias com nomes diferentes
df_impostos = pd.read_excel(
    path_impostos,
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
    path_impostos,
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

# %% [markdown]
# ## Calculos

# %% [markdown]
# ### ZP55

# %%
# criação do dicionário de chaves

df_zp55_limpo = df_zp55.drop_duplicates(subset=['CHAVE'], keep='first').copy()
df_zp55_limpo['CHAVE'] = df_zp55_limpo['CHAVE'].astype(str).str.strip()
dic_zp55 = df_zp55_limpo.set_index('CHAVE')['Cadastro'].to_dict()


# chaves de busca
company_code = df_n13p['Company Code'].astype(str).str.strip()
cod_cliente = df_n13p['COD_CLIENTE'].astype(str).str.strip()
hierarquia = df_n13p['Hierarquia'].astype(str).str.strip()
cd = df_n13p['CD'].astype(str).str.strip()
uf = df_n13p['UF DESTINO'].astype(str).str.strip()
origem = df_n13p['Origem'].astype(str).str.strip()
ncm = df_n13p['NCM'].astype(str).str.strip()

chave_1 = company_code + '_' + cod_cliente + '_' + hierarquia                  # CLIENTE
chave_2 = company_code + '_' + cod_cliente + '_' + hierarquia.str[:10]         # CLIENTE H05
chave_3 = cd + '_' + uf + '_' + origem                                         # CD + UF + Importação
chave_4 = cd + '_' + uf + '_' + ncm                                            # CD + UF + NCM
chave_5 = cd + '_' + uf + '_' + hierarquia.str[:10]                            # CD + UF + H05


# montagem das colunas
df_n13p['ZP55 CLIENTE'] = chave_1.map(dic_zp55) / 100
df_n13p['ZP55 CLIENTE H05'] = chave_2.map(dic_zp55) / 100
df_n13p['ZP55 CD + UF DESTINO + Importação'] = chave_3.map(dic_zp55) / 100
df_n13p['ZP55 CD + UF DESTINO + NCM'] = chave_4.map(dic_zp55) / 100
df_n13p['ZP55 CD + UF DESTINO + H05'] = chave_5.map(dic_zp55) / 100

# aplicação das regras
df_n13p['ZP55'] = (df_n13p['ZP55 CLIENTE']
                   .fillna(df_n13p['ZP55 CLIENTE H05'])
                   .fillna(df_n13p['ZP55 CD + UF DESTINO + Importação'])
                   .fillna(df_n13p['ZP55 CD + UF DESTINO + NCM'])
                   .fillna(df_n13p['ZP55 CD + UF DESTINO + H05'])
                  )

# %% [markdown]
# ### ZP54

# %%
# criação do dicionário de chaves
df_zp54_limpo = df_zp54.drop_duplicates(subset=['CHAVE'], keep='first').copy()
df_zp54_limpo['CHAVE'] = df_zp54_limpo['CHAVE'].astype(str).str.strip()
dic_zp54 = df_zp54_limpo.set_index('CHAVE')['Cadastro'].to_dict()

# chaves de buscas
company_code = df_n13p['Company Code'].astype(str).str.strip()
cod_cliente = df_n13p['COD_CLIENTE'].astype(str).str.strip()
cod_subrede = df_n13p['COD SUBREDE'].astype(str).str.strip()
cod_gp = df_n13p['COD GP'].astype(str).str.strip()
uf = df_n13p['UF DESTINO'].astype(str).str.strip()
hierarquia = df_n13p['Hierarquia'].astype(str).str.strip()

chave_1 = company_code + '_' + cod_cliente + '_' + hierarquia                       # CLIENTE
chave_2 = company_code + '_' + cod_subrede + '_' + hierarquia                       # REDE
chave_3 = company_code + '_' + cod_gp + ' ' + uf + '_' + hierarquia                 # GP UF HIER 6
chave_4 = company_code + '_' + cod_gp + ' ' + uf + '_' + hierarquia.str[:10]        # GP UF HIER 5

# montagem das colunas
df_n13p['ZP54 CLIENTE'] = chave_1.map(dic_zp54) / 100
df_n13p['ZP54 REDE'] = chave_2.map(dic_zp54) / 100
df_n13p['ZP54 GP UF HIER 6'] = chave_3.map(dic_zp54) / 100
df_n13p['ZP54 GP UF HIER 5'] = chave_4.map(dic_zp54) / 100

# aplicação das regras
df_n13p['ZP54'] = (df_n13p['ZP54 CLIENTE']
                   .fillna(df_n13p['ZP54 REDE'])
                   .fillna(df_n13p['ZP54 GP UF HIER 6'])
                   .fillna(df_n13p['ZP54 GP UF HIER 5'])
                  )

# %% [markdown]
# ### GSV (Gross Sales Value)

# %%
# GSV = LSV * (1 + ZP55) * (1 + ZP54)
df_n13p['GSV/CDA'] = df_n13p['LSV'] * (1 + df_n13p['ZP55']) * (1 + df_n13p['ZP54'])

coluna_gsv_cda = df_n13p['GSV/CDA'] 
coluna_kg_un = df_n13p['kg/Un'] 
coluna_unid_cda = df_n13p['Unid/CX']
denominador_peso = coluna_kg_un * coluna_unid_cda

# GSV/TON = (GSV/CDA) / (kg/Un * Unid/CX) * 1000
df_n13p['GSV/TON'] = np.where(
    (denominador_peso == 0) | (denominador_peso.isna()),
    np.nan,                                
    (coluna_gsv_cda / denominador_peso) * 1000           
)

# --- Projeções Dinâmicas (MENSAL E ANUAL AUTOMÁTICAS) ---
print("\nCalculando projeções de receita dinâmicas (GSV R$)...")

# 1. Calcula para os meses (ex: GSV R$ P03-2026)
for p in colunas_periodos_mensais:
    nome_coluna_projecao = f'GSV R$ {p}'
    df_n13p[nome_coluna_projecao] = df_n13p[p] * df_n13p['GSV/TON']

# 2. Calcula para os acumulados anuais (ex: GSV R$ 2026)
for p_anual in colunas_totais_anuais:
    nome_coluna_projecao = f'GSV R$ {p_anual}'
    df_n13p[nome_coluna_projecao] = df_n13p[p_anual] * df_n13p['GSV/TON']

print("✅ Projeções mensais e anuais calculadas com sucesso de forma dinâmica!")


# %% [markdown]
# ### ZP53

# %%
# limpeza das colunas e criação do dicionário de chaves
df_zp53_limpo = df_zp53.drop_duplicates(subset=['Chaves'], keep='first').copy()
df_zp53_limpo['Chaves'] = df_zp53_limpo['Chaves'].astype(str).str.strip()
dic_zp53_cadastro = df_zp53_limpo.set_index('Chaves')['Cadastro'].to_dict()
dic_zp53_validade = df_zp53_limpo.set_index('Chaves')["Fim"].to_dict()

# chaves de busca
company_code = df_n13p['Company Code'].astype(str).str.strip()
cod_cliente = df_n13p['COD_CLIENTE'].astype(str).str.strip()
cod_subrede = df_n13p['COD SUBREDE'].astype(str).str.strip()
cod_gp = df_n13p['COD GP'].astype(str).str.strip() # Ajustado para o nome oficial correto
uf = df_n13p['UF DESTINO'].astype(str).str.strip()
hierarquia = df_n13p['Hierarquia'].astype(str).str.strip()

chave_1 = company_code + '_' + cod_cliente + '_' + hierarquia                       # EMISSOR
chave_2 = company_code + '_' + cod_subrede + '_' + hierarquia                       # REDE
chave_3 = company_code + '_' + cod_gp + ' ' + uf + '_' + hierarquia                 # GP UF
chave_4 = company_code + '_' + cod_gp + '_' + hierarquia.str[:10]                   # GP

# busca e aplicação das chaves de valores
df_n13p['ZP53 EMISSOR'] = chave_1.map(dic_zp53_cadastro) / 100
df_n13p['ZP53 REDE'] = chave_2.map(dic_zp53_cadastro) / 100
df_n13p['ZP53 GP UF'] = chave_3.map(dic_zp53_cadastro) / 100
df_n13p['ZP53 GP'] = chave_4.map(dic_zp53_cadastro) / 100

df_n13p['ZP53'] = (df_n13p['ZP53 EMISSOR']
                   .fillna(df_n13p['ZP53 REDE'])
                   .fillna(df_n13p['ZP53 GP UF'])
                   .fillna(df_n13p['ZP53 GP'])
                   .fillna(0) # Se não encontrar correspondência, adota 0
                  )

# busca e aplicação das chaves de datas de validade
df_n13p['ZP53d EMISSOR'] = chave_1.map(dic_zp53_validade)
df_n13p['ZP53d REDE'] = chave_2.map(dic_zp53_validade)
df_n13p['ZP53d GP UF'] = chave_3.map(dic_zp53_validade)
df_n13p['ZP53d GP'] = chave_4.map(dic_zp53_validade)

df_n13p['ZP53d'] = (df_n13p['ZP53d EMISSOR']
                    .fillna(df_n13p['ZP53d REDE'])
                    .fillna(df_n13p['ZP53d GP UF'])
                    .fillna(df_n13p['ZP53d GP'])
                    .fillna(0)
                   )

# %% [markdown]
# ### ZP52

# %%
# criação do dicionário de chaves
df_zp52_limpo = df_zp52.drop_duplicates(subset=['Chaves'], keep='first').copy()
df_zp52_limpo['Chaves'] = df_zp52_limpo['Chaves'].astype(str).str.strip()
dic_zp52 = df_zp52_limpo.set_index('Chaves')['Cadastro'].to_dict()

# cahves de busca
company_code = df_n13p['Company Code'].astype(str).str.strip()
cod_cliente = df_n13p['COD_CLIENTE'].astype(str).str.strip()
cod_subrede = df_n13p['COD SUBREDE'].astype(str).str.strip()
hierarquia = df_n13p['Hierarquia'].astype(str).str.strip()

chave_1 = company_code + '_' + cod_cliente + '_' + hierarquia.str[:8]              # H04
chave_2 = company_code + '_' + cod_subrede + '_' + hierarquia.str[:2]              # H01


# busca e aplicação de prioridades
df_n13p['ZP52 H04'] = chave_1.map(dic_zp52) / 100
df_n13p['ZP52 H01'] = chave_2.map(dic_zp52) / 100

df_n13p['ZP52'] = (df_n13p['ZP52 H04']
                   .fillna(df_n13p['ZP52 H01'])
                   .fillna(0) # Adota 0 caso nenhuma regra combine
                  )

# %% [markdown]
# ### ZP73

# %%
# criação do dicionário de chaves
df_zp73_limpo = df_zp73.drop_duplicates(subset=['CHAVE'], keep='first').copy()
df_zp73_limpo['CHAVE'] = df_zp73_limpo['CHAVE'].astype(str).str.strip()
dic_zp73 = df_zp73_limpo.set_index('CHAVE')['Cadastro'].to_dict()

# chaves de busca
company_code = df_n13p['Company Code'].astype(str).str.strip()
cod_cliente = df_n13p['COD_CLIENTE'].astype(str).str.strip()
cod_subrede = df_n13p['COD SUBREDE'].astype(str).str.strip()

chave_1 = company_code + '_' + cod_cliente                                        # CLIENTE
chave_2 = company_code + '_' + cod_subrede                                        # REDE

# busca e aplicação das regras
df_n13p['ZP73 CLIENTE'] = (chave_1.map(dic_zp73) / 100)
df_n13p['ZP73 REDE'] = (chave_2.map(dic_zp73) / 100)

df_n13p['ZP73'] = (df_n13p['ZP73 CLIENTE']
                   .fillna(df_n13p['ZP73 REDE'])
                   .fillna(0) # Adota 0 caso nenhuma regra combine
                  )

# %% [markdown]
# ### ZP70

# %%
# criação do dicionário de chaves
df_zp70_limpo = df_zp70.drop_duplicates(subset=['CONDICAO DE PAGAMENTO'], keep='first').copy()
df_zp70_limpo['CONDICAO DE PAGAMENTO'] = df_zp70_limpo['CONDICAO DE PAGAMENTO'].astype(str).str.strip()
dic_zp70 = df_zp70_limpo.set_index('CONDICAO DE PAGAMENTO')['Desconto'].to_dict()

# chaves de busca
chave_cond_pag = df_n13p['COND. PAG'].astype(str).str.strip()

# busca e aplicação das regras de desconto
df_n13p['ZP70'] = chave_cond_pag.map(dic_zp70)

# %% [markdown]
# ### ZP39

# %%
# criação do dicionário de chaves
df_zp39_limpo = df_zp39.drop_duplicates(subset=['CHAVE'], keep='first').copy()
df_zp39_limpo['CHAVE'] = df_zp39_limpo['CHAVE'].astype(str).str.strip()
dic_zp39_cadastro = df_zp39_limpo.set_index('CHAVE')['Cadastro'].to_dict()
dic_zp39_validade = df_zp39_limpo.set_index('CHAVE')["Fim"].to_dict()

# chaves de busca
company_code = df_n13p['Company Code'].astype(str).str.strip()
cod_cliente = df_n13p['COD_CLIENTE'].astype(str).str.strip()
cod_subrede = df_n13p['COD SUBREDE'].astype(str).str.strip()
cod_gp = df_n13p['COD GP'].astype(str).str.strip() # Ajustado para o nome oficial correto
uf = df_n13p['UF DESTINO'].astype(str).str.strip()
hierarquia = df_n13p['Hierarquia'].astype(str).str.strip()

chave_1 = company_code + '_' + cod_cliente + '_' + hierarquia                       # Emissor H12
chave_2 = company_code + '_' + cod_cliente + '_' + hierarquia.str[:10]              # Emissor H10
chave_3 = company_code + '_' + cod_subrede + '_' + hierarquia                       # Subrede H12
chave_4 = company_code + '_' + cod_gp + ' ' + uf + '_' + hierarquia                 # GP UF H12

# busca e aplicação das regras de desconto
df_n13p['ZP39 Emissor H12'] = (chave_1.map(dic_zp39_cadastro) / 100)
df_n13p['ZP39 Emissor H10'] = (chave_2.map(dic_zp39_cadastro) / 100)
df_n13p['ZP39 Subrede H12'] = (chave_3.map(dic_zp39_cadastro) / 100)
df_n13p['ZP39 GP UF H12'] = (chave_4.map(dic_zp39_cadastro) / 100)

df_n13p['ZP39'] = (df_n13p['ZP39 Emissor H12']
                      .fillna(df_n13p['ZP39 Emissor H10'])
                      .fillna(df_n13p['ZP39 Subrede H12'])
                      .fillna(df_n13p['ZP39 GP UF H12'])
                      .fillna(0) # Se não encontrar, assume 0
                     )

# busca e aplicação das datas de validade
df_n13p['ZP39d Emissor H12'] = chave_1.map(dic_zp39_validade)
df_n13p['ZP39d Emissor H10'] = chave_2.map(dic_zp39_validade)
df_n13p['ZP39d Subrede H12'] = chave_3.map(dic_zp39_validade)
df_n13p['ZP39d GP UF H12'] = chave_4.map(dic_zp39_validade)

df_n13p['ZP39d'] = (df_n13p['ZP39d Emissor H12']
                      .fillna(df_n13p['ZP39d Emissor H10'])
                      .fillna(df_n13p['ZP39d Subrede H12'])
                      .fillna(df_n13p['ZP39d GP UF H12'])
                      .fillna(0)
                     )

# %% [markdown]
# ### NIV (Net Invoice Value)

# %%
# multiplicação
df_n13p['NIV/CDA'] = (
    df_n13p['GSV/CDA'] * 
    (1 + df_n13p['ZP53']) * 
    (1 + df_n13p['ZP52']) * 
    (1 + df_n13p['ZP73']) * 
    (1 + df_n13p['ZP70']) * 
    (1 + df_n13p['ZP39'])
)

# colunas usadas na conversão
coluna_niv_cda = df_n13p['NIV/CDA']
coluna_kg_un = df_n13p['kg/Un']       # Usando o nome exato da sua coluna: 'kg/Un'
coluna_unid_cda = df_n13p['Unid/CX']  # Usando o nome exato da sua coluna: 'Unid/CX'
denominador_peso = coluna_kg_un * coluna_unid_cda

# divisão
df_n13p['NIV/TON'] = np.where(
    (denominador_peso == 0) | (denominador_peso.isna()),
    np.nan,                                
    (coluna_niv_cda / denominador_peso) * 1000           
)

# %% [markdown]
# ### ICMS

# %%
# chaves de busca
cd = df_n13p['CD'].astype(str).str.strip()
cod_cliente = df_n13p['COD_CLIENTE'].astype(str).str.strip()
subbrand = df_n13p['Subbrand'].astype(str).str.strip()
uf_origem = df_n13p['UF ORIGEM'].astype(str).str.strip()
uf_destino = df_n13p['UF DESTINO'].astype(str).str.strip()

# dicionários de busca
dic_alc_zf = df_alc_zf.set_index('CHAVE EMISSOR')['Regra'].to_dict()
dic_icms_padrao = df_impostos_padrao.set_index('Chave')['Aliq_ICMS'].to_dict()
dic_icms_exc = df_impostos_excecao.set_index('exc_Chave')['exc_Aliq_ICMS'].to_dict()

# busca na zona franca
chave_alc_zf = cod_cliente + cd
val_zf = chave_alc_zf.map(dic_alc_zf)

# busca na padrão
chave_icms_padrao = uf_origem + uf_destino
val_icms_padrao = chave_icms_padrao.map(dic_icms_padrao)

# busca na exceção
chave_icms_exc = subbrand + uf_origem + uf_destino
val_icms_exc = chave_icms_exc.map(dic_icms_exc)

# regras de aplicação

# zf
resultado_r1 = val_zf

# exceção de PED e SHE
cond_r2 = df_n13p['Subbrand'].isin(["PED DTX", "SHE SCKS"])
resultado_r2 = val_icms_exc.where(cond_r2)

# excecão de FILEZITOS
cond_r3 = (df_n13p['Subbrand'] == 'PED FILEZITOS') & (df_n13p['CD'] == 'BR31') & (df_n13p['UF DESTINO'].isin(['ES', 'MG']))
resultado_r3 = val_icms_exc.where(cond_r3)

# cascata
icms_final = (resultado_r1
                .fillna(resultado_r2)
                .fillna(resultado_r3)
                .fillna(val_icms_padrao)
                .fillna(0)
            )

df_n13p['ICMS'] = icms_final

# %% [markdown]
# ### PIS

# %%
# criação do dicionário de chaves
dic_pis = df_impostos_padrao.set_index('Chave')['Aliq_PIS'].to_dict()

# chaves de busca
uf_origem = df_n13p['UF ORIGEM'].astype(str).str.strip()
uf_destino = df_n13p['UF DESTINO'].astype(str).str.strip()
chave_1 = uf_origem + uf_destino

# busca
df_n13p['PIS'] = (chave_1.map(dic_pis)).fillna(0)



# %% [markdown]
# ### COFINS

# %%
# criação do dicionário de chaves
dic_cofins = df_impostos_padrao.set_index('Chave')['Aliq_Cofins'].to_dict()

# chaves de busca
uf_origem = df_n13p['UF ORIGEM'].astype(str).str.strip()
uf_destino = df_n13p['UF DESTINO'].astype(str).str.strip()
chave_1 = uf_origem + uf_destino

# busca
df_n13p['COFINS'] = (chave_1.map(dic_cofins)).fillna(0)

# %% [markdown]
# ### NF Prazo

# %%
# denominador da conversão
denominador_cda = (1 - df_n13p['ICMS'])

# divisão segura
df_n13p['NF PRAZO/CDA'] = np.where(
    denominador_cda == 0,
    np.nan,
    (df_n13p['NIV/CDA'] / denominador_cda) * (1 - df_n13p['PIS'] - df_n13p['COFINS'])
)


coluna_nf_prazo = df_n13p['NF PRAZO/CDA']
coluna_kg_un = df_n13p['kg/Un']       # Usando o nome exato da sua coluna: 'kg/Un'
coluna_unid_cda = df_n13p['Unid/CX']  # Usando o nome exato da sua coluna: 'Unid/CX'

denominador_peso = coluna_kg_un * coluna_unid_cda

# divisão segura
df_n13p['NF PRAZO/TON'] = np.where(
    (denominador_peso == 0) | (denominador_peso.isna()),
    np.nan,                                
    (coluna_nf_prazo / denominador_peso)
)


# %% [markdown]
# ## Exportação

# %% [markdown]
# ### Ordenação das colunas

# %%
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

# %% [markdown]
# ### Definição da formatação das colunas

# %%
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

# %% [markdown]
# ### Salvamento em Excel

# %%
# nome do arquivo final
# nome_arquivo_formatado = f'N13_P{period:02d}_{year}.xlsx'
nome_arquivo_formatado = 'N13_P08.1.0.xlsx'

writer = pd.ExcelWriter(nome_arquivo_formatado, engine='xlsxwriter')

total_linhas = len(df_n13p)
print(f"total de linhas a serem salvas: {total_linhas}")

tamanho_chunk = 50000
progresso_inicial = 0
progresso_final = 100
margem_progresso = progresso_final - progresso_inicial

for i in range(0, total_linhas, tamanho_chunk):
    # corta o dataframe pro pedaço atual
    chunk = df_n13p_ordenado.iloc[i : i + tamanho_chunk]

    # verifica se é cabeçalho ou não
    if i == 0:
        chunk.to_excel(writer, sheet_name='Valoracao', index=False, startrow=8, header=True)
    else:
        chunk.to_excel(writer, sheet_name='Valoracao', index=False, startrow=i + 9, header=False)

    # calcula o progresso dinamico das linhas salvas
    linhas_processadas = min(i + tamanho_chunk, total_linhas)
    porcentagem_linhas = linhas_processadas / total_linhas
    progresso_atual = int(progresso_inicial + (porcentagem_linhas * margem_progresso))
    print(f"Salvando linhas no Excel: {linhas_processadas:,} de {total_linhas:,} concluídas... Total: {progresso_atual}%")


# %% [markdown]
# ### Personalização do estilo do Excel

# %%
print('1')
workbook  = writer.book
worksheet = writer.sheets['Valoracao']

print('2')
# adiciona linhas vazias acima da planilha
worksheet.autofilter(8, 0, total_linhas + 8, len(df_n13p_ordenado.columns) - 1)

# esconde as linhas verticais
worksheet.hide_gridlines(2)

# estilos de formatação
estilo_header = {
    'bold': True, 'top': 1, 'top_color': '#000000', 
    'align': 'left', 'valign': 'vcenter', 
    'font_name': 'Mars Centra'}

print('3')
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

print('4')
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

print('5')
# save
writer.close()
print('6')

print(f"Arquivo salvo como: {Path(nome_arquivo_formatado).resolve()}")


