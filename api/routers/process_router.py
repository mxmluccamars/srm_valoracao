from fastapi import APIRouter, File, UploadFile, Form
from typing import List

# Criamos um "Roteador". Ele funciona como um carteiro, que pega a encomenda 
# (os arquivos) e entrega na função certa.
router = APIRouter()

# Criamos a nossa rota principal. Usamos POST porque o usuário vai 
# "postar" (enviar) um pacote de dados pesados para o nosso servidor.
@router.post("/api/processar-valoracao")
async def processar_valoracao(
    # Aqui definimos as ENTRADAS que o nosso Back-end exige:
    
    # 1. 'arquivos': Vai ser uma Lista de múltiplos arquivos (List[UploadFile]).
    # O 'File(...)' avisa o sistema que isso virá por upload.
    arquivos: List[UploadFile] = File(...),
    
    # 2. 'ciclo': Uma string (texto). O 'Form(...)' significa que isso virá junto com os arquivos.
    ciclo: str = Form(...),
    
    # 3. 'ano': Outra string.
    ano: str = Form(...)
):
    """
    Este é o nosso Portão de Entrada! Quando o usuário clicar em "Calcular" no Front-end,
    os arquivos e as variáveis (ciclo e ano) vão cair direto aqui.
    """
    
    # Por enquanto, como ainda não colocamos a sua matemática aqui dentro, 
    # vamos apenas extrair os nomes dos arquivos que chegaram para testar se funcionou.
    nomes_dos_arquivos = [arquivo.filename for arquivo in arquivos]

    # O servidor responde devolvendo um aviso de sucesso e os dados que ele leu:
    return {
        "status": "Sucesso",
        "mensagem": "As bases de dados chegaram no Motor Matemático!",
        "ciclo_recebido": ciclo,
        "ano_recebido": ano,
        "quantidade_de_arquivos": len(arquivos),
        "arquivos_lidos": nomes_dos_arquivos
    }