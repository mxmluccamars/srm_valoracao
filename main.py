import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QFontDatabase
from src.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # --- CARREGANDO A FONTE PERSONALIZADA ---
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(base_dir, "src", "assets", "MarsCentra-Book.ttf") # ◀️ AJUSTE O NOME DO SEU ARQUIVO AQUI
    
    font_family = "Segoe UI"  # Fonte padrão
    
    if os.path.exists(font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            loaded_families = QFontDatabase.applicationFontFamilies(font_id)
            if loaded_families:
                font_family = loaded_families[0]
                # print(f"Fonte personalizada '{font_family}' carregada com sucesso!")
        else:
            print("Erro ao carregar a fonte personalizada.")
    else:
        print(f"Aviso: Arquivo de fonte não encontrado em {font_path}. Usando fonte padrão.")
    
    # --- MUDANÇA PRINCIPAL ---
    # Agora passamos o nome da fonte diretamente para a janela
    window = MainWindow(font_family=font_family)
    # -------------------------
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
