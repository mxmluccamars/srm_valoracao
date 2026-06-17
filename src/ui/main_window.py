import os
import sys
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QProgressBar, 
    QTextEdit, QFrame
)
from PySide6.QtGui import QFont, QIcon

# Importação da nossa classe de lógica de arquivos
from src.core.file_handler import FileHandler

from src.ui.theme import THEME

# Ativa o ícone correto na barra de tarefas do Windows
if sys.platform == "win32":
    import ctypes
    myappid = "mars.srm.valoracao.1.0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class MainWindow(QMainWindow):
    """
    Janela Principal do sistema SRM Valoração.
    
    Responsável pela interface visual, captura de dados do usuário,
    validação de arquivos locais e disparo do processamento.
    """

    def __init__(self, font_family: str = "Segoe UI"):
        super().__init__()

        # Instancia as classes de controle
        self.file_handler = FileHandler()
        self.verified_files = None

        # Configurações de Identidade do App
        self.nome_do_sistema = "SRM Valoração"
        self.setWindowTitle(self.nome_do_sistema)
        self._set_window_icon()
        self.font_family = font_family

        # Dimensões da janela
        self.setMinimumSize(QSize(650, 550))
        self.resize(700, 600)

        # Widget Central e Layout Principal
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(25, 25, 25, 25)

        # Inicializa todos os componentes visuais
        self._create_header()
        self._create_inputs()
        self._create_buttons()
        self._create_progress_bar()
        self._create_log_area()
        self._apply_styles()

        # Conecta os eventos dos botões
        self.btn_verificar.clicked.connect(self._run_file_verification)

        # Mensagem de boas-vindas no Log
        self.write_log("▶ Sistema SRM Valoração iniciado com sucesso.")
        self.write_log("➔ Insira o Ano e o Período nos campos acima e clique em 'Verificar Arquivos'.")

    def _set_window_icon(self):
        """Define o ícone da janela se ele existir na pasta assets."""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, "assets", "logo.png")

        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            # Não trava o sistema se o ícone não for encontrado
            print(f"Aviso: Ícone não encontrado em {icon_path}. Prosseguindo sem ícone personalizado.")

    def _create_header(self):
        """Desenha o cabeçalho superior."""
        self.title_label = QLabel(self.nome_do_sistema, self)
        font = QFont(self.font_family, 18, QFont.Bold)
        self.title_label.setFont(font)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.title_label)

        # Linha divisória fina estilosa
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #dcdde1;")
        self.main_layout.addWidget(line)

    def _create_inputs(self):
        """Cria os campos de texto para Ano e Período."""
        input_layout = QHBoxLayout()
        input_layout.setSpacing(25)

        # Campo Ano
        ano_layout = QVBoxLayout()
        self.lbl_ano = QLabel("Ano de Referência:", self)
        self.lbl_ano.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.txt_ano = QLineEdit(self)
        self.txt_ano.setPlaceholderText("Ex: 2026")
        self.txt_ano.setMaxLength(4)
        ano_layout.addWidget(self.lbl_ano)
        ano_layout.addWidget(self.txt_ano)

        # Campo Período
        periodo_layout = QVBoxLayout()
        self.lbl_periodo = QLabel("Período (Ciclo):", self)
        self.lbl_periodo.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.txt_periodo = QLineEdit(self)
        self.txt_periodo.setPlaceholderText("Ex: 1 a 13")
        self.txt_periodo.setMaxLength(2)
        periodo_layout.addWidget(self.lbl_periodo)
        periodo_layout.addWidget(self.txt_periodo)

        input_layout.addLayout(ano_layout)
        input_layout.addLayout(periodo_layout)
        self.main_layout.addLayout(input_layout)

    def _create_buttons(self):
        """Cria os botões de ação."""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        self.btn_verificar = QPushButton("🔍 Verificar Arquivos", self)
        self.btn_verificar.setCursor(Qt.PointingHandCursor)
        self.btn_verificar.setMinimumHeight(42)

        self.btn_processar = QPushButton("🚀 Processar Dados", self)
        self.btn_processar.setCursor(Qt.PointingHandCursor)
        self.btn_processar.setEnabled(False)
        self.btn_processar.setMinimumHeight(42)

        button_layout.addWidget(self.btn_verificar)
        button_layout.addWidget(self.btn_processar)
        self.main_layout.addLayout(button_layout)

    def _create_progress_bar(self):
        """Cria a barra de progresso."""
        progress_layout = QVBoxLayout()
        self.lbl_progresso = QLabel("Status do Processamento:", self)
        self.lbl_progresso.setFont(QFont("Segoe UI", 9, QFont.Bold))
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(22)
        self.progress_bar.setAlignment(Qt.AlignCenter)

        progress_layout.addWidget(self.lbl_progresso)
        progress_layout.addWidget(self.progress_bar)
        self.main_layout.addLayout(progress_layout)

    def _create_log_area(self):
        """Cria a área de texto onde mostramos os logs."""
        log_layout = QVBoxLayout()
        self.lbl_log = QLabel("Log de Atividades:", self)
        self.lbl_log.setFont(QFont(self.font_family, 9, QFont.Bold))

        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("Aguardando ações...")

        log_layout.addWidget(self.lbl_log)
        log_layout.addWidget(self.log_text)
        self.main_layout.addLayout(log_layout)

    def write_log(self, message: str):
        """Imprime uma linha formatada na caixa de logs."""
        self.log_text.append(message)
        self.log_text.ensureCursorVisible()

    def _run_file_verification(self):
        """Ação disparada ao clicar no botão 'Verificar Arquivos'."""
        self.log_text.clear()
        self.progress_bar.setValue(0)
        self.btn_processar.setEnabled(False)
        self.verified_files = None

        ano_str = self.txt_ano.text().strip()
        periodo_str = self.txt_periodo.text().strip()

        # Validação de campos vazios ou não numéricos
        if not ano_str or not periodo_str:
            self.write_log("⚠️ Erro: Os campos 'Ano de Referência' e 'Período' são obrigatórios.")
            return

        if not ano_str.isdigit() or not periodo_str.isdigit():
            self.write_log("⚠️ Erro: Insira apenas números inteiros nos campos de entrada.")
            return

        ano = int(ano_str)
        periodo = int(periodo_str)
        current_dir = os.getcwd()

        self.write_log(f"🔎 Analisando diretório para o Ciclo P{periodo} / {ano}...")
        self.write_log(f"📁 Pasta de busca: {current_dir}\n")

        # Chama a validação da classe de lógica
        success, result = self.file_handler.verify_files(current_dir, ano, periodo)

        if success:
            self.write_log("✅ Sucesso! Todas as planilhas necessárias foram encontradas.")
            self.write_log("👉 Clique em 'Processar Dados' para iniciar os cálculos.")
            self.verified_files = result
            self.btn_processar.setEnabled(True)
        else:
            self.write_log("❌ Falha! Alguns arquivos obrigatórios estão ausentes na pasta:")
            for missing in result:
                self.write_log(f"   • {missing}.xlsx (ou .xlsm)")

    def _apply_styles(self):
        """Aplica o design visual profissional utilizando o arquivo de tema centralizado."""
        style = f"""
            * {{
                font-family: "{self.font_family}";
            }}
            QMainWindow {{
                background-color: {THEME["window_background"]};
            }}
            QLabel {{
                color: {THEME["text_primary"]};
            }}
            QLineEdit {{
                border: 1px solid {THEME["border_color"]};
                border-radius: 6px;
                padding: 10px;
                background-color: {THEME["input_background"]};
                font-size: 10pt;
                color: #333333;
            }}
            QLineEdit:focus {{
                border: 1.5px solid {THEME["primary_focus"]};
            }}
            QPushButton {{
                font-size: 10pt;
                font-weight: bold;
                color: #ffffff;
                background-color: {THEME["btn_default_bg"]};
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {THEME["btn_default_hover"]};
            }}
            QPushButton:pressed {{
                background-color: {THEME["btn_default_pressed"]};
            }}
            QPushButton:disabled {{
                background-color: {THEME["btn_disabled_bg"]};
                color: {THEME["btn_disabled_text"]};
            }}
            QPushButton#btn_processar {{
                background-color: {THEME["btn_success_bg"]};
            }}
            QPushButton#btn_processar:hover {{
                background-color: {THEME["btn_success_hover"]};
            }}
            QPushButton#btn_processar:pressed {{
                background-color: {THEME["btn_success_pressed"]};
            }}
            QProgressBar {{
                border: 1px solid {THEME["border_color"]};
                border-radius: 6px;
                text-align: center;
                font-weight: bold;
                background-color: {THEME["progress_bg"]};
                color: {THEME["text_primary"]};
            }}
            QProgressBar::chunk {{
                background-color: {THEME["progress_chunk"]};
                border-radius: 5px;
            }}
            QTextEdit {{
                background-color: {THEME["log_background"]};
                color: {THEME["log_text"]};
                font-family: "Consolas", "Courier New", monospace;
                font-size: 10pt;
                border-radius: 6px;
                border: 1px solid {THEME["log_border"]};
                padding: 10px;
            }}
        """
        self.btn_processar.setObjectName("btn_processar")
        self.setStyleSheet(style)
