import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from tkcalendar import DateEntry
import json
import os

DIRETORIO_DADOS_APP = os.path.join(os.path.expanduser('~'), '.local', 'share', 'todolist')
os.makedirs(DIRETORIO_DADOS_APP, exist_ok=True)
ARQUIVO_DADOS = os.path.join(DIRETORIO_DADOS_APP, 'tasks.json')

# --- manipulação de Dados ---
def carregar_dados_do_json():
    if not os.path.exists(ARQUIVO_DADOS):
        return {}
    try:
        with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            if not conteudo:
                return {}
            dados = json.loads(conteudo)
            return dados if isinstance(dados, dict) else {}
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def salvar_dados_no_json(todos_dados_usuarios):
    with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
        json.dump(todos_dados_usuarios, f, indent=4, ensure_ascii=False)


class TelaSplash(ctk.CTkToplevel):
    def __init__(self, janela_pai, texto="Carregando...", duracao=2000, funcao_retorno=None):
        super().__init__(janela_pai)
        self.funcao_retorno = funcao_retorno

        largura_tela, altura_tela = self.winfo_screenwidth(), self.winfo_screenheight()
        largura_janela, altura_janela = 400, 200
        centro_x = int(largura_tela / 2 - largura_janela / 2)
        centro_y = int(altura_tela / 2 - altura_janela / 2)
        self.geometry(f'{largura_janela}x{altura_janela}+{centro_x}+{centro_y}')

        self.overrideredirect(True)
        self.configure(fg_color="#082044")
        
        rotulo = ctk.CTkLabel(self, text=texto, font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"))
        rotulo.pack(expand=True)

        self.after(duracao, self.fechar_splash)

    def fechar_splash(self):
        self.destroy()
        if self.funcao_retorno:
            self.funcao_retorno()

class TelaSelecaoUsuario(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Seleção de Usuário - ToDoList")
        self.configure(fg_color="#082044")

        largura_tela, altura_tela = self.winfo_screenwidth(), self.winfo_screenheight()
        largura_janela, altura_janela = 450, 520
        centro_x = int(largura_tela / 2 - largura_janela / 2)
        centro_y = int(altura_tela / 2 - altura_janela / 2)
        self.geometry(f'{largura_janela}x{altura_janela}+{centro_x}+{centro_y}')
        self.resizable(False, False)

        self.todos_dados_usuarios = carregar_dados_do_json()
        self.lista_usuarios = sorted(list(self.todos_dados_usuarios.keys()))

        frame_principal = ctk.CTkFrame(self, fg_color="transparent")
        frame_principal.pack(expand=True, fill="both", padx=30, pady=30)

        ctk.CTkLabel(frame_principal, text="ToDoList", font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold")).pack(pady=(0, 5))
        ctk.CTkLabel(frame_principal, text="Bem-vindo(a)!", font=ctk.CTkFont(family="Segoe UI", size=14)).pack(pady=(0, 20))

        ctk.CTkLabel(frame_principal, text="Selecione um usuário:", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).pack(anchor="w")
        self.combobox_usuarios = ctk.CTkComboBox(frame_principal, values=self.lista_usuarios)
        self.combobox_usuarios.pack(pady=5, fill="x")
        self.combobox_usuarios.set("")

        frame_botoes_login = ctk.CTkFrame(frame_principal, fg_color="transparent")
        frame_botoes_login.pack(fill="x", pady=(5, 20))
        frame_botoes_login.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(frame_botoes_login, text="Entrar", command=self.entrar, fg_color="#013F9A", hover_color="#01337D").grid(row=0, column=0, padx=(0, 5), sticky="ew", ipady=5)
        
        ctk.CTkButton(frame_botoes_login, text="Remover Usuário", command=self.remover_usuario_selecionado, fg_color="#c0392b", hover_color="#e74c3c").grid(row=0, column=1, padx=(5, 0), sticky="ew", ipady=5)
        
        ctk.CTkLabel(frame_principal, text="Ou crie um novo:", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).pack(anchor="w")
        self.entrada_novo_usuario = ctk.CTkEntry(frame_principal, placeholder_text="Nome do novo usuário")
        self.entrada_novo_usuario.pack(pady=5, fill="x")
        ctk.CTkButton(frame_principal, text="Adicionar e Entrar", command=self.adicionar_e_entrar, fg_color="#313842", hover_color="#707A88").pack(pady=5, fill="x", ipady=5)
        
        ctk.CTkButton(frame_principal, text="Fechar Programa", command=self.confirmar_e_fechar_programa, fg_color="#D32F2F", hover_color="#B71C1C").pack(pady=(30, 0), fill="x", ipady=5)
        
    def atualizar_lista_e_combobox_usuarios(self):
        self.todos_dados_usuarios = carregar_dados_do_json()
        self.lista_usuarios = sorted(list(self.todos_dados_usuarios.keys()))
        self.combobox_usuarios.configure(values=self.lista_usuarios)
        self.combobox_usuarios.set("")

    def entrar(self):
        nome_usuario = self.combobox_usuarios.get()
        if nome_usuario and nome_usuario in self.lista_usuarios:
            self.iniciar_app_para_usuario(nome_usuario)
        else:
            messagebox.showwarning("Aviso", "Por favor, selecione um usuário válido da lista.")
            self.combobox_usuarios.set("")

    def remover_usuario_selecionado(self):
        nome_usuario = self.combobox_usuarios.get()
        
        if not nome_usuario or nome_usuario not in self.lista_usuarios:
            messagebox.showwarning("Aviso", "Por favor, selecione um usuário da lista para remover.")
            self.combobox_usuarios.set("")
            return

        if messagebox.askyesno("Confirmar Exclusão", 
                                f"Tem certeza que deseja excluir permanentemente o usuário '{nome_usuario}' e todas as suas tarefas?\n\nEsta ação não pode ser desfeita.", 
                                icon='warning'):
            
            del self.todos_dados_usuarios[nome_usuario]
            salvar_dados_no_json(self.todos_dados_usuarios)
            self.atualizar_lista_e_combobox_usuarios()
            messagebox.showinfo("Sucesso", f"O usuário '{nome_usuario}' foi removido com sucesso.")

    def adicionar_e_entrar(self):
        nome_usuario = self.entrada_novo_usuario.get().strip()
        if not nome_usuario:
            messagebox.showwarning("Aviso", "O nome do usuário não pode ser vazio.")
            return
        if nome_usuario in self.todos_dados_usuarios:
            messagebox.showwarning("Aviso", f"O usuário '{nome_usuario}' já existe. Selecione-o na lista.")
            return
        
        self.todos_dados_usuarios[nome_usuario] = []
        salvar_dados_no_json(self.todos_dados_usuarios)
        self.entrada_novo_usuario.delete(0, 'end')
        self.atualizar_lista_e_combobox_usuarios()
        self.iniciar_app_para_usuario(nome_usuario)

    def iniciar_app_para_usuario(self, nome_usuario):
        self.withdraw()
        
        def abrir_app_principal():
            janela_app = AplicativoPrincipal(janela_pai=self, nome_usuario=nome_usuario)
            
        TelaSplash(self, texto=f"Carregando tarefas\nde {nome_usuario}...", duracao=1500, funcao_retorno=abrir_app_principal)

    def confirmar_e_fechar_programa(self):
        self.withdraw()
        TelaSplash(self, texto="Fechando...", duracao=1500, funcao_retorno=self.destroy)

class AplicativoPrincipal(ctk.CTkToplevel):
    def __init__(self, janela_pai, nome_usuario):
        super().__init__(janela_pai)
        self.janela_pai = janela_pai
        self.nome_usuario = nome_usuario

        self.protocol("WM_DELETE_WINDOW", self.sair_do_app)
        
        # --- Constantes de Cores ---
        self.COR_AZUL_MARINHO = "#082044"
        self.COR_AZUL_BRILHANTE = "#013F9A"
        self.COR_CARVAO = "#313842"
        self.COR_CINZA_ARdosia = "#707A88"
        self.COR_BRANCO = "#FFFFFF"

        self.todos_dados_usuarios = carregar_dados_do_json()
        self.dados_tarefas = self.todos_dados_usuarios.get(self.nome_usuario, [])
        
        self.construir_interface_principal()
        self.atualizar_treeview()

    def construir_interface_principal(self):
        self.title(f"ToDoList - Usuário: {self.nome_usuario}")
        self.geometry("800x600")
        self.minsize(720, 500)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.configure(fg_color=self.COR_AZUL_MARINHO)

        frame_entrada = ctk.CTkFrame(self, fg_color="transparent")
        frame_entrada.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        frame_entrada.grid_columnconfigure(0, weight=1)

        frame_tarefas = ctk.CTkFrame(self, fg_color="transparent")
        frame_tarefas.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        frame_tarefas.grid_columnconfigure(0, weight=1)
        frame_tarefas.grid_rowconfigure(0, weight=1)
        
        frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_botoes.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.entrada_tarefa = ctk.CTkEntry(frame_entrada, placeholder_text="Adicionar nova tarefa...", font=("Segoe UI", 12))
        self.entrada_tarefa.grid(row=0, column=0, padx=(10, 10), pady=10, sticky="ew")
        
        self.entrada_data_vencimento = DateEntry(frame_entrada, width=12, background=self.COR_AZUL_BRILHANTE, foreground=self.COR_BRANCO, borderwidth=2, date_pattern='dd/mm/yyyy')
        self.entrada_data_vencimento.grid(row=0, column=1, padx=(0, 10), pady=10)
        
        self.botao_adicionar = ctk.CTkButton(frame_entrada, text="Adicionar", command=self.adicionar_tarefa, fg_color=self.COR_AZUL_BRILHANTE, hover_color="#01337D", font=("Segoe UI", 12, "bold"))
        self.botao_adicionar.grid(row=0, column=2, padx=(0,10), pady=10)
        
        estilo = ttk.Style(self)
        estilo.theme_use("default")
        estilo.configure("Treeview", background=self.COR_CARVAO, foreground=self.COR_BRANCO, fieldbackground=self.COR_CARVAO, borderwidth=0, rowheight=35, font=('Segoe UI', 12))
        estilo.map('Treeview', background=[('selected', self.COR_AZUL_BRILHANTE)])
        estilo.configure("Treeview.Heading", background=self.COR_AZUL_MARINHO, foreground=self.COR_BRANCO, relief="flat", font=('Segoe UI', 12, 'bold'), padding=[10, 10])
        estilo.map("Treeview.Heading", background=[('active', self.COR_AZUL_BRILHANTE)])

        self.treeview_tarefas = ttk.Treeview(frame_tarefas, columns=("Tarefa", "Prazo", "Status"), show="headings")
        self.treeview_tarefas.heading("Tarefa", text="Tarefa")
        self.treeview_tarefas.heading("Prazo", text="Prazo")
        self.treeview_tarefas.heading("Status", text="Status")
        self.treeview_tarefas.column("Tarefa", width=380, stretch=tk.YES)
        self.treeview_tarefas.column("Prazo", width=120, anchor=tk.CENTER, stretch=tk.NO)
        self.treeview_tarefas.column("Status", width=120, anchor=tk.CENTER, stretch=tk.NO)
        self.treeview_tarefas.grid(row=0, column=0, sticky="nsew")

        fonte_riscada = ctk.CTkFont(family="Segoe UI", size=12, overstrike=True)
        self.treeview_tarefas.tag_configure('concluida', foreground=self.COR_CINZA_ARdosia, font=fonte_riscada)
        self.treeview_tarefas.tag_configure('pendente', foreground=self.COR_BRANCO)
        self.treeview_tarefas.tag_configure('linha_impar', background=self.COR_CARVAO)
        self.treeview_tarefas.tag_configure('linha_par', background="#2B3036")

        fonte_botao = ("Segoe UI", 12)
        cor_btn, cor_hover_btn = self.COR_CINZA_ARdosia, self.COR_CARVAO
        self.botao_concluir = ctk.CTkButton(frame_botoes, text="Concluir/Reativar", command=self.alternar_conclusao, fg_color=cor_btn, hover_color=cor_hover_btn, font=fonte_botao)
        self.botao_concluir.pack(side="left", padx=10, pady=10)
        self.botao_editar = ctk.CTkButton(frame_botoes, text="Editar Tarefa", command=self.janela_editar_tarefa, fg_color=cor_btn, hover_color=cor_hover_btn, font=fonte_botao)
        self.botao_editar.pack(side="left", padx=10, pady=10)
        self.botao_excluir = ctk.CTkButton(frame_botoes, text="Excluir Tarefa", command=self.excluir_tarefa, fg_color=cor_btn, hover_color=cor_hover_btn, font=fonte_botao)
        self.botao_excluir.pack(side="left", padx=10, pady=10)
        self.botao_excluir_todas = ctk.CTkButton(frame_botoes, text="Apagar Todas", command=self.excluir_todas_as_tarefas, fg_color="#D32F2F", hover_color="#B71C1C", font=fonte_botao)
        self.botao_excluir_todas.pack(side="left", padx=10, pady=10)
        self.botao_sair = ctk.CTkButton(frame_botoes, text="Trocar Usuário", command=self.sair_do_app, fg_color=self.COR_CARVAO, hover_color=self.COR_CINZA_ARdosia, font=fonte_botao)
        self.botao_sair.pack(side="right", padx=10, pady=10)

    def salvar_dados_usuario_atual(self):
        self.todos_dados_usuarios[self.nome_usuario] = self.dados_tarefas
        salvar_dados_no_json(self.todos_dados_usuarios)

    def atualizar_treeview(self):
        for item in self.treeview_tarefas.get_children():
            self.treeview_tarefas.delete(item)
        
        tarefas_ordenadas = sorted(self.dados_tarefas, key=lambda t: (t['completed'], t.get('due_date', '')))
        
        for i, tarefa in enumerate(tarefas_ordenadas):
            tag_linha = 'linha_par' if i % 2 == 0 else 'linha_impar'
            texto_status = "Concluída" if tarefa['completed'] else "Pendente"
            tag_status = 'concluida' if tarefa['completed'] else 'pendente'
            self.treeview_tarefas.insert("", tk.END, iid=tarefa['id'], values=(tarefa['task'], tarefa['due_date'], texto_status), tags=(tag_linha, tag_status))

    def obter_id_tarefa_selecionada(self):
        selecao = self.treeview_tarefas.selection()
        if selecao:
            return int(selecao[0])
        messagebox.showwarning("Aviso", "Por favor, selecione uma tarefa na lista.", parent=self)
        return None

    def adicionar_tarefa(self):
        texto_tarefa = self.entrada_tarefa.get()
        data_vencimento = self.entrada_data_vencimento.get()
        if not texto_tarefa:
            messagebox.showwarning("Aviso", "Por favor, insira o nome da tarefa.", parent=self)
            return
            
        novo_id = (max(t['id'] for t in self.dados_tarefas) + 1) if self.dados_tarefas else 1
        nova_tarefa = {"id": novo_id, "task": texto_tarefa, "due_date": data_vencimento, "completed": False}
        self.dados_tarefas.append(nova_tarefa)
        self.salvar_dados_usuario_atual()
        self.entrada_tarefa.delete(0, tk.END)
        self.atualizar_treeview()

    def excluir_tarefa(self):
        id_tarefa = self.obter_id_tarefa_selecionada()
        if id_tarefa and messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta tarefa?", parent=self):
            self.dados_tarefas = [t for t in self.dados_tarefas if t['id'] != id_tarefa]
            self.salvar_dados_usuario_atual()
            self.atualizar_treeview()

    def alternar_conclusao(self):
        id_tarefa = self.obter_id_tarefa_selecionada()
        if id_tarefa:
            for tarefa in self.dados_tarefas:
                if tarefa['id'] == id_tarefa:
                    tarefa['completed'] = not tarefa['completed']
                    break
            self.salvar_dados_usuario_atual()
            self.atualizar_treeview()

    def janela_editar_tarefa(self):
        id_tarefa = self.obter_id_tarefa_selecionada()
        if not id_tarefa: return
        
        tarefa_para_editar = next((t for t in self.dados_tarefas if t['id'] == id_tarefa), None)
        if not tarefa_para_editar: return
        
        janela_edicao = ctk.CTkToplevel(self)
        janela_edicao.title("Editar Tarefa")
        janela_edicao.transient(self)
        janela_edicao.grab_set()
        janela_edicao.configure(fg_color=self.COR_AZUL_MARINHO)
        janela_edicao.geometry("400x150")
        
        entrada_nova_tarefa = ctk.CTkEntry(janela_edicao, width=350, font=("Segoe UI", 12))
        entrada_nova_tarefa.pack(pady=20, padx=20, fill="x", expand=True)
        entrada_nova_tarefa.insert(0, tarefa_para_editar['task'])
        
        def atualizar_tarefa():
            novo_texto = entrada_nova_tarefa.get().strip()
            if novo_texto:
                tarefa_para_editar['task'] = novo_texto
                self.salvar_dados_usuario_atual()
                self.atualizar_treeview()
                janela_edicao.destroy()
        
        botao_atualizar = ctk.CTkButton(janela_edicao, text="Atualizar", command=atualizar_tarefa, fg_color=self.COR_AZUL_BRILHANTE, hover_color="#01337D")
        botao_atualizar.pack(pady=(0, 20))

    def excluir_todas_as_tarefas(self):
        if messagebox.askyesno("Confirmar Exclusão Total", f"Você tem certeza que deseja apagar TODAS as tarefas de {self.nome_usuario}?\nEsta ação não pode ser desfeita.", parent=self):
            self.dados_tarefas = []
            self.salvar_dados_usuario_atual()
            self.atualizar_treeview()

    def sair_do_app(self):
        self.salvar_dados_usuario_atual()
        self.destroy()
        
        def mostrar_selecao_usuario():
            self.janela_pai.atualizar_lista_e_combobox_usuarios()
            self.janela_pai.deiconify()

        TelaSplash(self.janela_pai, texto="Voltando ao menu...", duracao=1500, funcao_retorno=mostrar_selecao_usuario)

if __name__ == "__main__":
    app_login = TelaSelecaoUsuario()
    app_login.mainloop()