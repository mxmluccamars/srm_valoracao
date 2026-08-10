# components/downloader.py

import streamlit as st
import pandas as pd

def render_download_section(df_resultado, excel_data, ciclo):
    """
    Renderiza a seção final com a pré-visualização dos dados e o botão de download.
    """
    st.success("🎉 Relatório finalizado e pronto para download!")
    st.balloons()

    st.markdown("### 📊 Amostra dos Dados Processados")
    st.dataframe(df_resultado.head(100), use_container_width=True, height=350)
    
    st.markdown("---")

    nome_arquivo = f"Resultado SPIM - P{ciclo['periodo']}_{ciclo['ano']}.xlsx"
    
    st.download_button(
        label="📥 Baixar Relatório em Excel",
        data=excel_data,
        file_name=nome_arquivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        use_container_width=True,
        key="btn_download"
    )
