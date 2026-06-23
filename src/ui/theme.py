"""
Configuração de Identidade Visual e Cores do SRM Valoração.

Centraliza todas as cores do sistema para fácil manutenção e criação de temas.
"""

THEME = {
    # Cores Gerais da Janela
    "window_background": "#000000",     # Cinza bem claro
    "text_primary": "#df500d",          # Azul escuro corporativo para textos
    "input_background": "#cacaca",      # Branco para campos de texto
    "border_color": "#818181",          # Cinza para bordas suaves
    "primary_focus": "#797979",         # Azul brilhante para foco/seleção

    # Botão Padrão (Verificar Arquivos)
    "btn_default_bg": "#df500d",        # Azul escuro
    "btn_default_hover": "#df4f0d7d",     # Azul cinzento ao passar o mouse
    "btn_default_pressed": "#df4f0d37",   # Azul bem escuro ao clicar

    # Botão de Ação Principal (Processar)
    "btn_success_bg": "#df500d",        # Verde
    "btn_success_hover": "#df4f0d7d",     # Verde claro ao passar o mouse
    "btn_success_pressed": "#df4f0d37",   # Verde escuro ao clicar

    # Botão Desabilitado
    "btn_disabled_bg": "#bdc3c7",       # Cinza claro desabilitado
    "btn_disabled_text": "#7f8c8d",     # Texto cinza escuro desabilitado

    # Barra de Progresso
    "progress_bg": "#df500d",           # Fundo da barra cinza claro
    "progress_chunk": "#ffffff",        # Enchimento da barra em verde vibrante
    "progress_text": "#000000",         # Texto da barra em branco para contraste

    # Caixa de Logs (Terminal)
    "log_background": "#1e272e",        # Preto/Grafite escuro estilo terminal
    "log_text": "#dcdde1",              # Texto cinza claro de alta leitura
    "log_border": "#2f3542",            # Borda discreta para o terminal
    
    # Estado: Pendente (Cinza)
    "card_pending_bg": "#f1f2f6",
    "card_pending_text": "#7f8c8d",
    "card_pending_border": "#ced4da",

    # Estado: Encontrado / OK (Verde)
    "card_success_bg": "#d4edda",
    "card_success_text": "#155724",
    "card_success_border": "#c3e6cb",

    # Estado: Ausente / Erro (Vermelho)
    "card_error_bg": "#f8d7da",
    "card_error_text": "#721c24",
    "card_error_border": "#f5c6cb",
}
