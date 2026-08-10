# components/config_styles.py

import streamlit as st

def apply_global_styles():
    """
    Esta função injeta todo o CSS global do aplicativo, incluindo:
    - Configurações da página (ícone, layout)
    - Importação de fontes (Montserrat)
    - Cor de fundo universal
    - Reset de paddings e remoção da UI do Streamlit
    - Aplicação da fonte global
    """
    # 1. Configurações da página (deve ser a primeira chamada do Streamlit no script)
    st.set_page_config(
        page_title="SPIM - Pricing Tool",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # 2. Injeção de todo o CSS global
    st.markdown(
        """
        <style>
            /* --- 1. IMPORTAÇÃO DA FONTE MONTSERRAT --- */
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;800&display=swap');

            /* --- 2. ESTILOS GLOBAIS DA PÁGINA --- */
            /* Cor de fundo universal do app */
            [data-testid="stAppViewContainer"] {
                background-color: #F8F7F2; /* Seu fundo claro */
            }

            /* Aplica a fonte Montserrat em TUDO */
            html, body, [class*="st-"], [class*="css-"] {
                font-family: 'Montserrat', sans-serif !important;
            }

            /* --- 3. REMOÇÃO DA UI E PADDINGS LATERAIS --- */
            div[data-testid="stToolbar"], div[data-testid="stDecoration"],
            div[data-testid="stStatusWidget"], #MainMenu, header, footer {
                visibility: hidden; height: 0%; position: fixed;
            }
            
            /* Remove as margens laterais do contêiner principal */
            [data-testid="block-container"] {
                padding-left: 0rem;
                padding-right: 0rem;
                padding-top: 0rem;
                padding-bottom: 0rem;
                margin: 0px;
            }
            
            /* Mantém o espaço para o header fixo */
            .stApp { 
                padding-top: 85px; 
            }
        </style>
        """,
        unsafe_allow_html=True
    )
