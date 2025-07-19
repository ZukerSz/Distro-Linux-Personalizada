import customtkinter as ctk
from tkinter import ttk, messagebox
import json
import os
import statistics
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageOps

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

BG_DARK = "#082044"
BG_LIGHT = "#313842"
TEXT_COLOR = "#F0F0F0"
MODERN_BLUE = "#013F9A"
MODERN_BLUE_ACTIVE = "#01337D"
ALT_ROW_COLOR = "#707A88"
DANGER_COLOR = "#c0392b"
DANGER_HOVER_COLOR = "#E74C3C"
WARNING_COLOR = "#ffc107"
SUCCESS_COLOR = "#28a745"
SUCCESS_HOVER_COLOR = "#218838"

APP_DATA_DIR = os.path.join(os.path.expanduser('~'), '.local', 'share', 'notesyst')
os.makedirs(APP_DATA_DIR, exist_ok=True)
DB_FILE = os.path.join(APP_DATA_DIR, 'alunos.json')

def carregar_dados():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content:
                return {}
            dados = json.loads(content)
            if not isinstance(dados, dict):
                print(f"AVISO: O arquivo de dados '{DB_FILE}' foi corrompido (não continha um dicionário). Resetando.")
                return {}
            return dados
    except (json.JSONDecodeError, IOError) as e:
        print(f"ERRO: Não foi possível ler o arquivo '{DB_FILE}'. Erro: {e}. Um novo dicionário vazio será usado.")
        return {}

def salvar_dados():
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados_alunos, f, indent=4, ensure_ascii=False)

dados_alunos = carregar_dados()

def calcular_media_e_status(nome_aluno):
    aluno = dados_alunos.get(nome_aluno)
    if not aluno: return
    
    nota_b1 = aluno.get('nota_bimestre_1')
    nota_b2 = aluno.get('nota_bimestre_2')
    
    if nota_b1 is not None and nota_b2 is not None:
        media_final = round(statistics.mean([nota_b1, nota_b2]), 2)
        aluno['media_final'] = media_final
        aluno['status'] = "Aprovado" if media_final >= 7.0 else "Recuperação"
    else:
        aluno['media_final'] = None
        aluno['status'] = "Pendente"

def obter_medias_gerais_turma():
    medias = {'b1': [], 'b2': [], 'final': []}
    for aluno in dados_alunos.values():
        if aluno.get('nota_bimestre_1') is not None: medias['b1'].append(aluno['nota_bimestre_1'])
        if aluno.get('nota_bimestre_2') is not None: medias['b2'].append(aluno['nota_bimestre_2'])
        if aluno.get('media_final') is not None: medias['final'].append(aluno['media_final'])
    return {
        'Média 1ºB': round(statistics.mean(medias['b1']), 2) if medias['b1'] else 0,
        'Média 2ºB': round(statistics.mean(medias['b2']), 2) if medias['b2'] else 0,
        'Média Final': round(statistics.mean(medias['final']), 2) if medias['final'] else 0,
    }

def criar_imagem_quadrada(caminho_imagem, tamanho_tuple):
    try:
        img = Image.open(caminho_imagem)
        img_quadrada = ImageOps.fit(img, tamanho_tuple, centering=(0.5, 0.5))
        return img_quadrada
    except FileNotFoundError:
        img_padrao = Image.new('RGB', tamanho_tuple, (80, 80, 80))
        return img_padrao
    except Exception as e:
        print(f"AVISO: Não foi possível carregar a imagem. Erro: {e}")
        return None

def centralizar_janela(janela, width, height):
    screen_width = janela.winfo_screenwidth()
    screen_height = janela.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    janela.geometry(f'{width}x{height}+{x}+{y}')

