import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import datetime
import json
import os
import re

# Caminho absoluto para salvar e carregar corretamente os arquivos JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRAZOS_FILE = os.path.join(BASE_DIR, "prazos.json")
PERITOS_FILE = os.path.join(BASE_DIR, "peritos.json")
PERICIAS_FILE = os.path.join(BASE_DIR, "pericias.json")

def carregar_dados(file):
    """Carrega dados de um arquivo JSON"""
    try:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar {file}: {str(e)}")
        return {}

def salvar_dados(file, data):
    """Salva dados em um arquivo JSON"""
    try:
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar {file}: {str(e)}")

# Carrega dados iniciais
prazos = carregar_dados(PRAZOS_FILE)
peritos = carregar_dados(PERITOS_FILE)
pericias = carregar_dados(PERICIAS_FILE)

class SistemaPrazos:
    def __init__(self, root):
        self.root = root
        self.root.title("CPJ - Controle de Prazos e Perícias")
        self.root.geometry("1100x700")
        
        # Configuração de estilo
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        
        self.criar_interface()
        self.atualizar_lista(datetime.date.today())

    def criar_interface(self):
        """Cria a interface gráfica principal"""
        # Frame superior com dashboard
        self.dashboard = ttk.LabelFrame(self.root, text="Perícias Marcadas (Próximos 30 dias)")
        self.dashboard.pack(side=tk.TOP, fill="x", padx=10, pady=5)
        
        self.dashboard_text = tk.Text(self.dashboard, height=6, bg="white", state="disabled", 
                                    font=('Arial', 10), wrap=tk.WORD)
        scroll = ttk.Scrollbar(self.dashboard, command=self.dashboard_text.yview)
        self.dashboard_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.dashboard_text.pack(fill="both", expand=True)

        # Barra de ferramentas
        tool_frame = ttk.Frame(self.root)
        tool_frame.pack(side=tk.TOP, fill="x", padx=10, pady=5)
        
        buttons = [
            ("Cadastrar Perito", self.cadastrar_perito),
            ("Adicionar Prazo", self.adicionar_prazo),
            ("Cadastrar Perícia", self.cadastrar_pericia),
            ("Prazos do Dia", lambda: self.atualizar_lista(datetime.date.today())),
            ("Prazos da Semana", self.filtrar_semana),
            ("Prazos do Mês", self.filtrar_mes)
        ]
        
        for text, command in buttons:
            ttk.Button(tool_frame, text=text, command=command).pack(side=tk.LEFT, padx=2)

        # Barra de busca
        search_frame = ttk.Frame(tool_frame)
        search_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(search_frame, text="Buscar Processo:").pack(side=tk.LEFT)
        self.entry_busca = ttk.Entry(search_frame, width=30)
        self.entry_busca.pack(side=tk.LEFT, padx=2)
        ttk.Button(search_frame, text="Buscar", command=self.buscar_por_processo).pack(side=tk.LEFT)

        # Área principal com calendário e lista
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Calendário
        cal_frame = ttk.Frame(main_frame)
        cal_frame.pack(side=tk.LEFT, fill="y", padx=5)
        
        self.cal = Calendar(cal_frame, selectmode='day', date_pattern='yyyy-mm-dd',
                          font=('Arial', 12), background='white', foreground='black',
                          selectbackground='#4a6984', selectforeground='white')
        self.cal.pack(padx=5, pady=5)
        self.cal.selection_set(datetime.date.today())
        self.cal.bind("<<CalendarSelected>>", lambda e: self.atualizar_lista(self.cal.selection_get()))

        # Lista de prazos e perícias
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5)
        
        self.lista_prazos = tk.Listbox(list_frame, width=90, height=35, bg="white", 
                                     font=("Arial", 10), selectbackground='#4a6984',
                                     selectforeground='white')
        scroll = ttk.Scrollbar(list_frame, command=self.lista_prazos.yview)
        self.lista_prazos.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.lista_prazos.pack(fill="both", expand=True)

        # Atualiza dashboard inicial
        self.atualizar_dashboard()
        self.configurar_menu_contexto()

    def formatar_cpf(self, cpf):
        """Formata o CPF para o padrão 000.000.000-00"""
        cpf = re.sub(r'\D', '', cpf)
        if len(cpf) != 11:
            return None
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"

    def validar_processo(self, processo):
        """Valida o formato do número do processo"""
        padrao = r'^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$'
        return re.match(padrao, processo) is not None

    def atualizar_dashboard(self):
        """Atualiza o painel de perícias agendadas"""
        self.dashboard_text.config(state="normal")
        self.dashboard_text.delete(1.0, tk.END)
        
        hoje = datetime.date.today()
        fim = hoje + datetime.timedelta(days=30)
        pericias_proximas = []
        
        for data_str in sorted(pericias):
            try:
                data = datetime.datetime.strptime(data_str, "%Y-%m-%d").date()
                if hoje <= data <= fim:
                    for p in pericias[data_str]:
                        pericias_proximas.append((data_str, p))
            except:
                continue
        
        if pericias_proximas:
            for data_str, p in sorted(pericias_proximas, key=lambda x: x[0]):
                status = "✔" if p.get("realizada", False) else "🔴"
                linha = (f"{status} Data: {data_str} | Perito: {p['perito_nome']} | "
                        f"Processo: {p['processo']} | Especialidade: {p['especialidade']}\n")
                self.dashboard_text.insert(tk.END, linha)
        else:
            self.dashboard_text.insert(tk.END, "Nenhuma perícia marcada para os próximos 30 dias.")
        
        self.dashboard_text.config(state="disabled")

    def atualizar_lista(self, data):
        """Atualiza a lista de prazos e perícias para a data selecionada"""
        self.lista_prazos.delete(0, tk.END)
        data_str = data.strftime("%Y-%m-%d")
        
        if data_str in prazos:
            self.lista_prazos.insert(tk.END, "=== PRAZOS ===")
            self.lista_prazos.itemconfig(tk.END, {'fg': 'blue'})
            
            for p in prazos[data_str]:
                status = "✔" if p["concluido"] else "🔴"
                cor = "green" if p["concluido"] else "red"
                self.lista_prazos.insert(tk.END, 
                    f"{status} {p['processo']} - {p['perito_nome']} - {p.get('descricao', '')}")
                self.lista_prazos.itemconfig(tk.END, {'fg': cor})
        
        if data_str in pericias:
            self.lista_prazos.insert(tk.END, "=== PERÍCIAS ===")
            self.lista_prazos.itemconfig(tk.END, {'fg': 'blue'})
            
            for p in pericias[data_str]:
                status = "✔" if p.get("realizada", False) else "🔴"
                cor = "green" if p.get("realizada", False) else "red"
                self.lista_prazos.insert(tk.END, 
                    f"{status} {p['processo']} - {p['perito_nome']} - {p['especialidade']}")
                self.lista_prazos.itemconfig(tk.END, {'fg': cor})

    def cadastrar_perito(self):
        """Janela para cadastro de novo perito"""
        top = tk.Toplevel(self.root)
        top.title("Cadastro de Perito")
        top.geometry("400x250")
        top.resizable(False, False)
        
        main_frame = ttk.Frame(top)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Campos do formulário
        campos = [
            ("Nome Completo:", 40),
            ("CPF:", 20),
            ("Telefone:", 20),
            ("Profissão:", 30)
        ]
        
        entries = []
        for label, width in campos:
            frame = ttk.Frame(main_frame)
            frame.pack(fill="x", pady=5)
            ttk.Label(frame, text=label).pack(side=tk.LEFT)
            entry = ttk.Entry(frame, width=width)
            entry.pack(side=tk.RIGHT)
            entries.append(entry)
        
        nome_entry, cpf_entry, telefone_entry, profissao_entry = entries
        
        def salvar_perito():
            try:
                nome = nome_entry.get().strip()
                cpf = self.formatar_cpf(cpf_entry.get())
                telefone = telefone_entry.get().strip()
                profissao = profissao_entry.get().strip()
                
                # Validações
                if not nome: raise ValueError("Nome é obrigatório!")
                if not cpf: raise ValueError("CPF inválido! Deve conter 11 dígitos.")
                if any(perito.get("cpf") == cpf for perito in peritos.values()):
                    raise ValueError("CPF já cadastrado!")
                if not telefone: raise ValueError("Telefone é obrigatório!")
                if not profissao: raise ValueError("Profissão é obrigatória!")

                peritos[nome] = {
                    "nome": nome,
                    "cpf": cpf,
                    "telefone": telefone,
                    "profissao": profissao,
                    "data_cadastro": datetime.date.today().strftime("%Y-%m-%d")
                }
                
                salvar_dados(PERITOS_FILE, peritos)
                messagebox.showinfo("Sucesso", "Perito cadastrado com sucesso!")
                top.destroy()
                
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="Cancelar", command=top.destroy).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Salvar", command=salvar_perito).pack(side=tk.RIGHT)

    def cadastrar_pericia(self):
        """Janela para cadastro de nova perícia"""
        if not peritos:
            messagebox.showerror("Erro", "Cadastre pelo menos um perito primeiro!")
            return
            
        top = tk.Toplevel(self.root)
        top.title("Cadastrar Perícia")
        top.geometry("450x550")
        top.resizable(False, False)
        
        main_frame = ttk.Frame(top)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Data da perícia
        ttk.Label(main_frame, text="Data da Perícia:").pack(anchor=tk.W)
        cal = Calendar(main_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=5)
        
        # Número do processo
        ttk.Label(main_frame, text="Número do Processo (0000000-00.0000.0.00.0000):").pack(anchor=tk.W)
        processo_entry = ttk.Entry(main_frame, width=30)
        processo_entry.pack(fill="x")
        
        # Perito
        ttk.Label(main_frame, text="Perito:").pack(anchor=tk.W)
        perito_var = tk.StringVar()
        perito_dropdown = ttk.Combobox(main_frame, textvariable=perito_var, 
                                      values=list(peritos.keys()), width=35)
        perito_dropdown.pack(fill="x")
        
        # Especialidade
        ttk.Label(main_frame, text="Especialidade:").pack(anchor=tk.W)
        especialidade_entry = ttk.Entry(main_frame, width=30)
        especialidade_entry.pack(fill="x")
        
        # Local
        ttk.Label(main_frame, text="Local:").pack(anchor=tk.W)
        local_entry = ttk.Entry(main_frame, width=30)
        local_entry.pack(fill="x")
        
        # Observações
        ttk.Label(main_frame, text="Observações:").pack(anchor=tk.W)
        obs_entry = tk.Text(main_frame, height=4, width=40, wrap=tk.WORD)
        obs_entry.pack(fill="x")

        def salvar():
            try:
                processo = processo_entry.get().strip()
                perito = perito_var.get()
                especialidade = especialidade_entry.get().strip()
                local = local_entry.get().strip()
                observacoes = obs_entry.get("1.0", tk.END).strip()
                
                if not self.validar_processo(processo):
                    raise ValueError("Número do processo inválido!")
                if not perito: raise ValueError("Selecione um perito!")
                if not especialidade: raise ValueError("Especialidade é obrigatória!")
                if not local: raise ValueError("Local é obrigatório!")

                data_str = cal.selection_get().strftime("%Y-%m-%d")
                
                if data_str in pericias:
                    for p in pericias[data_str]:
                        if p["processo"] == processo:
                            raise ValueError(f"Perícia já cadastrada para {data_str}!")

                pericias.setdefault(data_str, []).append({
                    "processo": processo,
                    "perito_nome": perito,
                    "especialidade": especialidade,
                    "local": local,
                    "observacoes": observacoes if observacoes else None,
                    "realizada": False,
                    "data_cadastro": datetime.date.today().strftime("%Y-%m-%d")
                })
                
                salvar_dados(PERICIAS_FILE, pericias)
                messagebox.showinfo("Sucesso", "Perícia agendada com sucesso!")
                self.atualizar_dashboard()
                top.destroy()
                
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="Cancelar", command=top.destroy).pack(side=tk.LEFT)
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=10)
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="Salvar", command=salvar).pack(side=tk.RIGHT)

    
    def adicionar_prazo(self):
        """Janela para adicionar novo prazo"""
        if not peritos:
            messagebox.showerror("Erro", "Cadastre pelo menos um perito primeiro!")
            return

        top = tk.Toplevel(self.root)
        top.title("Adicionar Prazo")
        top.geometry("450x550")
        top.resizable(False, False)

        main_frame = ttk.Frame(top)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(main_frame, text="Data do Prazo:").pack(anchor=tk.W)
        cal = Calendar(main_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=5)

        ttk.Label(main_frame, text="Número do Processo (0000000-00.0000.0.00.0000):").pack(anchor=tk.W)
        processo_entry = ttk.Entry(main_frame, width=30)
        processo_entry.pack(fill="x")

        ttk.Label(main_frame, text="Perito:").pack(anchor=tk.W)
        perito_var = tk.StringVar()
        perito_dropdown = ttk.Combobox(main_frame, textvariable=perito_var, 
                                      values=list(peritos.keys()), width=35)
        perito_dropdown.pack(fill="x")

        ttk.Label(main_frame, text="Descrição:").pack(anchor=tk.W)
        descricao_entry = ttk.Entry(main_frame, width=40)
        descricao_entry.pack(fill="x")

        ttk.Label(main_frame, text="Prioridade:").pack(anchor=tk.W)
        prioridade_var = tk.StringVar(value="Normal")
        ttk.Radiobutton(main_frame, text="Baixa", variable=prioridade_var, value="Baixa").pack(anchor=tk.W)
        ttk.Radiobutton(main_frame, text="Normal", variable=prioridade_var, value="Normal").pack(anchor=tk.W)
        ttk.Radiobutton(main_frame, text="Alta", variable=prioridade_var, value="Alta").pack(anchor=tk.W)

        def salvar():
            try:
                processo = processo_entry.get().strip()
                perito = perito_var.get()
                descricao = descricao_entry.get().strip()
                prioridade = prioridade_var.get()

                if not self.validar_processo(processo):
                    raise ValueError("Número do processo inválido!")
                if not perito: raise ValueError("Selecione um perito!")
                if not descricao: raise ValueError("Descrição é obrigatória!")

                data_str = cal.selection_get().strftime("%Y-%m-%d")

                if data_str in prazos:
                    for p in prazos[data_str]:
                        if p["processo"] == processo:
                            raise ValueError(f"Prazo já cadastrado para {data_str}!")

                prazos.setdefault(data_str, []).append({
                    "processo": processo,
                    "perito_nome": perito,
                    "descricao": descricao,
                    "prioridade": prioridade,
                    "concluido": False,
                    "data_cadastro": datetime.date.today().strftime("%Y-%m-%d")
                })

                salvar_dados(PRAZOS_FILE, prazos)
                messagebox.showinfo("Sucesso", "Prazo adicionado com sucesso!")
                self.atualizar_lista(cal.selection_get())
                top.destroy()

            except Exception as e:
                messagebox.showerror("Erro", str(e))

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="Cancelar", command=top.destroy).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Salvar", command=salvar).pack(side=tk.RIGHT)


    def filtrar_semana(self):
        hoje = datetime.date.today()
        fim_semana = hoje + datetime.timedelta(days=7)
        self.lista_prazos.delete(0, tk.END)
        encontrados = False
        
        # Prazos
        for data_str in sorted(prazos):
            try:
                data = datetime.datetime.strptime(data_str, "%Y-%m-%d").date()
                if hoje <= data <= fim_semana:
                    if not encontrados:
                        self.lista_prazos.insert(tk.END, "=== PRAZOS DA SEMANA ===")
                        self.lista_prazos.itemconfig(tk.END, {'fg': 'blue'})
                        encontrados = True
                    for prazo in prazos[data_str]:
                        status = "✔" if prazo["concluido"] else "🔴"
                        cor = "green" if prazo["concluido"] else "red"
                        self.lista_prazos.insert(tk.END, f"{data_str} - {status} {prazo['processo']}")
                        self.lista_prazos.itemconfig(tk.END, {'fg': cor})
            except: continue
        
        # Perícias
        for data_str in sorted(pericias):
            try:
                data = datetime.datetime.strptime(data_str, "%Y-%m-%d").date()
                if hoje <= data <= fim_semana:
                    if not encontrados:
                        self.lista_prazos.insert(tk.END, "=== PERÍCIAS DA SEMANA ===")
                        self.lista_prazos.itemconfig(tk.END, {'fg': 'blue'})
                        encontrados = True
                    for pericia in pericias[data_str]:
                        status = "✔" if pericia.get("realizada", False) else "🔴"
                        cor = "green" if pericia.get("realizada", False) else "red"
                        self.lista_prazos.insert(tk.END, f"{data_str} - {status} {pericia['processo']}")
                        self.lista_prazos.itemconfig(tk.END, {'fg': cor})
            except: continue
        
        if not encontrados:
            self.lista_prazos.insert(tk.END, "Nenhum registro para esta semana.")
            self.lista_prazos.itemconfig(tk.END, {'fg': 'red'})

    def filtrar_mes(self):
        hoje = datetime.date.today()
        fim_mes = hoje + datetime.timedelta(days=30)
        self.lista_prazos.delete(0, tk.END)
        encontrados = False
        
        # Prazos
        for data_str in sorted(prazos):
            try:
                data = datetime.datetime.strptime(data_str, "%Y-%m-%d").date()
                if hoje <= data <= fim_mes:
                    if not encontrados:
                        self.lista_prazos.insert(tk.END, "=== PRAZOS DO MÊS ===")
                        self.lista_prazos.itemconfig(tk.END, {'fg': 'blue'})
                        encontrados = True
                    for prazo in prazos[data_str]:
                        status = "✔" if prazo["concluido"] else "🔴"
                        cor = "green" if prazo["concluido"] else "red"
                        self.lista_prazos.insert(tk.END, f"{data_str} - {status} {prazo['processo']}")
                        self.lista_prazos.itemconfig(tk.END, {'fg': cor})
            except: continue
        
        # Perícias
        for data_str in sorted(pericias):
            try:
                data = datetime.datetime.strptime(data_str, "%Y-%m-%d").date()
                if hoje <= data <= fim_mes:
                    if not encontrados:
                        self.lista_prazos.insert(tk.END, "=== PERÍCIAS DO MÊS ===")
                        self.lista_prazos.itemconfig(tk.END, {'fg': 'blue'})
                        encontrados = True
                    for pericia in pericias[data_str]:
                        status = "✔" if pericia.get("realizada", False) else "🔴"
                        cor = "green" if pericia.get("realizada", False) else "red"
                        self.lista_prazos.insert(tk.END, f"{data_str} - {status} {pericia['processo']}")
                        self.lista_prazos.itemconfig(tk.END, {'fg': cor})
            except: continue
        
        if not encontrados:
            self.lista_prazos.insert(tk.END, "Nenhum registro para este mês.")
            self.lista_prazos.itemconfig(tk.END, {'fg': 'red'})

    def buscar_por_processo(self):
            termo = self.entry_busca.get().strip()
            self.lista_prazos.delete(0, tk.END)
            encontrados = False

            for data_str in sorted(prazos, reverse=True):
                for prazo in prazos[data_str]:
                    if termo.lower() in prazo["processo"].lower():
                        if not encontrados:
                            self.lista_prazos.insert(tk.END, "=== PRAZOS ENCONTRADOS ===")
                            self.lista_prazos.itemconfig(tk.END, {'fg': 'blue'})
                            encontrados = True
                        status = "✔" if prazo["concluido"] else "🔴"
                        cor = "green" if prazo["concluido"] else "red"
                        self.lista_prazos.insert(tk.END, f"{data_str} - {status} {prazo['processo']}")
                        self.lista_prazos.itemconfig(tk.END, {'fg': cor})

            for data_str in sorted(pericias, reverse=True):
                for pericia in pericias[data_str]:
                    if termo.lower() in pericia["processo"].lower():
                        if not encontrados:
                            self.lista_prazos.insert(tk.END, "=== PERÍCIAS ENCONTRADAS ===")
                            self.lista_prazos.itemconfig(tk.END, {'fg': 'blue'})
                            encontrados = True
                        status = "✔" if pericia.get("realizada", False) else "🔴"
                        cor = "green" if pericia.get("realizada", False) else "red"
                        self.lista_prazos.insert(tk.END, f"{data_str} - {status} {pericia['processo']}")
                        self.lista_prazos.itemconfig(tk.END, {'fg': cor})

            if not encontrados:
                self.lista_prazos.insert(tk.END, "Nenhum resultado encontrado.")
                self.lista_prazos.itemconfig(tk.END, {'fg': 'red'})



    def configurar_menu_contexto(self):
        """Configura o menu de contexto para a lista de prazos"""
        self.menu_contexto = tk.Menu(self.root, tearoff=0)
        self.menu_contexto.add_command(label="Concluir", command=self.concluir_item)
        self.menu_contexto.add_command(label="Reagendar", command=self.reagendar_item)
        self.menu_contexto.add_command(label="Editar", command=self.editar_item)
        self.menu_contexto.add_separator()
        self.menu_contexto.add_command(label="Apagar", command=self.apagar_item)
        self.lista_prazos.bind("<Button-3>", self.mostrar_menu_contexto)

    def mostrar_menu_contexto(self, event):
        try:
            self.lista_prazos.selection_clear(0, tk.END)
            self.lista_prazos.selection_set(self.lista_prazos.nearest(event.y))
            self.item_selecionado = self.lista_prazos.get(self.lista_prazos.curselection())
            self.menu_contexto.post(event.x_root, event.y_root)
        except:
            pass

    def concluir_item(self):
        if not hasattr(self, 'item_selecionado'):
            return
        texto = self.item_selecionado
        data_str = self.cal.selection_get().strftime("%Y-%m-%d")
        try:
            if "=== PRAZOS ===" in self.lista_prazos.get(0):
                for i, prazo in enumerate(prazos.get(data_str, [])):
                    if prazo["processo"] in texto:
                        prazos[data_str][i]["concluido"] = True
                        salvar_dados(PRAZOS_FILE, prazos)
                        messagebox.showinfo("Sucesso", "Prazo marcado como concluído!")
                        break
            elif "=== PERÍCIAS ===" in self.lista_prazos.get(0):
                for i, pericia in enumerate(pericias.get(data_str, [])):
                    if pericia["processo"] in texto:
                        pericias[data_str][i]["realizada"] = True
                        salvar_dados(PERICIAS_FILE, pericias)
                        messagebox.showinfo("Sucesso", "Perícia marcada como realizada!")
                        break
            self.atualizar_lista(self.cal.selection_get())
            self.atualizar_dashboard()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível concluir o item: {str(e)}")

    def reagendar_item(self):
        if not hasattr(self, 'item_selecionado'):
            return
        texto = self.item_selecionado
        data_original_str = self.cal.selection_get().strftime("%Y-%m-%d")
        top = tk.Toplevel(self.root)
        top.title("Reagendar")
        top.geometry("300x200")
        ttk.Label(top, text="Selecione a nova data:").pack(pady=10)
        novo_cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        novo_cal.pack(pady=10)
        def confirmar_reagendamento():
            nova_data_str = novo_cal.selection_get().strftime("%Y-%m-%d")
            try:
                if "=== PRAZOS ===" in self.lista_prazos.get(0):
                    for i, prazo in enumerate(prazos.get(data_original_str, [])):
                        if prazo["processo"] in texto:
                            item = prazos[data_original_str].pop(i)
                            prazos.setdefault(nova_data_str, []).append(item)
                            salvar_dados(PRAZOS_FILE, prazos)
                            break
                elif "=== PERÍCIAS ===" in self.lista_prazos.get(0):
                    for i, pericia in enumerate(pericias.get(data_original_str, [])):
                        if pericia["processo"] in texto:
                            item = pericias[data_original_str].pop(i)
                            pericias.setdefault(nova_data_str, []).append(item)
                            salvar_dados(PERICIAS_FILE, pericias)
                            break
                messagebox.showinfo("Sucesso", "Item reagendado com sucesso!")
                top.destroy()
                self.atualizar_lista(self.cal.selection_get())
                self.atualizar_dashboard()
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível reagendar: {str(e)}")
        ttk.Button(top, text="Confirmar", command=confirmar_reagendamento).pack(pady=5)

    def editar_item(self):
        if not hasattr(self, 'item_selecionado'):
            return
        texto = self.item_selecionado
        data_str = self.cal.selection_get().strftime("%Y-%m-%d")
        try:
            if "=== PRAZOS ===" in self.lista_prazos.get(0):
                for i, prazo in enumerate(prazos.get(data_str, [])):
                    if prazo["processo"] in texto:
                        self.editar_prazo(data_str, i)
                        break
            elif "=== PERÍCIAS ===" in self.lista_prazos.get(0):
                for i, pericia in enumerate(pericias.get(data_str, [])):
                    if pericia["processo"] in texto:
                        self.editar_pericia(data_str, i)
                        break
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível editar: {str(e)}")

    def apagar_item(self):
        if not hasattr(self, 'item_selecionado'):
            return
        texto = self.item_selecionado
        data_str = self.cal.selection_get().strftime("%Y-%m-%d")
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja apagar este item?"):
            return
        try:
            if "=== PRAZOS ===" in self.lista_prazos.get(0):
                for i, prazo in enumerate(prazos.get(data_str, [])):
                    if prazo["processo"] in texto:
                        prazos[data_str].pop(i)
                        if not prazos[data_str]: prazos.pop(data_str)
                        salvar_dados(PRAZOS_FILE, prazos)
                        break
            elif "=== PERÍCIAS ===" in self.lista_prazos.get(0):
                for i, pericia in enumerate(pericias.get(data_str, [])):
                    if pericia["processo"] in texto:
                        pericias[data_str].pop(i)
                        if not pericias[data_str]: pericias.pop(data_str)
                        salvar_dados(PERICIAS_FILE, pericias)
                        break
            messagebox.showinfo("Sucesso", "Item apagado com sucesso!")
            self.atualizar_lista(self.cal.selection_get())
            self.atualizar_dashboard()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível apagar o item: {str(e)}")

if __name__ == '__main__':
    root = tk.Tk()
    app = SistemaPrazos(root)
    root.mainloop()