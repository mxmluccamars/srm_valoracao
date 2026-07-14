# TODO terminar de criar os schemes e atualizar no script principal



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
        'CDO GP': str,

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
        'Cadastro': str,
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
        'Cadastro': float,
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
