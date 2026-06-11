# frontend.py

import customtkinter as ctk
import os
import threading
import backend  # Importa o nosso "Cérebro"

# ==========================================
# 1. CONFIGURAÇÕES VISUAIS PADRÃO
# ==========================================
ctk.set_appearance_mode("dark")  # Opções: "dark", "light", "system"
ctk.set_default_color_theme("blue")  # Temas: "blue", "green", "dark-blue"

class AppValoracao(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da Janela
        self.title("Motor de Valoração - SRM")
        self.geometry("800x600")
        self.resizable(False, False) # Trava o tamanho para o layout não quebrar

        # ==========================================
        # 2. DESENHO DA TELA (Layout)
        # ==========================================
        # Título Superior
        self.label_titulo = ctk.CTkLabel(self, text="MOTOR DE VALORAÇÃO", font=("Arial", 20, "bold"))
        self.label_titulo.pack(pady=(20, 5))

        self.label_sub = ctk.CTkLabel(self, text="* Coloque o executável na mesma pasta das planilhas.", text_color="gray")
        self.label_sub.pack(pady=(0, 20))

        # Frame (Caixa) para os Inputs de Ano e Período
        self.frame_inputs = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inputs.pack(pady=10)

        # Campo Ano
        self.label_ano = ctk.CTkLabel(self.frame_inputs, text="Ano (Ex: 2024):")
        self.label_ano.grid(row=0, column=0, padx=10, pady=10)
        self.entrada_ano = ctk.CTkEntry(self.frame_inputs, width=100)
        self.entrada_ano.grid(row=0, column=1, padx=10, pady=10)

        # Campo Período
        self.label_periodo = ctk.CTkLabel(self.frame_inputs, text="Período (Ex: 03):")
        self.label_periodo.grid(row=0, column=2, padx=10, pady=10)
        self.entrada_periodo = ctk.CTkEntry(self.frame_inputs, width=100)
        self.entrada_periodo.grid(row=0, column=3, padx=10, pady=10)

        # Botão Verificar
        self.btn_verificar = ctk.CTkButton(self, text="🔍 Verificar Arquivos", command=self.acao_verificar, fg_color="#D97706", hover_color="#B45309")
        self.btn_verificar.pack(pady=(10, 5))

        # Botão Iniciar (Nasce bloqueado/cinza)
        self.btn_iniciar = ctk.CTkButton(self, text="🚀 Iniciar Valoração", command=self.acao_iniciar, state="disabled")
        self.btn_iniciar.pack(pady=(5, 20))

        # Caixinha preta de Log (Console)
        self.caixa_log = ctk.CTkTextbox(self, width=750, height=300, state="disabled", fg_color="#1E1E1E", text_color="#00FF00")
        self.caixa_log.pack(pady=10)
        
        self.escrever_log("Sistema pronto. Digite o Ano, o Período e clique em Verificar.")

    # ==========================================
    # 3. FUNÇÕES DE COMUNICAÇÃO (Callbacks)
    # ==========================================
    def escrever_log(self, mensagem):
        """Escreve uma nova linha na caixinha preta e rola para baixo."""
        self.caixa_log.configure(state="normal") # Destrava para escrever
        self.caixa_log.insert(ctk.END, mensagem + "\n")
        self.caixa_log.see(ctk.END) # Rola a barra até o final
        self.caixa_log.configure(state="disabled") # Trava de novo (pro usuário não apagar)

    def acao_verificar(self):
        """O que acontece quando clica em Verificar"""
        
        # --- NOVO BLOCO: Limpa o console antes de cada nova verificação ---
        self.caixa_log.configure(state="normal")
        self.caixa_log.delete("0.0", "end")
        self.caixa_log.configure(state="disabled")
        # -----------------------------------------------------------------

        ano = self.entrada_ano.get().strip()
        periodo = self.entrada_periodo.get().strip()

        if not ano or not periodo:
            self.escrever_log("⚠️ ERRO: Preencha o Ano e o Período antes de verificar!")
            return

        # Pega a pasta onde o programa está rodando agora
        diretorio_atual = os.getcwd()
        
        self.escrever_log(f"🔍 Iniciando nova verificação (Ciclo {periodo}/{ano})...")
        self.escrever_log("-" * 50) 
        
        # Chama a função do Backend
        tudo_ok = backend.auditar_arquivos(ano, periodo, diretorio_atual, self.escrever_log)

        # Destrava ou trava o botão Iniciar
        if tudo_ok:
            self.btn_iniciar.configure(state="normal", fg_color="#16A34A", hover_color="#15803D")
        else:
            self.btn_iniciar.configure(state="disabled", fg_color="#374151")

    def acao_iniciar(self):
        """O que acontece quando clica em Iniciar"""
        self.escrever_log("-" * 50)
        self.escrever_log("🚀 Dando a partida no Motor...")
        
        # Trava os botões para o usuário não clicar duas vezes e abrir dois motores juntos
        self.btn_iniciar.configure(state="disabled") 
        self.btn_verificar.configure(state="disabled") 

        # Pega os dados que já foram validados
        ano = self.entrada_ano.get().strip()
        periodo = self.entrada_periodo.get().strip()
        diretorio_atual = os.getcwd()

        # Cria a Thread (A segunda pista) para rodar o motor sem travar a tela
        thread = threading.Thread(target=self.rodar_motor_em_background, args=(ano, periodo, diretorio_atual))
        thread.start() # Dá o play na thread

    def rodar_motor_em_background(self, ano, periodo, diretorio):
        """Função intermediária que roda invisível e chama o Backend"""
        try:
            # Chama a função principal do seu backend
            sucesso = backend.executar_motor(ano, periodo, diretorio, self.escrever_log)
            
            if sucesso:
                self.escrever_log("🎉 Processo finalizado com sucesso!")
            else:
                self.escrever_log("⚠️ O processo parou devido a um erro. Verifique o log.")
                
        except Exception as e:
            self.escrever_log(f"❌ ERRO FATAL: {str(e)}")
            
        finally:
            # No final de tudo (dando certo ou errado), destrava o botão de Verificar de novo
            self.btn_verificar.configure(state="normal")

# ==========================================
# 4. GATILHO DE EXECUÇÃO
# ==========================================
if __name__ == "__main__":
    app = AppValoracao()
    app.mainloop()