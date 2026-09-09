# components/uploader.py

import streamlit as st
import re
from datetime import datetime

def _desenhar_card_compacto(descricao, arquivo_encontrado=None):
    """
    Função auxiliar que gera o HTML de um card de status usando classes CSS.
    O estilo é definido na função principal.
    """
    if arquivo_encontrado:
        cor_borda = "#0900A7"
        icone = "☑️"
        nome_arquivo = f"<b>Arquivo:</b> `{arquivo_encontrado.name}`"
    else:
        cor_borda = "#FFDB00"
        icone = "⚠️"
        nome_arquivo = "Aguardando..."
        
    # HTML do card, agora usando classes em vez de estilo inline
    card_html = f'''
        <div class="card-wrapper" style="border-left-color: {cor_borda};">
            <p class="card-title">{icone} {descricao}</p>
            <small class="card-filename">{nome_arquivo}</small>
        </div>
    '''
    st.markdown(card_html, unsafe_allow_html=True)

def render_uploader():
    """
    Desenha a seção de upload com um st.file_uploader customizado e os cards de status.
    """

    ARQUIVO_HERO = {'N13P': 'Ciclo N13P'}
    ARQUIVOS_BASES = {
        'BASE CLIENTES': 'Base de Dados de Clientes',
        'BASE PRODUTOS': 'Base de Dados de Produtos',
        'BASE IMPOSTOS': 'Base de Dados de Impostos'
    }
    ARQUIVOS_ZPS = {
        'ZP55': 'ZP55', 'ZP54': 'ZP54', 'ZP53': 'ZP53', 'ZP52': 'ZP52',
        'ZP73': 'ZP73', 'ZP70': 'ZP70', 'ZP39': 'ZP39'
    }

    # --- INÍCIO DA SEÇÃO DE UPLOAD ---
    
    # st.subheader("📂 Dashboard de Carregamento") # Título removido, como solicitado.

    # --- Bloco de CSS com Comentários para Personalização ---
    st.markdown(
        """
        <style>
            /* --- Contêiner Principal do File Uploader --- */
            [data-testid="stFileUploader"] {
                background-color: #0900A7;
                border: 2px dashed #4B5563;
                border-radius: 10px;
                padding: 1.5rem;
            }

            /* --- Label Principal do componente (ex: "Carregue aqui...") --- */
            [data-testid="stFileUploader"] label {
                color: #F8F7F2  !important;
                font-size: 1.1rem;
            }

            /* --- A SOLUÇÃO DEFINITIVA --- */
            /* Encontra o parágrafo de texto informativo ("Drag and drop...") DENTRO 
               da área de upload e o ESCONDE completamente. */
            [data-testid="stFileUploader"] section p {
                display: none !important;
            }

            /* --- Botão "Browse files" / "upload" --- */
            /* Agora que só temos o botão, podemos estilizá-lo sem medo de conflito. */
            [data-testid="stFileUploader"] section button {
                /* ESTAS SÃO AS LINHAS QUE CORRIGEM O PROBLEMA */
                min-width: 180px;      /* Garante uma largura mínima para o botão */
                padding: 0.5rem 2rem;  /* Adiciona espaçamento interno (vertical e horizontal) */
                border-radius: 8px;    /* Deixa as bordas do botão arredondadas */
                
                /* Estilos que você já tinha */
                background-color: #0900A7;
                color: #1F2937;
                border: none;
                font-weight: 600; /* Deixa o texto do botão um pouco mais forte */
            }
            [data-testid="stFileUploader"] section button:hover {
                background-color: #73FBFD;
                color: #F8F7F2;
            }




            /* --- Estilo do Card Individual --- */
            .card-wrapper {
                /* Define a cor de fundo do card. */
                background-color: #00DCCF;

                /* Define o quão arredondadas são as bordas. */
                border-radius: 5px;

                /* Define a espessura da borda colorida à esquerda (a cor é definida dinamicamente). */
                border-left-width: 5px;
                border-left-style: solid;
                
                /* Adiciona uma sombra sutil para dar profundidade e fazer o card "flutuar". */
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);

                /* Define a altura fixa do card. */
                height: 85px;

                /* Define o espaçamento interno para o conteúdo não colar nas bordas. */
                padding: 1rem;

                /* Usa flexbox para alinhar o conteúdo interno verticalmente. */
                display: flex;
                flex-direction: column;
                justify-content: center;

                /* Adiciona um espaço abaixo de cada card. */
                margin-bottom: 10px;

                /* Adiciona uma transição suave para futuros efeitos de hover. */
                transition: all 0.2s ease-in-out;
            }

            /* Efeito de hover: o que acontece quando o mouse passa por cima do card. */
            .card-wrapper:hover {
                /* Faz o card "levantar" um pouco da página. */
                transform: translateY(-3px);
                border: 3px solid #FFDB00;

                /* Aumenta a intensidade da sombra para realçar o efeito. */
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }

            /* --- Estilo do Título do Card --- */
            .card-title {
                /* Define a cor do texto do título principal. */
                color: #0900A7;

                /* Define a família da fonte (herda do global, mas pode ser sobrescrita aqui). */
                font-family: 'Montserrat', sans-serif;

                /* Define o peso da fonte (600 é semibold). */
                font-weight: 600;

                /* Define o tamanho da fonte. */
                font-size: 1rem;

                /* Remove margens padrão para controle total do layout. */
                margin: 0;
                padding: 0;
            }

            /* --- Estilo do Nome do Arquivo / Status --- */
            .card-filename {
                /* Define a cor do texto secundário. */
                color: #0900A7;
                font-size: 0.75rem;

                /* As 3 linhas abaixo criam o efeito de "..." se o nome do arquivo for muito longo. */
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }


            /* --- ESTILO PARA A MENSAGEM DE SUCESSO (st.success) --- */
            /* Este seletor mira na caixa verde de sucesso. */
            [data-testid="stSuccess"] {
                /* Define a cor de fundo da caixa. */
                background-color: #00DCCF; /* Exemplo: Um verde pastel claro */

                /* Define a cor da borda esquerda. */
                border-left-color: #28A745; /* Exemplo: O mesmo verde da borda dos cards */
                
                /* Define a cor do ícone e do texto dentro da caixa. */
                color: #155724; /* Exemplo: Um verde escuro para boa legibilidade */
            }

            /* --- ESTILO PARA A MENSAGEM DE ERRO (st.error) --- */
            /* Este seletor mira na caixa vermelha de erro. */
            [data-testid="stError"] {
                /* Define a cor de fundo da caixa. */
                background-color: #F8D7DA; /* Exemplo: Um vermelho/rosa pastel claro */

                /* Define a cor da borda esquerda. */
                border-left-color: #DC3545; /* Exemplo: Um vermelho forte */
                
                /* Define a cor do ícone e do texto dentro da caixa. */
                color: #721C24; /* Exemplo: Um vermelho escuro/vinho */
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    arquivos_carregados = st.file_uploader(
        label="Carregue aqui as 11 planilhas necessárias para o cálculo.", # Label mais direto
        type=["xlsx", "csv"],
        accept_multiple_files=True,
        label_visibility="visible" # Mantém o label visível, pois ele agora é o título
    )
    
    # st.markdown("---")

    # Lógica de Processamento
    ARQUIVOS_ESPERADOS = {**ARQUIVO_HERO, **ARQUIVOS_BASES, **ARQUIVOS_ZPS}
    arquivos_encontrados = {}
    ciclo_final = None
    if arquivos_carregados:
        for nome_esperado in ARQUIVOS_ESPERADOS:
            for arquivo in arquivos_carregados:
                if nome_esperado in arquivo.name.upper():
                    arquivos_encontrados[nome_esperado] = arquivo
                    if nome_esperado == "N13P":
                        match = re.search(r'P(\d{2})', arquivo.name.upper())
                        if match:
                            periodo = match.group(1)
                            ano_atual = str(datetime.now().year)
                            ciclo_final = {"periodo": periodo, "ano": ano_atual}
                    break
    
    # st.subheader("Status de Carregamento")

    # --- SEÇÃO 1: O CARD "HERO" (100% LARGURA) ---
    # st.write("**Arquivo Principal de Ciclo**")
    nome_hero, desc_hero = list(ARQUIVO_HERO.items())[0]
    _desenhar_card_compacto(desc_hero, arquivos_encontrados.get(nome_hero))
    
    # st.markdown("---")

    # --- SEÇÃO 2: AS 3 BASES (3 COLUNAS) ---
    # st.write("**Arquivos de Base**")
    colunas_bases = st.columns(3)
    for i, (nome_base, desc_base) in enumerate(ARQUIVOS_BASES.items()):
        with colunas_bases[i]:
            _desenhar_card_compacto(desc_base, arquivos_encontrados.get(nome_base))

    # st.markdown("---")

    # --- SEÇÃO 3: AS 7 ZPs (GRID 4x4 COM CENTRALIZAÇÃO) ---
    # st.write("**Arquivos de Desconto (ZPs)**")
    lista_zps = list(ARQUIVOS_ZPS.items())
    
    # Primeira linha de 4 ZPs
    colunas_zps1 = st.columns(4)
    for i in range(4):
        nome_zp, desc_zp = lista_zps[i]
        with colunas_zps1[i]:
            _desenhar_card_compacto(desc_zp, arquivos_encontrados.get(nome_zp))

    # Segunda linha com 3 ZPs restantes, centralizadas
    col_vazia1, col_zp1, col_zp2, col_zp3, col_vazia2 = st.columns([0.5, 1, 1, 1, 0.5])
    with col_zp1:
        nome_zp, desc_zp = lista_zps[4]
        _desenhar_card_compacto(desc_zp, arquivos_encontrados.get(nome_zp))
    with col_zp2:
        nome_zp, desc_zp = lista_zps[5]
        _desenhar_card_compacto(desc_zp, arquivos_encontrados.get(nome_zp))
    with col_zp3:
        nome_zp, desc_zp = lista_zps[6]
        _desenhar_card_compacto(desc_zp, arquivos_encontrados.get(nome_zp))


    # Status Final e Feedback
    # st.markdown("<br>", unsafe_allow_html=True)
    pronto_para_processar = len(arquivos_encontrados) == len(ARQUIVOS_ESPERADOS) and ciclo_final is not None
    # if arquivos_carregados or pronto_para_processar:
    #     if ciclo_final:
    #         st.success(f"Ciclo de processamento definido: **Período {ciclo_final['periodo']} / Ano {ciclo_final['ano']}**")
    #     elif "N13P" in arquivos_encontrados:
    #         st.error("Arquivo N13P carregado, mas não foi possível detectar o período (ex: P08) no nome.")


    return pronto_para_processar, arquivos_encontrados, ciclo_final

