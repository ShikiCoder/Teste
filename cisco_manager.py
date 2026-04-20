#!/usr/bin/env python3
"""
Cisco Switch Manager — Configuração de VLANs e Portas via SSH
Requer: pip install netmiko
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time

try:
    from netmiko import ConnectHandler
    from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
    NETMIKO_OK = True
except ImportError:
    NETMIKO_OK = False

# ─────────────────────────────────────────────
# CONFIGURAÇÕES PRÉ-ESTABELECIDAS DO SWITCH
# ─────────────────────────────────────────────
CISCO_DEVICE_DEFAULTS = {
    "device_type": "cisco_ios",
    "conn_timeout": 20,
    # Resolve o erro de key exchange do Cisco IOS antigo
    "ssh_config_file": None,
    "global_delay_factor": 2,
}

SSH_OPTIONS = {
    "kex_algorithms": [
        "diffie-hellman-group1-sha1",
        "diffie-hellman-group14-sha1",
        "diffie-hellman-group-exchange-sha1",
        "diffie-hellman-group-exchange-sha256",
    ],
    "disabled_algorithms": {
        "pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]
    },
}

# Cores e estilo
BG       = "#0d1117"
BG2      = "#161b22"
BG3      = "#21262d"
ACCENT   = "#00d4aa"
ACCENT2  = "#0ea5e9"
DANGER   = "#f85149"
WARNING  = "#e3b341"
SUCCESS  = "#3fb950"
TEXT     = "#e6edf3"
TEXT2    = "#8b949e"
BORDER   = "#30363d"

FONT_MONO = ("Courier New", 10)
FONT_UI   = ("Segoe UI", 10)
FONT_H    = ("Segoe UI", 12, "bold")
FONT_SM   = ("Segoe UI", 9)


# ─────────────────────────────────────────────
# FUNÇÕES DE CONEXÃO / CONFIGURAÇÃO
# ─────────────────────────────────────────────
class SwitchManager:
    def __init__(self):
        self.connection = None

    def connect(self, host, username, password, secret=""):
        device = {
            **CISCO_DEVICE_DEFAULTS,
            "host": host,
            "username": username,
            "password": password,
            "secret": secret if secret else password,
            **SSH_OPTIONS,
        }
        self.connection = ConnectHandler(**device)
        self.connection.enable()
        return self.connection.find_prompt()

    def disconnect(self):
        if self.connection:
            self.connection.disconnect()
            self.connection = None

    def is_connected(self):
        return self.connection is not None

    def create_vlan(self, vlan_id, vlan_name, ip_address=None, subnet_mask=None):
        """Cria VLAN e opcionalmente configura SVI (IP de gateway Layer 3)."""
        commands = [
            f"vlan {vlan_id}",
            f" name {vlan_name}",
            "exit",
        ]
        if ip_address and subnet_mask:
            commands += [
                f"interface vlan {vlan_id}",
                f" ip address {ip_address} {subnet_mask}",
                " no shutdown",
                "exit",
            ]
        output = self.connection.send_config_set(commands)
        # Salva config
        output += self.connection.save_config()
        return output

    def assign_port_access(self, interface, vlan_id):
        """Configura porta em modo access numa VLAN."""
        commands = [
            f"interface {interface}",
            " switchport mode access",
            f" switchport access vlan {vlan_id}",
            " no shutdown",
            "exit",
        ]
        output = self.connection.send_config_set(commands)
        output += self.connection.save_config()
        return output

    def assign_port_trunk(self, interface, allowed_vlans):
        """Configura porta em modo trunk com VLANs permitidas."""
        commands = [
            f"interface {interface}",
            " switchport mode trunk",
            f" switchport trunk allowed vlan {allowed_vlans}",
            " no shutdown",
            "exit",
        ]
        output = self.connection.send_config_set(commands)
        output += self.connection.save_config()
        return output

    def show_vlans(self):
        return self.connection.send_command("show vlan brief")

    def show_interfaces(self):
        return self.connection.send_command("show interfaces status")

    def shutdown_port(self, interface):
        commands = [
            f"interface {interface}",
            " shutdown",
            "exit",
        ]
        output = self.connection.send_config_set(commands)
        output += self.connection.save_config()
        return output


# ─────────────────────────────────────────────
# INTERFACE GRÁFICA
# ─────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cisco Switch Manager")
        self.geometry("960x680")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.manager = SwitchManager()
        self._build_ui()

    # ── Layout Principal ──────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG2, height=56)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        tk.Label(hdr, text="⬡  Cisco Switch Manager",
                 font=("Segoe UI", 14, "bold"), bg=BG2,
                 fg=ACCENT).pack(side="left", padx=20, pady=12)

        self.lbl_status = tk.Label(hdr, text="● Desconectado",
                                   font=FONT_SM, bg=BG2, fg=DANGER)
        self.lbl_status.pack(side="right", padx=20)

        # Notebook (abas)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG3, foreground=TEXT2,
                        padding=[16, 8], font=FONT_UI, borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", BG2)],
                  foreground=[("selected", ACCENT)])

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=0, pady=0)

        self.tab_conn  = tk.Frame(nb, bg=BG)
        self.tab_vlan  = tk.Frame(nb, bg=BG)
        self.tab_port  = tk.Frame(nb, bg=BG)
        self.tab_show  = tk.Frame(nb, bg=BG)

        nb.add(self.tab_conn, text="  🔌  Conexão  ")
        nb.add(self.tab_vlan, text="  🏷️  VLANs  ")
        nb.add(self.tab_port, text="  🔧  Portas  ")
        nb.add(self.tab_show, text="  📋  Visualizar  ")

        self._build_conn_tab()
        self._build_vlan_tab()
        self._build_port_tab()
        self._build_show_tab()

        # Log inferior
        log_frame = tk.Frame(self, bg=BG2, height=200)
        log_frame.pack(fill="x", side="bottom")
        log_frame.pack_propagate(False)

        tk.Label(log_frame, text="LOG DE SAÍDA", font=("Segoe UI", 8, "bold"),
                 bg=BG2, fg=TEXT2).pack(anchor="w", padx=12, pady=(8, 0))

        self.log = scrolledtext.ScrolledText(
            log_frame, bg=BG, fg=TEXT, font=FONT_MONO,
            insertbackground=ACCENT, relief="flat", bd=0,
            state="disabled", height=8
        )
        self.log.pack(fill="both", expand=True, padx=8, pady=(2, 8))

    # ── Aba Conexão ───────────────────────────
    def _build_conn_tab(self):
        f = tk.Frame(self.tab_conn, bg=BG)
        f.place(relx=0.5, rely=0.45, anchor="center")

        self._section(f, "Dados de Conexão SSH")

        fields = [
            ("IP do Switch",     "entry_host",   "ex: 192.168.1.1"),
            ("Usuário",          "entry_user",   "ex: admin"),
            ("Senha",            "entry_pass",   "••••••••"),
            ("Enable Secret",    "entry_secret", "deixe vazio se igual à senha"),
        ]
        for label, attr, placeholder in fields:
            row = tk.Frame(f, bg=BG)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, width=16, anchor="w",
                     font=FONT_UI, bg=BG, fg=TEXT2).pack(side="left")
            e = self._entry(row, placeholder,
                            show="*" if "Senha" in label or "Secret" in label else "")
            e.pack(side="left", fill="x", expand=True)
            setattr(self, attr, e)

        tk.Frame(f, bg=BORDER, height=1).pack(fill="x", pady=12)

        btn_row = tk.Frame(f, bg=BG)
        btn_row.pack()
        self._btn(btn_row, "Conectar", self._do_connect, ACCENT).pack(side="left", padx=6)
        self._btn(btn_row, "Desconectar", self._do_disconnect, DANGER).pack(side="left", padx=6)

    # ── Aba VLANs ─────────────────────────────
    def _build_vlan_tab(self):
        f = tk.Frame(self.tab_vlan, bg=BG)
        f.place(relx=0.5, rely=0.45, anchor="center")

        self._section(f, "Criar / Configurar VLAN")

        fields = [
            ("ID da VLAN",        "v_id",      "ex: 10"),
            ("Nome da VLAN",      "v_name",    "ex: FINANCEIRO"),
            ("IP Gateway (SVI)",  "v_ip",      "ex: 192.168.10.1  (opcional)"),
            ("Máscara de Sub-rede","v_mask",   "ex: 255.255.255.0 (opcional)"),
        ]
        for label, attr, ph in fields:
            row = tk.Frame(f, bg=BG)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, width=20, anchor="w",
                     font=FONT_UI, bg=BG, fg=TEXT2).pack(side="left")
            e = self._entry(row, ph)
            e.pack(side="left", fill="x", expand=True)
            setattr(self, attr, e)

        tk.Frame(f, bg=BORDER, height=1).pack(fill="x", pady=12)
        self._btn(f, "✔  Aplicar VLAN no Switch", self._do_vlan, ACCENT).pack()

    # ── Aba Portas ────────────────────────────
    def _build_port_tab(self):
        f = tk.Frame(self.tab_port, bg=BG)
        f.place(relx=0.5, rely=0.45, anchor="center")

        self._section(f, "Atribuir Porta a VLAN")

        fields = [
            ("Interface",         "p_iface",  "ex: GigabitEthernet0/1  ou  e0/1"),
            ("VLAN ID / VLANs",   "p_vlan",   "ex: 10  ou  10,20,30 (trunk)"),
        ]
        for label, attr, ph in fields:
            row = tk.Frame(f, bg=BG)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, width=20, anchor="w",
                     font=FONT_UI, bg=BG, fg=TEXT2).pack(side="left")
            e = self._entry(row, ph)
            e.pack(side="left", fill="x", expand=True)
            setattr(self, attr, e)

        tk.Frame(f, bg=BORDER, height=1).pack(fill="x", pady=8)

        # Modo
        mode_f = tk.Frame(f, bg=BG)
        mode_f.pack(fill="x", pady=4)
        tk.Label(mode_f, text="Modo da Porta", width=20, anchor="w",
                 font=FONT_UI, bg=BG, fg=TEXT2).pack(side="left")
        self.p_mode = tk.StringVar(value="access")
        tk.Radiobutton(mode_f, text="Access", variable=self.p_mode,
                       value="access", bg=BG, fg=TEXT,
                       selectcolor=BG3, activebackground=BG,
                       font=FONT_UI).pack(side="left", padx=8)
        tk.Radiobutton(mode_f, text="Trunk", variable=self.p_mode,
                       value="trunk", bg=BG, fg=TEXT,
                       selectcolor=BG3, activebackground=BG,
                       font=FONT_UI).pack(side="left")

        tk.Frame(f, bg=BORDER, height=1).pack(fill="x", pady=12)

        btn_row = tk.Frame(f, bg=BG)
        btn_row.pack()
        self._btn(btn_row, "✔  Aplicar Porta", self._do_port, ACCENT).pack(side="left", padx=6)
        self._btn(btn_row, "⏻  Shutdown Porta", self._do_shutdown, DANGER).pack(side="left", padx=6)

    # ── Aba Visualizar ────────────────────────
    def _build_show_tab(self):
        f = tk.Frame(self.tab_show, bg=BG)
        f.pack(fill="both", expand=True, padx=20, pady=20)

        self._section(f, "Consultar Switch")

        btn_row = tk.Frame(f, bg=BG)
        btn_row.pack(pady=8)
        self._btn(btn_row, "Show VLAN Brief", self._do_show_vlans, ACCENT2).pack(side="left", padx=6)
        self._btn(btn_row, "Show Interfaces Status", self._do_show_ifaces, ACCENT2).pack(side="left", padx=6)

        self.show_box = scrolledtext.ScrolledText(
            f, bg=BG2, fg=TEXT, font=FONT_MONO,
            relief="flat", bd=0, state="disabled"
        )
        self.show_box.pack(fill="both", expand=True, pady=8)

    # ── Helpers de Widget ─────────────────────
    def _section(self, parent, title):
        tk.Label(parent, text=title, font=FONT_H,
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(0, 12))

    def _entry(self, parent, placeholder="", show=""):
        e = tk.Entry(parent, bg=BG3, fg=TEXT, insertbackground=ACCENT,
                     relief="flat", bd=0, font=FONT_UI, show=show,
                     width=34, highlightthickness=1,
                     highlightbackground=BORDER, highlightcolor=ACCENT)
        if placeholder and not show:
            e.insert(0, placeholder)
            e.config(fg=TEXT2)
            def on_focus_in(ev, entry=e, ph=placeholder):
                if entry.get() == ph:
                    entry.delete(0, "end")
                    entry.config(fg=TEXT)
            def on_focus_out(ev, entry=e, ph=placeholder):
                if not entry.get():
                    entry.insert(0, ph)
                    entry.config(fg=TEXT2)
            e.bind("<FocusIn>", on_focus_in)
            e.bind("<FocusOut>", on_focus_out)
        return e

    def _btn(self, parent, text, cmd, color=ACCENT):
        return tk.Button(parent, text=text, command=cmd,
                         bg=color, fg=BG, font=("Segoe UI", 10, "bold"),
                         relief="flat", bd=0, padx=18, pady=8,
                         cursor="hand2", activebackground=TEXT,
                         activeforeground=BG)

    # ── Log ───────────────────────────────────
    def _log(self, msg, color=TEXT):
        self.log.config(state="normal")
        ts = time.strftime("%H:%M:%S")
        self.log.insert("end", f"[{ts}] {msg}\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def _set_show(self, text):
        self.show_box.config(state="normal")
        self.show_box.delete("1.0", "end")
        self.show_box.insert("end", text)
        self.show_box.config(state="disabled")

    # ── Ações (rodam em thread para não travar UI) ──
    def _run(self, fn):
        threading.Thread(target=fn, daemon=True).start()

    def _do_connect(self):
        if not NETMIKO_OK:
            messagebox.showerror("Erro", "Netmiko não instalado.\nExecute: pip install netmiko")
            return

        host   = self.entry_host.get().strip()
        user   = self.entry_user.get().strip()
        passwd = self.entry_pass.get().strip()
        secret = self.entry_secret.get().strip()

        placeholders = ["ex: 192.168.1.1", "ex: admin", "••••••••",
                        "deixe vazio se igual à senha"]
        if host in placeholders or not host or not user or not passwd:
            messagebox.showwarning("Atenção", "Preencha IP, usuário e senha.")
            return

        self._log(f"Conectando a {host}...")
        self.lbl_status.config(text="● Conectando...", fg=WARNING)

        def task():
            try:
                prompt = self.manager.connect(host, user, passwd, secret)
                self.lbl_status.config(text=f"● Conectado  {prompt}", fg=SUCCESS)
                self._log(f"Conexão estabelecida. Prompt: {prompt}", SUCCESS)
            except NetmikoAuthenticationException:
                self.lbl_status.config(text="● Desconectado", fg=DANGER)
                self._log("Erro: usuário ou senha incorretos.", DANGER)
            except NetmikoTimeoutException:
                self.lbl_status.config(text="● Desconectado", fg=DANGER)
                self._log("Erro: timeout — verifique IP e conectividade.", DANGER)
            except Exception as ex:
                self.lbl_status.config(text="● Desconectado", fg=DANGER)
                self._log(f"Erro: {ex}", DANGER)

        self._run(task)

    def _do_disconnect(self):
        self.manager.disconnect()
        self.lbl_status.config(text="● Desconectado", fg=DANGER)
        self._log("Desconectado do switch.")

    def _do_vlan(self):
        if not self.manager.is_connected():
            messagebox.showwarning("Atenção", "Conecte ao switch primeiro.")
            return
        vid   = self.v_id.get().strip()
        vname = self.v_name.get().strip()
        vip   = self.v_ip.get().strip()
        vmask = self.v_mask.get().strip()

        phs = ["ex: 10", "ex: FINANCEIRO", "ex: 192.168.10.1  (opcional)",
               "ex: 255.255.255.0 (opcional)"]
        if vid in phs or not vid or not vname or vname in phs:
            messagebox.showwarning("Atenção", "Informe ao menos ID e Nome da VLAN.")
            return

        use_ip   = vip   not in phs and vip
        use_mask = vmask not in phs and vmask

        self._log(f"Criando VLAN {vid} ({vname})...")

        def task():
            try:
                out = self.manager.create_vlan(
                    vid, vname,
                    use_ip   or None,
                    use_mask or None
                )
                self._log(f"VLAN {vid} configurada com sucesso.")
                self._log(out)
            except Exception as ex:
                self._log(f"Erro ao criar VLAN: {ex}", DANGER)

        self._run(task)

    def _do_port(self):
        if not self.manager.is_connected():
            messagebox.showwarning("Atenção", "Conecte ao switch primeiro.")
            return
        iface = self.p_iface.get().strip()
        vlan  = self.p_vlan.get().strip()
        mode  = self.p_mode.get()

        phs = ["ex: GigabitEthernet0/1  ou  e0/1", "ex: 10  ou  10,20,30 (trunk)"]
        if not iface or iface in phs or not vlan or vlan in phs:
            messagebox.showwarning("Atenção", "Preencha interface e VLAN.")
            return

        self._log(f"Configurando {iface} → modo {mode}, VLAN {vlan}...")

        def task():
            try:
                if mode == "access":
                    out = self.manager.assign_port_access(iface, vlan)
                else:
                    out = self.manager.assign_port_trunk(iface, vlan)
                self._log(f"Porta {iface} configurada com sucesso.")
                self._log(out)
            except Exception as ex:
                self._log(f"Erro ao configurar porta: {ex}", DANGER)

        self._run(task)

    def _do_shutdown(self):
        if not self.manager.is_connected():
            messagebox.showwarning("Atenção", "Conecte ao switch primeiro.")
            return
        iface = self.p_iface.get().strip()
        if not iface or iface == "ex: GigabitEthernet0/1  ou  e0/1":
            messagebox.showwarning("Atenção", "Informe a interface.")
            return
        if not messagebox.askyesno("Confirmar", f"Dar shutdown em {iface}?"):
            return

        self._log(f"Executando shutdown em {iface}...")

        def task():
            try:
                out = self.manager.shutdown_port(iface)
                self._log(f"Porta {iface} desligada.")
                self._log(out)
            except Exception as ex:
                self._log(f"Erro: {ex}", DANGER)

        self._run(task)

    def _do_show_vlans(self):
        if not self.manager.is_connected():
            messagebox.showwarning("Atenção", "Conecte ao switch primeiro.")
            return
        self._log("Buscando VLANs...")

        def task():
            try:
                out = self.manager.show_vlans()
                self._set_show(out)
                self._log("VLANs carregadas.")
            except Exception as ex:
                self._log(f"Erro: {ex}", DANGER)

        self._run(task)

    def _do_show_ifaces(self):
        if not self.manager.is_connected():
            messagebox.showwarning("Atenção", "Conecte ao switch primeiro.")
            return
        self._log("Buscando status das interfaces...")

        def task():
            try:
                out = self.manager.show_interfaces()
                self._set_show(out)
                self._log("Interfaces carregadas.")
            except Exception as ex:
                self._log(f"Erro: {ex}", DANGER)

        self._run(task)


# ─────────────────────────────────────────────
if __name__ == "__main__":
    if not NETMIKO_OK:
        print("⚠  Netmiko não encontrado. Instale com:")
        print("   pip install netmiko")
        print("Iniciando em modo de pré-visualização...\n")

    app = App()
    app.mainloop()
