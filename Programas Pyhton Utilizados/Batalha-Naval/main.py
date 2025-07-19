import customtkinter as ctk
from tkinter import messagebox
import os
import sys
from PIL import Image

try:
    import pygame
    from game import Jogo
except ImportError as e:
    print(f"Erro ao importar dependências do jogo: {e}")
    print("Certifique-se de que 'pygame' está instalado ('pip install pygame') e que 'game.py' está acessível.")
    root_fallback = ctk.CTk()
    root_fallback.withdraw()
    messagebox.showerror("Erro de Dependência", f"Não foi possível carregar o Pygame ou o arquivo 'game.py'.\n\nErro: {e}\n\nO programa será encerrado.")
    sys.exit()

BG_DARK = "#082044"
BG_LIGHT = "#313842"
TEXT_COLOR = "#F0F0F0"
MODERN_BLUE = "#013F9A"
MODERN_BLUE_ACTIVE = "#01337D"
DANGER_COLOR = "#c0392b"
DANGER_HOVER_COLOR = "#E74C3C"

class SplashScreen(ctk.CTk):
    def __init__(self, callback_after_splash, duration=2500, loading_text="Carregando..."):
        super().__init__()
        self.callback = callback_after_splash
        self.title("Carregando...")
        window_width, window_height = 450, 350
        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()
        center_x, center_y = int(screen_width/2 - window_width / 2), int(screen_height/2 - window_height / 2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.overrideredirect(True)
        self.configure(fg_color=BG_DARK)
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both")
        loading_label = ctk.CTkLabel(main_frame, text=loading_text, font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"), text_color=TEXT_COLOR)
        loading_label.pack(expand=True)
        self.after(duration, self.run_callback)

    def run_callback(self):
        self.destroy()
        if self.callback:
            self.callback()


class MenuPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Batalha Naval")
        window_width, window_height = 500, 480
        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()
        center_x, center_y = int(screen_width/2 - window_width / 2), int(screen_height/2 - window_height / 2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.resizable(False, False)
        self.configure(fg_color=BG_DARK)
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(pady=40, padx=40, fill="both", expand=True)
        ctk.CTkLabel(container, text="Batalha Naval", font=ctk.CTkFont(size=32, weight="bold"), text_color=TEXT_COLOR).pack(pady=(20, 10))
        ctk.CTkLabel(container, text="Prepare-se para o combate!", font=ctk.CTkFont(size=12), text_color=TEXT_COLOR).pack(pady=(0, 40))
        btn_jogar = ctk.CTkButton(container, text="⚓ Jogar", command=self.iniciar_jogo, height=50, font=ctk.CTkFont(size=16, weight="bold"), corner_radius=25, fg_color=MODERN_BLUE, hover_color=MODERN_BLUE_ACTIVE)
        btn_jogar.pack(pady=10, fill="x")
        btn_como_jogar = ctk.CTkButton(container, text="📜  Como Jogar", command=self.mostrar_instrucoes, height=50, font=ctk.CTkFont(size=16, weight="bold"), corner_radius=25, fg_color=MODERN_BLUE, hover_color=MODERN_BLUE_ACTIVE)
        btn_como_jogar.pack(pady=10, fill="x")
        btn_sair = ctk.CTkButton(container, text="Sair do Programa", command=self.destroy, height=50, font=ctk.CTkFont(size=16, weight="bold"), corner_radius=25, fg_color=DANGER_COLOR, hover_color=DANGER_HOVER_COLOR)
        btn_sair.pack(pady=(40, 10), fill="x")

   
    def iniciar_jogo(self):
        self.withdraw() 

        def _gerenciar_ciclo_de_jogo():
            """
            Função que executa um ciclo completo do jogo (inicia, joga, termina).
            Essa abordagem com callbacks é mais estável do que o loop 'while True'.
            """
            pygame.init()
            jogo_batalha_naval = Jogo()
            acao_final = jogo_batalha_naval.executar() # O jogo roda e retorna a ação do jogador
            pygame.quit() # Encerra o Pygame após cada partida

            if acao_final == "reiniciar":
                # Se o jogador quer reiniciar, mostra a splash e define a próxima chamada
                # para esta mesma função (_gerenciar_ciclo_de_jogo).
                splash_reinicio = SplashScreen(
                    callback_after_splash=_gerenciar_ciclo_de_jogo, 
                    duration=1500, 
                    loading_text="Reiniciando Partida..."
                )
                splash_reinicio.mainloop()
            
            elif acao_final == "sair":
                # Se o jogador quer sair, mostra a splash de encerramento e fecha o programa.
                splash_final = SplashScreen(
                    callback_after_splash=sys.exit, 
                    duration=1500, 
                    loading_text="Fechando..."
                )
                splash_final.mainloop()
            
            else: # Se o jogador fechou a janela do Pygame (acao_final é None ou outra coisa)
                # Encerra o processo completamente para não deixar a janela do menu "pendurada".
                sys.exit()

        # Mostra a splash inicial antes de chamar o gerenciador do jogo pela primeira vez.
        splash_para_jogo = SplashScreen(
            callback_after_splash=_gerenciar_ciclo_de_jogo,
            duration=2000,
            loading_text="Iniciando combate..."
        )
        splash_para_jogo.mainloop()


    def mostrar_instrucoes(self):
        instrucoes_window = ctk.CTkToplevel(self)
        instrucoes_window.title("Como Jogar")
        instrucoes_window.geometry("700x500")
        instrucoes_window.resizable(False, False)
        instrucoes_window.configure(fg_color=BG_DARK)
        instrucoes_text_box = ctk.CTkTextbox(instrucoes_window, width=660, height=460, 
                                             font=("Consolas", 14), text_color=TEXT_COLOR,
                                             fg_color=BG_LIGHT, wrap="word",
                                             border_color=MODERN_BLUE, border_width=2)
        instrucoes_text_box.pack(pady=20, padx=20)
        texto_instrucoes = """
OBJETIVO: Afundar todos os navios do seu oponente (IA) antes que ele afunde os seus.

---------------------------------
FASE 1: POSICIONAMENTO DOS NAVIOS
---------------------------------
- Use as teclas numéricas (1 a 6) para selecionar um tipo de navio.
- Pressione a tecla 'R' para girar o navio entre horizontal e vertical.
- Clique com o mouse no SEU tabuleiro (o da esquerda) para posicionar o navio selecionado.
- Você deve posicionar todos os 6 navios para o combate começar.

--------------------------
FASE 2: BATALHA EM TURNOS
--------------------------
- O jogo funciona em turnos. Você sempre começa.
- Na sua vez, clique em uma célula do tabuleiro do seu OPONENTE (o da direita) para lançar um ataque.

  - TIRO NA ÁGUA (marcador vermelho): Você errou. A vez passa para a IA.
  
  - TIRO CERTEIRO (marcador verde): Você acertou uma parte de um navio! A vez passa para a IA.
  
  - NAVIO AFUNDADO (fica laranja): Quando todas as partes de um navio são atingidas, ele afunda.

--------------------
FIM DE JOGO
--------------------
- Você vence se afundar todos os navios da IA.
- Você perde se a IA afundar todos os seus navios.

Boa sorte, comandante!
"""
        instrucoes_text_box.insert("0.0", texto_instrucoes)
        instrucoes_text_box.configure(state="disabled")
        instrucoes_window.transient(self)
        instrucoes_window.grab_set()
        self.wait_window(instrucoes_window)

# --- PONTO DE ENTRADA (sem alterações) ---
if __name__ == "__main__":
    menu = MenuPrincipal()
    menu.mainloop()