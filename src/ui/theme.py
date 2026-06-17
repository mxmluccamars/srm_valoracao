"""
Configuração de Identidade Visual e Cores do SRM Valoração.

Centraliza todas as cores do sistema para fácil manutenção e criação de temas.
"""

THEME = {
    # Cores Gerais da Janela
    "window_background": "#000000",     # Cinza bem claro
    "text_primary": "#ffbe0c",          # Azul escuro corporativo para textos
    "input_background": "#cacaca",      # Branco para campos de texto
    "border_color": "#818181",          # Cinza para bordas suaves
    "primary_focus": "#797979",         # Azul brilhante para foco/seleção

    # Botão Padrão (Verificar Arquivos)
    "btn_default_bg": "#ffbe0c",        # Azul escuro
    "btn_default_hover": "#df500d",     # Azul cinzento ao passar o mouse
    "btn_default_pressed": "#1a252f",   # Azul bem escuro ao clicar

    # Botão de Ação Principal (Processar)
    "btn_success_bg": "#ffbe0c",        # Verde
    "btn_success_hover": "#df500d",     # Verde claro ao passar o mouse
    "btn_success_pressed": "#1a252f",   # Verde escuro ao clicar

    # Botão Desabilitado
    "btn_disabled_bg": "#bdc3c7",       # Cinza claro desabilitado
    "btn_disabled_text": "#7f8c8d",     # Texto cinza escuro desabilitado

    # Barra de Progresso
    "progress_bg": "#e9ecef",           # Fundo da barra cinza claro
    "progress_chunk": "#2ecc71",        # Enchimento da barra em verde vibrante

    # Caixa de Logs (Terminal)
    "log_background": "#1e272e",        # Preto/Grafite escuro estilo terminal
    "log_text": "#dcdde1",              # Texto cinza claro de alta leitura
    "log_border": "#2f3542",            # Borda discreta para o terminal
}