class SplashScreen(ctk.CTk):
    def __init__(self, callback_after_splash, duration=2000, loading_text="Carregando..."):
        super().__init__()
        self.callback = callback_after_splash
        self.title("Carregando...")
        self.overrideredirect(True)
        centralizar_janela(self, 400, 300)
        self.configure(fg_color=BG_DARK)
        
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="both")
        loading_label = ctk.CTkLabel(container, text=loading_text, font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"), text_color=TEXT_COLOR)
        loading_label.pack(expand=True)
        self.after(duration, self.run_callback)

    def run_callback(self):
        self.destroy()
        if self.callback:
            self.callback()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NotesSyst - Sistema de Notas")
        self.resizable(False, False)
        centralizar_janela(self, 480, 450)
        self.configure(fg_color=BG_DARK)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(pady=20, padx=20, fill="both", expand=True)
        content_frame = ctk.CTkFrame(container, fg_color="transparent")
        content_frame.pack(expand=True)

        ctk.CTkLabel(content_frame, text="Bem-vindo(a) NotesSyst!", font=ctk.CTkFont(size=24, weight="bold"), text_color=TEXT_COLOR).pack(pady=(0, 10))
        ctk.CTkLabel(content_frame, text="Selecione seu perfil:", font=ctk.CTkFont(size=12), text_color=TEXT_COLOR).pack(pady=(0, 20))

        btn_professor = ctk.CTkButton(content_frame, text="👨‍🏫 Professor", command=lambda: self.abrir_tela(TelaProfessor), height=40, font=ctk.CTkFont(size=14), corner_radius=20, fg_color=MODERN_BLUE, hover_color=MODERN_BLUE_ACTIVE)
        btn_professor.pack(pady=5, fill="x")

        btn_aluno = ctk.CTkButton(content_frame, text="🧑‍🎓 Aluno", command=lambda: self.abrir_tela(TelaAluno), height=40, font=ctk.CTkFont(size=14), corner_radius=20, fg_color=MODERN_BLUE, hover_color=MODERN_BLUE_ACTIVE)
        btn_aluno.pack(pady=5, fill="x")

        btn_sair = ctk.CTkButton(content_frame, text="Sair do Programa", command=self.close_application, height=40, font=ctk.CTkFont(size=14), corner_radius=20, fg_color=DANGER_COLOR, hover_color=DANGER_HOVER_COLOR)
        btn_sair.pack(pady=(20, 5), fill="x")

    def abrir_tela(self, ClasseDaTela):
        def launch_target_screen():
            global dados_alunos
            dados_alunos = carregar_dados()
            tela = ClasseDaTela()
            tela.mainloop()
        self.destroy()
        splash = SplashScreen(callback_after_splash=launch_target_screen, duration=1500)
        splash.mainloop()

    def close_application(self):
        self.withdraw()
        splash_exit = SplashScreen(callback_after_splash=self.destroy, duration=2000, loading_text="Fechando...")
        splash_exit.mainloop()

class TelaProfessor(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Área do Professor")
        self.minsize(900, 600)
        centralizar_janela(self, 1100, 700)
        self.configure(fg_color=BG_DARK)
        self._configurar_estilos_tabela()
        self._criar_widgets()
        self.atualizar_tabela_e_combobox()

    def _configurar_estilos_tabela(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("Treeview.Heading", background=MODERN_BLUE, foreground="white", font=('Helvetica', 11, 'bold'), borderwidth=0, relief="flat")
        style.map("Treeview.Heading", relief=[('active', 'groove'), ('!active', 'flat')])
        style.configure("Treeview", background=BG_LIGHT, fieldbackground=BG_LIGHT, foreground=TEXT_COLOR, rowheight=30, borderwidth=0)
        style.map("Treeview", background=[('selected', MODERN_BLUE_ACTIVE)])

    def _criar_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        controles_frame = ctk.CTkFrame(main_frame, width=280, fg_color="transparent")
        controles_frame.grid(row=0, column=0, padx=(0, 20), sticky="ns")
        controles_frame.grid_rowconfigure(0, weight=1)
        content_wrapper = ctk.CTkScrollableFrame(controles_frame, fg_color="transparent", label_text="")
        content_wrapper.grid(row=0, column=0, sticky="nsew")

        frame_add_aluno = ctk.CTkFrame(content_wrapper, fg_color=BG_LIGHT)
        frame_add_aluno.pack(fill="x", pady=(0, 15), padx=(0, 10))
        ctk.CTkLabel(frame_add_aluno, text="1. Adicionar Aluno", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5,0))
        self.entry_novo_aluno = ctk.CTkEntry(frame_add_aluno, placeholder_text="Nome do Aluno")
        self.entry_novo_aluno.pack(pady=10, padx=10, fill="x")
        ctk.CTkButton(frame_add_aluno, text="Adicionar Aluno", command=self.adicionar_aluno, fg_color=MODERN_BLUE, hover_color=MODERN_BLUE_ACTIVE).pack(pady=(0,10), padx=10, fill="x")

        frame_lancar_nota = ctk.CTkFrame(content_wrapper, fg_color=BG_LIGHT)
        frame_lancar_nota.pack(fill="x", pady=15, padx=(0, 10))
        ctk.CTkLabel(frame_lancar_nota, text="2. Lançar/Substituir Nota", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5,0))
        self.combo_alunos = ctk.CTkComboBox(frame_lancar_nota, state="readonly")
        self.combo_alunos.pack(pady=10, padx=10, fill="x")
        self.combo_bimestre = ctk.CTkComboBox(frame_lancar_nota, state="readonly", values=["1º Bimestre", "2º Bimestre"])
        self.combo_bimestre.pack(pady=10, padx=10, fill="x")
        self.entry_nota = ctk.CTkEntry(frame_lancar_nota, placeholder_text="Nota (0 a 10)")
        self.entry_nota.pack(pady=10, padx=10, fill="x")
        ctk.CTkButton(frame_lancar_nota, text="Lançar Nota", command=self.lancar_nota, fg_color=MODERN_BLUE, hover_color=MODERN_BLUE_ACTIVE).pack(pady=(0,10), padx=10, fill="x")

        frame_gerenciar = ctk.CTkFrame(content_wrapper, fg_color=BG_LIGHT)
        frame_gerenciar.pack(fill="x", pady=15, padx=(0, 10))
        ctk.CTkLabel(frame_gerenciar, text="3. Gerenciar Aluno", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5,5))
        ctk.CTkButton(frame_gerenciar, text="Remover Aluno Selecionado", command=self.remover_aluno_selecionado, fg_color=DANGER_COLOR, hover_color=DANGER_HOVER_COLOR).pack(pady=10, padx=10, fill="x")

        frame_acoes_massa = ctk.CTkFrame(content_wrapper, fg_color=BG_LIGHT)
        frame_acoes_massa.pack(fill="x", pady=15, padx=(0, 10))
        ctk.CTkLabel(frame_acoes_massa, text="4. Ações em Massa", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5,5))
        ctk.CTkButton(frame_acoes_massa, text="Resetar Notas da Turma", command=self.resetar_notas_turma, fg_color=WARNING_COLOR, text_color="black", hover_color="#e0a800").pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(frame_acoes_massa, text="Excluir Turma Inteira", command=self.excluir_turma_inteira, fg_color=DANGER_COLOR, hover_color=DANGER_HOVER_COLOR).pack(pady=5, padx=10, fill="x")
        
        ctk.CTkButton(controles_frame, text="⬅️ Voltar ao Menu", command=self.voltar, fg_color="#555555", hover_color="#666666").grid(row=1, column=0, sticky="sew", pady=(10,0))
        
        tabela_frame = ctk.CTkFrame(main_frame, fg_color=BG_LIGHT)
        tabela_frame.grid(row=0, column=1, sticky="nsew")
        tabela_frame.grid_rowconfigure(0, weight=1)
        tabela_frame.grid_columnconfigure(0, weight=1)

        cols = ("Nome", "Nota 1ºB", "Nota 2ºB", "Média Final", "Status")
        self.tree = ttk.Treeview(tabela_frame, columns=cols, show='headings')
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.column("Nome", width=250, anchor="w")
        self.tree.column("Nota 1ºB", width=100, anchor="center")
        self.tree.column("Nota 2ºB", width=100, anchor="center")
        self.tree.column("Média Final", width=100, anchor="center")
        self.tree.column("Status", width=120, anchor="center")
        self.tree.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.tree.tag_configure('oddrow', background=BG_LIGHT)
        self.tree.tag_configure('evenrow', background=ALT_ROW_COLOR)

    def adicionar_aluno(self):
        nome = self.entry_novo_aluno.get().strip().title()
        if not nome:
            messagebox.showerror("Erro", "O nome do aluno não pode ser vazio.")
            return
        if nome in dados_alunos:
            messagebox.showwarning("Atenção", f"O aluno '{nome}' já está cadastrado.")
            return
        dados_alunos[nome] = {'nota_bimestre_1': None, 'nota_bimestre_2': None, 'media_final': None, 'status': 'Pendente'}
        salvar_dados()
        self.entry_novo_aluno.delete(0, ctk.END)
        self.atualizar_tabela_e_combobox()
        messagebox.showinfo("Sucesso", f"Aluno '{nome}' adicionado!")

    def lancar_nota(self):
        aluno = self.combo_alunos.get()
        bimestre_str = self.combo_bimestre.get()
        nota_str = self.entry_nota.get().strip().replace(',', '.')
        if not all([aluno, bimestre_str, nota_str]) or aluno == 'Nenhum aluno cadastrado':
            messagebox.showerror("Erro", "Preencha todos os campos: Aluno, Bimestre e Nota.")
            return
        try:
            nota = float(nota_str)
            if not (0 <= nota <= 10):
                raise ValueError("Nota fora do intervalo válido.")
        except ValueError:
            messagebox.showerror("Erro de Validação", "A nota deve ser um número entre 0 e 10.")
            return
        
        chave_bimestre = 'nota_bimestre_1' if '1º' in bimestre_str else 'nota_bimestre_2'
        nota_antiga = dados_alunos[aluno].get(chave_bimestre)
        
        if nota_antiga is not None:
            confirmar = messagebox.askyesno("Confirmar Substituição", f"Este bimestre já possui a nota {nota_antiga:.1f}.\nDeseja substituí-la pela nota {nota:.1f}?")
            if not confirmar:
                self.entry_nota.delete(0, ctk.END)
                return
                
        dados_alunos[aluno][chave_bimestre] = nota
        calcular_media_e_status(aluno)
        salvar_dados()
        self.entry_nota.delete(0, ctk.END)
        self.atualizar_tabela_e_combobox()
        messagebox.showinfo("Sucesso", f"Nota de '{aluno}' foi atualizada.")

    def remover_aluno_selecionado(self):
        item_selecionado = self.tree.focus()
        if not item_selecionado:
            messagebox.showerror("Erro", "Selecione um aluno na tabela para remover.")
            return
        aluno_selecionado = self.tree.item(item_selecionado)['values'][0]
        
        if messagebox.askyesno("Confirmar Remoção", f"Tem certeza que deseja remover permanentemente o aluno '{aluno_selecionado}'?"):
            del dados_alunos[aluno_selecionado]
            salvar_dados()
            self.atualizar_tabela_e_combobox()
            messagebox.showinfo("Sucesso", f"Aluno '{aluno_selecionado}' foi removido.")

    def resetar_notas_turma(self):
        if not dados_alunos:
            messagebox.showinfo("Informação", "Não há alunos cadastrados para resetar as notas.")
            return
        if messagebox.askyesno("Confirmar Reset", "Tem certeza que deseja LIMPAR TODAS AS NOTAS da turma?\nOs alunos não serão removidos."):
            for nome in dados_alunos:
                dados_alunos[nome] = {'nota_bimestre_1': None, 'nota_bimestre_2': None, 'media_final': None, 'status': 'Pendente'}
            salvar_dados()
            self.atualizar_tabela_e_combobox()
            messagebox.showinfo("Sucesso", "Todas as notas da turma foram resetadas.")

    def excluir_turma_inteira(self):
        if not dados_alunos:
            messagebox.showinfo("Informação", "A lista de alunos já está vazia.")
            return
        if messagebox.askyesno("CONFIRMAR EXCLUSÃO TOTAL", "⚠️ ATENÇÃO! ⚠️\n\nTem certeza que deseja EXCLUIR PERMANENTEMENTE TODOS os alunos e suas notas?\n\nEsta ação não pode ser desfeita."):
            dados_alunos.clear()
            salvar_dados()
            self.atualizar_tabela_e_combobox()
            messagebox.showinfo("Sucesso", "Todos os alunos foram removidos.")

    def atualizar_tabela_e_combobox(self):
        self.tree.delete(*self.tree.get_children())
        alunos_ordenados = sorted(dados_alunos.items())
        
        for i, (nome, dados) in enumerate(alunos_ordenados):
            n1, n2, mf = dados.get('nota_bimestre_1'), dados.get('nota_bimestre_2'), dados.get('media_final')
            status = dados.get('status', 'Pendente')
            
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            n1_display = f"{n1:.1f}" if n1 is not None else "N/A"
            n2_display = f"{n2:.1f}" if n2 is not None else "N/A"
            mf_display = f"{mf:.2f}" if mf is not None else "N/A"
            self.tree.insert("", "end", values=(nome, n1_display, n2_display, mf_display, status), tags=(tag,))
            
        alunos_lista = sorted(list(dados_alunos.keys()))
        if alunos_lista:
            self.combo_alunos.configure(values=alunos_lista)
            self.combo_alunos.set('')
        else:
            self.combo_alunos.configure(values=[])
            self.combo_alunos.set('Nenhum aluno cadastrado')
    
    def voltar(self):
        self.destroy()
        def start_main_app():
            app = App()
            app.mainloop()
        splash_retorno = SplashScreen(callback_after_splash=start_main_app, duration=1000, loading_text="Voltando ao menu...")
        splash_retorno.mainloop()

