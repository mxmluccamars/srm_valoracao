import os
import sys
from PySide6.QtCore import Qt, QSize, QThread, Signal, QObject
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QProgressBar, 
    QTextEdit, QFrame, QGridLayout
)
from PySide6.QtGui import QFont, QIcon

# Importações do nosso Core (Lógica) e UI (Tema)
from src.core.file_handler import FileHandler
from src.core.data_processor import DataProcessor
from src.ui.theme import THEME


class ProcessingWorker(QObject):
    """
    Worker intermediário que executa o processamento de dados em segundo plano.
    
    Isso impede que a interface gráfica (UI) trave durante cálculos pesados.
    """
    # Sinais que o Worker usará para se comunicar com a interface principal
    progress_changed = Signal(int)
    log_emitted = Signal(str)
    finished = Signal(bool)

    def __init__(self, processor: DataProcessor, file_paths: list, ano: int, periodo: int):
        super().__init__()
        self.processor = processor
        self.file_paths = file_paths
        self.ano = ano
        self.periodo = periodo

    def run(self):
        """Método que roda dentro da Thread secundária."""
        # Esta função serve de ponte: ela recebe o progresso do DataProcessor
        # e o emite através dos sinais do Qt para a Janela Principal.
        def callback(porcentagem: int, mensagem: str):
            self.progress_changed.emit(porcentagem)
            self.log_emitted.emit(f"➔ {mensagem}")

        # Executa o processamento real (ou simulado)
        sucesso = self.processor.process(self.file_paths, self.ano, self.periodo, callback)
        self.finished.emit(sucesso)


