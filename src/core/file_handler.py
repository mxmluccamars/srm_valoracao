import os
from typing import Tuple, List

class FileHandler:
    """
    Responsável por encontrar e validar a existência dos arquivos de entrada
    necessários para o processo de valoração em um diretório específico.
    """

    def __init__(self):
        """
        Inicializa o FileHandler com a lista de nomes base dos arquivos estáticos.
        """
        self.static_files = [
            "BASE CLIENTES",
            "BASE PRODUTOS",
            "ZP39",
            "ZP52",
            "ZP53",
            "ZP54",
            "ZP55",
            "ZP70",
            "ZP73",
        ]

    def verify_files(self, directory: str, ano: int, periodo: int) -> Tuple[bool, List[str]]:
        """
        Verifica a existência de todos os arquivos necessários no diretório fornecido.

        Constrói dinamicamente o nome do arquivo de "Ciclo" e verifica a presença de
        todos os arquivos da lista, procurando por extensões .xlsx ou .xlsm.

        Args:
            directory (str): O caminho para a pasta onde os arquivos devem ser procurados.
            ano (int): O ano fornecido pelo usuário para formatar o nome do arquivo de ciclo.
            periodo (int): O período fornecido pelo usuário para formatar o nome do arquivo de ciclo.

        Returns:
            Tuple[bool, List[str]]: 
                - (True, found_paths): Se todos os arquivos foram encontrados, retorna True
                  e a lista com os caminhos completos para cada arquivo.
                - (False, missing_files): Se algum arquivo não foi encontrado, retorna False
                  e a lista com os nomes dos arquivos ausentes.
        """
        # Formata o nome do arquivo dinâmico
        ciclo_filename = f"Ciclo_P{periodo} N13P {ano} - envio"
        
        all_required_basenames = self.static_files + [ciclo_filename]
        
        found_paths = []
        missing_files = []

        print(f"Verificando arquivos no diretório: {directory}") # Log para debug

        for basename in all_required_basenames:
            path_xlsx = os.path.join(directory, f"{basename}.xlsx")
            path_xlsm = os.path.join(directory, f"{basename}.xlsm")

            if os.path.exists(path_xlsx):
                found_paths.append(path_xlsx)
            elif os.path.exists(path_xlsm):
                found_paths.append(path_xlsm)
            else:
                missing_files.append(basename)

        if not missing_files:
            print("Sucesso! Todos os arquivos foram encontrados.") # Log para debug
            return True, found_paths
        else:
            print(f"Erro: Arquivos ausentes: {missing_files}") # Log para debug
            return False, missing_files

