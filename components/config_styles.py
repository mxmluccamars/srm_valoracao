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
                background-color: #F8F7F2 ;
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
        </style>
        """,
        unsafe_allow_html=True
    )