class MainWindow(QMainWindow):
    """
    Janela Principal do sistema SRM Valoração.
    """

    def __init__(self, font_family: str = "Segoe UI"):
        super().__init__()

        self.font_family = font_family
        self.file_handler = FileHandler()
        
        # Cria a instância do processador definindo a pasta atual para salvar o resultado
        self.data_processor = DataProcessor(output_dir=os.getcwd())
        
        self.verified_files = None
        self.thread = None  # Guardará a referência da nossa Thread
        self.worker = None  # Guardará a referência do nosso Worker

        # Configurações de Identidade
        self.nome_do_sistema = "SRM Valoração"
        self.setWindowTitle(self.nome_do_sistema)
        self._set_window_icon()

        # Dimensões
        self.setMinimumSize(QSize(700, 650))
        self.resize(750, 700)

        # Widget Central
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(25, 25, 25, 25)

        # Inicializa Componentes
        self._create_header()
        self._create_inputs()
        self._create_buttons()
        self._create_file_status_grid()
        self._create_progress_bar()
        self._create_log_area()
        self._apply_styles()

        # Conecta eventos dos botões
        self.btn_verificar.clicked.connect(self._run_file_verification)
        self.btn_processar.clicked.connect(self._run_data_processing) # ◀️ Conecta o botão processar!

        self.write_log("▶ SRM Valoração iniciado. Insira Ano/Período e clique em 'Verificar Arquivos'.")

    def _set_window_icon(self):
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, "assets", "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def _create_header(self):
        self.title_label = QLabel(self.nome_do_sistema, self)
        font = QFont(self.font_family, 18, QFont.Bold)
        self.title_label.setFont(font)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.title_label)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #dcdde1;")
        self.main_layout.addWidget(line)

    def _create_inputs(self):
        input_layout = QHBoxLayout()
        input_layout.setSpacing(25)

        # Campo Ano
        ano_layout = QVBoxLayout()
        self.lbl_ano = QLabel("Ano de Referência:", self)
        self.lbl_ano.setFont(QFont(self.font_family, 9, QFont.Bold))
        self.txt_ano = QLineEdit(self)
        self.txt_ano.setPlaceholderText("Ex: 2026")
        self.txt_ano.setMaxLength(4)
        ano_layout.addWidget(self.lbl_ano)
        ano_layout.addWidget(self.txt_ano)

        # Campo Período
        periodo_layout = QVBoxLayout()
        self.lbl_periodo = QLabel("Período (Ciclo):", self)
        self.lbl_periodo.setFont(QFont(self.font_family, 9, QFont.Bold))
        self.txt_periodo = QLineEdit(self)
        self.txt_periodo.setPlaceholderText("Ex: 1 a 13")
        self.txt_periodo.setMaxLength(2)
        periodo_layout.addWidget(self.lbl_periodo)
        periodo_layout.addWidget(self.txt_periodo)

        input_layout.addLayout(ano_layout)
        input_layout.addLayout(periodo_layout)
        self.main_layout.addLayout(input_layout)

    def _create_buttons(self):
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

    def _create_file_status_grid(self):
        self.grid_widget = QWidget(self)
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setContentsMargins(0, 5, 0, 5)

        self.files_to_track = {
            "BASE CLIENTES": "BASE CLIENTES",
            "BASE PRODUTOS": "BASE PRODUTOS",
            "ZP39": "ZP39",
            "ZP52": "ZP52",
            "ZP53": "ZP53",
            "ZP54": "ZP54",
            "ZP55": "ZP55",
            "ZP70": "ZP70",
            "ZP73": "ZP73",
            "CICLO": "Ciclo_P{periodo:02d} N13P {ano} - envio"
        }

        self.file_cards = {}
        columns = 2
        for i, (key, display_name) in enumerate(self.files_to_track.items()):
            row = i // columns
            col = i % columns

            card = QLabel(f"⚪  {display_name}", self)
            card.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            card.setMinimumHeight(35)
            card.setContentsMargins(15, 0, 15, 0)
            
            card.setStyleSheet(f"""
                border: 1px solid {THEME["card_pending_border"]};
                border-radius: 6px;
                background-color: {THEME["card_pending_bg"]};
                color: {THEME["card_pending_text"]};
                font-size: 9pt;
                font-weight: bold;
            """)

            self.grid_layout.addWidget(card, row, col)
            self.file_cards[key] = card

        self.main_layout.addWidget(self.grid_widget)
 
    def _create_progress_bar(self):
        progress_layout = QVBoxLayout()
        self.lbl_progresso = QLabel("Status do Processamento:", self)
        self.lbl_progresso.setFont(QFont(self.font_family, 9, QFont.Bold))
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(22)
        self.progress_bar.setAlignment(Qt.AlignCenter)

        progress_layout.addWidget(self.lbl_progresso)
        progress_layout.addWidget(self.progress_bar)
        self.main_layout.addLayout(progress_layout)

    def _create_log_area(self):
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
        self.log_text.append(message)
        self.log_text.ensureCursorVisible()

    def _update_card_style(self, key: str, state: str, filename: str = None):
        card = self.file_cards[key]
        display_name = filename if filename else self.files_to_track[key]

        if state == "success":
            card.setText(f"✓  {display_name}")
            card.setStyleSheet(f"""
                border: 1px solid {THEME["card_success_border"]};
                border-radius: 6px;
                background-color: {THEME["card_success_bg"]};
                color: {THEME["card_success_text"]};
                font-size: 9pt;
                font-weight: bold;
            """)
        elif state == "error":
            card.setText(f"✗  {display_name}")
            card.setStyleSheet(f"""
                border: 1px solid {THEME["card_error_border"]};
                border-radius: 6px;
                background-color: {THEME["card_error_bg"]};
                color: {THEME["card_error_text"]};
                font-size: 9pt;s
                font-weight: bold;
            """)
        else:
            card.setText(f"⚪  {display_name}")
            card.setStyleSheet(f"""
                border: 1px solid {THEME["card_pending_border"]};
                border-radius: 6px;
                background-color: {THEME["card_pending_bg"]};
                color: {THEME["card_pending_text"]};
                font-size: 9pt;
                font-weight: bold;
            """)

    def _run_file_verification(self):
        self.log_text.clear()
        self.progress_bar.setValue(0)
        self.btn_processar.setEnabled(False)
        self.verified_files = None

        for key in self.files_to_track.keys():
            self._update_card_style(key, "pending")

        ano_str = self.txt_ano.text().strip()
        periodo_str = self.txt_periodo.text().strip()

        if not ano_str or not periodo_str:
            self.write_log("⚠️ Erro: Os campos 'Ano de Referência' e 'Período' são obrigatórios.")
            return

        if not ano_str.isdigit() or not periodo_str.isdigit():
            self.write_log("⚠️ Erro: Insira apenas números inteiros nos campos de entrada.")
            return

        ano = int(ano_str)
        periodo = int(periodo_str)
        current_dir = os.getcwd()

        ciclo_filename = f"Ciclo_P{periodo:02d} N13P {ano} - envio"
        self._update_card_style("CICLO", "pending", ciclo_filename)

        self.write_log(f"🔎 Analisando diretório para o Ciclo P{periodo:02d} / {ano}...")
        self.write_log(f"📁 Pasta de busca: {current_dir}\n")

        success, result = self.file_handler.verify_files(current_dir, ano, periodo)

        if success:
            for key in self.file_cards.keys():
                if key == "CICLO":
                    self._update_card_style(key, "success", ciclo_filename)
                else:
                    self._update_card_style(key, "success")
            
            self.write_log("✅ Sucesso! Todas as planilhas necessárias foram encontradas.")
            self.write_log("👉 Clique em 'Processar Dados' para iniciar os cálculos.")
            self.verified_files = result
            self.btn_processar.setEnabled(True)
        else:
            missing_basenames = result
            for key in self.file_cards.keys():
                actual_name = ciclo_filename if key == "CICLO" else self.files_to_track[key]
                if actual_name in missing_basenames:
                    self._update_card_style(key, "error", actual_name)
                else:
                    self._update_card_style(key, "success", actual_name)

            self.write_log("❌ Falha! Alguns arquivos obrigatórios estão ausentes (marcados com ✗).")

    # --- INÍCIO DA MUDANÇA (LÓGICA DE PROCESSAMENTO EM SEGUNDO PLANO) ---
    def _run_data_processing(self):
        """Inicia o processamento de dados usando uma Thread secundária."""
        # 1. Bloqueia os botões e inputs para o usuário não mexer durante o cálculo
        self._toggle_interface_enabled(False)
        self.progress_bar.setValue(0)
        self.write_log("\n⚙️ Iniciando esteira de processamento...")

        ano = int(self.txt_ano.text())
        periodo = int(self.txt_periodo.text())

        # 2. Cria a Thread e o Worker
        self.thread = QThread()
        self.worker = ProcessingWorker(
            processor=self.data_processor,
            file_paths=self.verified_files,
            ano=ano,
            periodo=periodo
        )
        
        # Move o Worker para a Thread de segundo plano
        self.worker.moveToThread(self.thread)

        # 3. Conecta os sinais do Worker à interface principal
        self.thread.started.connect(self.worker.run)
        self.worker.progress_changed.connect(self.progress_bar.setValue)
        self.worker.log_emitted.connect(self.write_log)
        
        # Conecta a finalização
        self.worker.finished.connect(self._on_processing_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # 4. Inicia a execução da Thread
        self.thread.start()

    def _on_processing_finished(self, sucesso: bool):
        """Chamado quando o Worker conclui o processamento."""
        # Desbloqueia os botões e inputs da interface
        self._toggle_interface_enabled(True)

        if sucesso:
            self.write_log("\n🎉 Processo finalizado com sucesso absoluto!")
            self.write_log("📂 Sinta-se à vontade para realizar um novo processamento.")
        else:
            self.write_log("\n⚠️ Ocorreu um erro durante o processamento. Verifique as planilhas.")

    def _toggle_interface_enabled(self, enabled: bool):
        """Desativa ou ativa os controles de interface durante processamentos longos."""
        self.btn_verificar.setEnabled(enabled)
        self.btn_processar.setEnabled(enabled)
        self.txt_ano.setEnabled(enabled)
        self.txt_periodo.setEnabled(enabled)
    # --- FIM DA MUDANÇA ---

    def _apply_styles(self):
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
                color: {THEME["progress_text"]};
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
