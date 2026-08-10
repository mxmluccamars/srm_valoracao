# components/config_styles.py

import streamlit as st

def apply_global_styles():
    """
    Esta função injeta o CSS global do aplicativo, definindo:
    - Configurações da página (ícone, layout)
    - Importação e aplicação da fonte Montserrat
    - Cor de fundo branca
    - Remoção da UI padrão do Streamlit
    """
    # 1. Configurações da página (deve ser a primeira chamada do Streamlit)
    st.set_page_config(
        page_title="SPIM - Pricing Tool",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # 2. Injeção do CSS global
    st.markdown(
        """
        <style>
            /* --- 1. IMPORTAÇÃO DA FONTE MONTSERRAT --- */
            /* Pesos: 400 (Regular), 500 (Medium), 800 (Extrabold) */
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;800&display=swap');

            /* --- 2. ESTILOS GLOBAIS DA PÁGINA --- */
            
            /* Define a cor de fundo universal como branca */
            [data-testid="stAppViewContainer"] {
                # background-color: #F8F7F2  ;
                backgroun-color: #39107B ;
                color: #F8F7F2 ; /* Cor do texto padrão */
            }

            /* Aplica a fonte Montserrat em TUDO e força a cor do texto padrão */
            html, body, [class*="st-"], [class*="css-"] {
                font-family: 'Montserrat', sans-serif !important;
                color: #F8F7F2 ; 
            }

            /* --- 3. REMOÇÃO DA UI PADRÃO DO STREAMLIT --- */
            div[data-testid="stToolbar"],
            div[data-testid="stDecoration"],
            div[data-testid="stStatusWidget"],
            #MainMenu,
            header,
            footer {
                visibility: hidden;
                height: 0%;
                position: fixed;
            }

            [data-testid="block-container"] {
                padding: 0rem;
                margin: 0rem;
            }

           /* --- 4. ESTILO DOS BOTÕES DE AÇÃO --- */

            /* Estilo para o botão primário (type="primary") */
            /* O seletor correto é "stBaseButton-primary" */
            button[data-testid="stBaseButton-primary"] {
                background-color: #0900A7; /* Sua cor azul principal */
                color: white;
                border: none;
                height: 3rem;
                font-weight: 600;
                transition: all 0.2s ease-in-out; /* Adiciona uma transição suave */
            }
            button[data-testid="stBaseButton-primary"]:hover {
                background-color: #FFDB00;
                color: #0900A7;
                border: 1px solid #0900A7;
                transform: scale(1.02); /* Efeito de crescimento sutil no hover */
            }

            /* Estilo para o botão quando ele está desabilitado */
            button[data-testid="stBaseButton-primary"]:disabled {
                background-color: #F8F7F2; /* Um cinza para indicar inatividade */
                color: #0900A7;
                border: none;
                transform: none; /* Garante que não haja efeito no botão desabilitado */
            }
        </style>
        """,
        unsafe_allow_html=True
    )
