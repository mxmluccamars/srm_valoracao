# components/header.py

import streamlit as st
import base64

def render_header():
    """
    Desenha o header final com a versão posicionada de forma sutil.
    """
    # 1. Configurações da página
    st.set_page_config(
        page_title="SPIM - Pricing Tool",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # 2. Lógica para embutir a imagem
    try:
        with open("assets/header_logo.png", "rb") as f:
            logo_data = base64.b64encode(f.read()).decode("utf-8")
        logo_html = f'<img src="data:image/png;base64,{logo_data}" style="height: 55px; width: auto;">'
    except FileNotFoundError:
        logo_html = '<span style="font-size: 32px;">🚀</span>'

    # 3. Construção do Header com o CSS final
    st.markdown(
        f"""
        <style>
            /* --- REMOÇÃO DA UI DO STREAMLIT --- */
            div[data-testid="stToolbar"],
            div[data-testid="stDecoration"],
            div[data-testid="stStatusWidget"],
            #MainMenu,
            header,
            footer {{
                visibility: hidden; height: 0%; position: fixed;
            }}
            .main .block-container {{ padding-top: 0rem; }}
            .stApp {{ padding-top: 90px; }}
            
            /* --- ESTILO DO HEADER --- */
            .header-container {{
                position: fixed; top: 0; left: 0;
                width: 100%; height: 85px;
                background-color: #FF1414;
                display: flex; align-items: center; justify-content: space-between;
                padding: 10px 2rem;
                z-index: 999;
                box-sizing: border-box;
            }}
            
            /* --- ELEMENTOS DO HEADER --- */
            .header-logo {{ flex: 1; }}
            .header-title {{
                flex: 2; text-align: center;
                font-family: sans-serif; font-size: 32px; font-weight: 700; color: white;
            }}
            
            /* AJUSTES NA VERSÃO */
            .header-version {{
                flex: 1;
                display: flex;
                justify-content: flex-end;  /* Alinha o conteúdo à direita */
                align-items: flex-end;      /* Alinha o conteúdo na parte de baixo */
            }}
            .header-version span {{
                font-family: sans-serif;
                font-size: 12px;         /* Fonte menor */
                font-weight: 500;
                color: rgba(255, 255, 255, 0.7); /* Branco com 70% de opacidade (mais escuro) */
                margin-bottom: 5px;      /* Leve espaço abaixo do texto */
            }}
            .header-container * {{ color: white; }}
        </style>

        <div class="header-container">
            <div class="header-logo">{logo_html}</div>
            <div class="header-title">SRM Valoração</div>
            <div class="header-version"><span>v1.0.0</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )
