# components/actions.py

import streamlit as st

def render_action_buttons():
    """
    Renderiza os botões de ação principais da página, como "Processar" e "Download".
    O comportamento dos botões é controlado pelo estado da aplicação.
    """

    # O botão só será clicável se o estado for 'READY_TO_PROCESS'
    # Em todos os outros estados, ele aparecerá cinza e desabilitado.
    processar_clicado = st.button(
        "Iniciar Valoração",
        key="btn_processar",
        type="primary", # Dá um estilo de destaque padrão do Streamlit
        use_container_width=True,
        disabled=(st.session_state.app_state != 'READY_TO_PROCESS')
    )

    # Futuramente, o botão de download também virá aqui.

    return processar_clicado
