# utils.py

import pandas as pd

def limpa_chave(coluna):
    """
    Padroniza colunas para o formato de chave:
    Transforma em string, remove '.0', tira espaços laterais e força maiúscula.
    """
    return (coluna
            .astype(str)
            .str.replace(r'\.0$', '', regex=True)
            .str.strip()
            .str.upper()
           )