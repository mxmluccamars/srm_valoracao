# components/header.py

import streamlit as st
import base64

def render_header():
    """
    Desenha o header no topo da página.
    Este componente agora é "rolável" e não mais fixo.
    Os estilos globais são gerenciados por config_styles.py.
    """
    # 1. Lógica para embutir a imagem do logo
    try:
        with open("assets/header_logo_t.png", "rb") as f:
            logo_data = base64.b64encode(f.read()).decode("utf-8")
        logo_html = f'<img src="data:image/png;base64,{logo_data}" style="height: 55px; width: auto;">'
    except FileNotFoundError:
        logo_html = '<span style="font-size: 32px;">🚀</span>'

    # 2. Construção do CSS e HTML APENAS do header
    st.markdown(
        f"""
        <style>
            /* --- ESTILO DO HEADER E SEUS FILHOS --- */
            .header-container {{
                position: fixed; top: 0; left: 0;
                width: 100%; height: 85px;
                background-color: #0900A7;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 10px 2rem;
                z-index: 999;
                box-sizing: border-box;
            }}
            
            .header-logo {{ 
                flex: 1; 
            }}

            .header-title {{
                flex: 2;
                text-align: center;
                font-weight: 800 !important; /* EXTRABOLD */
                font-size: 32px;
                color: F8F7F2  !important;
            }}
            
            .header-version {{
                flex: 1;
                display: flex;
                justify-content: flex-end;
                align-items: flex-end;
            }}

            .header-version span {{
                font-weight: 500 !important; /* MEDIUM */
                font-size: 12px;
                color: rgba(255, 255, 255, 0.7) !important;
                margin-bottom: 5px;
            }}
        </style>

        <div class="header-container">
            <div class="header-logo">{logo_html}</div>
            <div class="header-title">SRM Valoração</div>
            <div class="header-version"><span>v1.0.0</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )

