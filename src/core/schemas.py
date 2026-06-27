"""
Definição dos Esquemas (Schemas) de Dados do SRM Valoração.

Este módulo centraliza todas as configurações de leitura das fontes de dados
(planilhas de entrada). Ele define as regras de cabeçalho, tipagem de colunas
críticas e validações necessárias para garantir a integridade do processamento.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Type


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
    header_row=0,  # O cabeçalho está na primeira linha (linha indexada como 0)
    engine="openpyxl",
    dtypes={
        "COD_CLIENTE": str,
        "CNPJ": str
    },
    required_columns=[
        "COD_CLIENTE", "NOME_CLIENTE", "REGIONAL", "UF"
    ]
)

BASE_PRODUTOS_SCHEMA = ExcelSheetSchema(
    display_name="Base de Produtos",
    header_row=0,  # O cabeçalho está na primeira linha (linha indexada como 0)
    engine="openpyxl",
    dtypes={
        'EAN': str, 
        'SKU': str,
        'Ton/CDA': float, 
        'Unid/\nCX	': float, 
        'Hierarquia': str,
        'NCM': str,
        'kg/Un': float,
        'H05': str,
        'LSV': float
    },
    required_columns=[
        "EAN", "SKU", "Desc. SKU", "Marca", "Classificação"
    ]





)
