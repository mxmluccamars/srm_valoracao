from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import process_router # Importamos a nossa "porta de entrada" que criaremos a seguir

# 1. Criamos a aplicação (o nosso servidor)
app = FastAPI(
    title="API de Valoração",
    description="Motor matemático para processamento em lote de planilhas",
    version="1.0.0"
)

# 2. Configuração do CORS (Cross-Origin Resource Sharing)
# Como o React (nosso visual) e o FastAPI (nossa matemática) vão rodar em "lugares" diferentes 
# no seu PC enquanto desenvolvemos, precisamos avisar o FastAPI que ele pode conversar com o React.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # O asterisco significa: "Aceite pedidos de qualquer Front-end"
    allow_credentials=True,
    allow_methods=["*"], # Permite todos os comandos (Enviar, Receber, Deletar...)
    allow_headers=["*"], # Permite todos os tipos de informações no cabeçalho
)

# 3. Conectamos a nossa rota ao aplicativo principal.
# É como dizer: "Servidor, adicione essa porta na fachada da casa".
app.include_router(process_router.router)

# 4. Uma Rota "Teste" apenas para sabermos se o servidor ligou.
@app.get("/")
def teste_de_vida():
    return {"mensagem": "Servidor de Valoração está vivo e rodando 100%!"}