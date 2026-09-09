# Projeto Valoração 🚀

Este projeto tem como objetivo otimizar e automatizar o processo de valoração, processando de forma rápida diversas planilhas em lote através de uma interface gráfica simples e profissional, exportando os resultados consolidados.

## 🛠️ Tecnologias Utilizadas

- **Python**: Linguagem base.
- **Pandas**: Processamento e manipulação dos dados.
- **PySide6**: Interface gráfica do usuário (GUI).
- **PyInstaller**: Empacotamento e geração do executável `.exe`.

## 📂 Estrutura do Projeto

- `src/ui/`: Telas e elementos visuais da aplicação.
- `src/core/`: Regras de negócio, cálculos e validação de arquivos.
- `src/utils/`: Funções utilitárias e logs.
- `main.py`: Arquivo de inicialização.

## 🚀 Como Rodar o Projeto em Desenvolvimento

1. Crie o ambiente virtual: `python -m venv .venv`
2. Ative o ambiente: `.venv\Scripts\activate`
3. Instale as dependências: `pip install -r requirements.txt`
4. Execute o projeto: `python main.py`


---

## 📊 Estrutura de Dados de Entrada

Para que o processamento seja bem-sucedido, os seguintes arquivos devem estar presentes na mesma pasta que o executável. O sistema é flexível e aceita tanto a extensão `.xlsx` quanto `.xlsm`.

### Arquivos Estáticos
- `BASE CLIENTES`
- `BASE PRODUTOS`
- `ZP39`
- `ZP52`
- `ZP53`
- `ZP54`
- `ZP55`
- `ZP70`
- `ZP73`

### Arquivo Dinâmico
O nome deste arquivo depende do **Ano** e **Período** informados na interface, seguindo o padrão:
- `Ciclo_P<periodo> N13P <ANO> - envio`

**Exemplo:** Para o ano `2024` e período `1`, o arquivo esperado seria `Ciclo_P1 N13P 2024 - envio.xlsx`.