class TelaAluno(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Área do Aluno")
        self.minsize(800, 550)
        centralizar_janela(self, 950, 600)
        self.configure(fg_color=BG_DARK)
        self.canvas = None
        self._criar_widgets()

    def _criar_widgets(self):
        frame_selecao = ctk.CTkFrame(self, fg_color="transparent")
        frame_selecao.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(frame_selecao, text="Selecione seu nome:", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
        
        alunos_lista = sorted(list(dados_alunos.keys())) if dados_alunos else ["Nenhum aluno cadastrado"]
        self.combo_nomes = ctk.CTkComboBox(frame_selecao, state="readonly", values=alunos_lista, font=ctk.CTkFont(size=12), width=300, command=self.exibir_dados_aluno)
        self.combo_nomes.pack(side="left", padx=5)
        self.combo_nomes.set("Selecione um aluno" if "Nenhum aluno cadastrado" not in alunos_lista else "Nenhum aluno cadastrado")
        
        ctk.CTkButton(frame_selecao, text="⬅️ Voltar ao Menu", command=self.voltar, width=150, fg_color="#555555", hover_color="#666666").pack(side="right")

        self.frame_dados = ctk.CTkFrame(self, fg_color=BG_LIGHT)
        self.frame_dados.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.lbl_info = ctk.CTkLabel(self.frame_dados, text="Selecione seu nome para ver seu desempenho.", font=ctk.CTkFont(size=14), text_color="#AAAAAA")
        self.lbl_info.pack(pady=20, padx=10)
        
        self.lbl_media = ctk.CTkLabel(self.frame_dados, text="", font=ctk.CTkFont(size=16))
        self.lbl_status = ctk.CTkLabel(self.frame_dados, text="", font=ctk.CTkFont(size=16, weight="bold"))
        self.grafico_container = ctk.CTkFrame(self.frame_dados, fg_color="transparent")

    def exibir_dados_aluno(self, nome_selecionado):
        if not nome_selecionado or nome_selecionado == "Nenhum aluno cadastrado":
            return
        
        self.lbl_info.pack_forget()
        self.lbl_media.pack_forget()
        self.lbl_status.pack_forget()
        self.grafico_container.pack_forget()

        self.lbl_media.pack(pady=5, padx=10)
        self.lbl_status.pack(pady=(5, 20), padx=10)
        self.grafico_container.pack(fill="both", expand=True, padx=10, pady=10)

        aluno = dados_alunos.get(nome_selecionado, {})
        media_final = aluno.get('media_final')
        status = aluno.get('status', 'Pendente')

        self.lbl_media.configure(text=f"Sua Média Final: {media_final:.2f}" if media_final is not None else "Média Final: N/A")
        self.lbl_status.configure(text=f"Status: {status}")

        cor = {"Aprovado": SUCCESS_COLOR, "Recuperação": WARNING_COLOR, "Pendente": "gray"}
        self.lbl_status.configure(text_color=cor.get(status, "white"))
        
        self.atualizar_grafico(aluno)

    def atualizar_grafico(self, aluno):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            plt.close(self.canvas.figure)
        for widget in self.grafico_container.winfo_children():
            widget.destroy()

        if aluno.get('nota_bimestre_1') is None and aluno.get('nota_bimestre_2') is None:
            ctk.CTkLabel(self.grafico_container, text="Nenhuma nota lançada para exibir no gráfico.", font=ctk.CTkFont(size=12)).pack(pady=20)
            return
            
        medias_gerais = obter_medias_gerais_turma()
        labels = ['Nota 1ºB', 'Nota 2ºB', 'Média Final']
        notas_aluno = [aluno.get('nota_bimestre_1') or 0, aluno.get('nota_bimestre_2') or 0, aluno.get('media_final') or 0]
        notas_turma = [medias_gerais.get('Média 1ºB', 0), medias_gerais.get('Média 2ºB', 0), medias_gerais.get('Média Final', 0)]
        
        fig, ax = plt.subplots(figsize=(7, 4))
        fig.patch.set_facecolor(BG_LIGHT)
        ax.set_facecolor(BG_LIGHT)
        ax.set_ylabel('Notas', color=TEXT_COLOR)
        ax.set_title('Suas Notas vs. Média da Turma', color=TEXT_COLOR, fontweight='bold')
        ax.tick_params(axis='x', colors=TEXT_COLOR)
        ax.tick_params(axis='y', colors=TEXT_COLOR)
        
        for spine in ax.spines.values():
            spine.set_edgecolor(TEXT_COLOR)
            
        bar_width = 0.35
        index = range(len(labels))
        
        rects1 = ax.bar([i - bar_width/2 for i in index], notas_aluno, bar_width, label='Sua Nota', color=MODERN_BLUE)
        rects2 = ax.bar([i + bar_width/2 for i in index], notas_turma, bar_width, label='Média da Turma', color=ALT_ROW_COLOR)
        
        ax.set_xticks(index)
        ax.set_xticklabels(labels)
        legend = ax.legend()
        plt.setp(legend.get_texts(), color=TEXT_COLOR)
        legend.get_frame().set_facecolor(BG_DARK)
        ax.set_ylim(0, 11)
        
        ax.bar_label(rects1, padding=3, fmt='%.1f', color=TEXT_COLOR)
        ax.bar_label(rects2, padding=3, fmt='%.1f', color=TEXT_COLOR)
        
        fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(fig, master=self.grafico_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def voltar(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            plt.close(self.canvas.figure)
            self.canvas = None
        self.destroy()

        def start_main_app():
            app = App()
            app.mainloop()
        splash_retorno = SplashScreen(callback_after_splash=start_main_app, duration=1000, loading_text="Voltando ao menu...")
        splash_retorno.mainloop()

if __name__ == "__main__":
    try:
        root_check = ctk.CTk()
        root_check.destroy()
    except Exception as e:
        print("="*60)
        print("ERRO CRÍTICO DE AMBIENTE: Não foi possível iniciar a interface.")
        print("Isso geralmente acontece em Linux se o 'tkinter' não estiver instalado.")
        print("Por favor, rode o seguinte comando no seu terminal:")
        print("sudo apt-get install python3-tk")
        print(f"Detalhes do erro: {e}")
        print("="*60)
        exit()

    app = App()
    app.mainloop()