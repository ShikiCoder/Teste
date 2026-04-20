from netmiko import ConnectHandler

# Dados do switch
switch = {
    "device_type": "cisco_ios",
    "host": "192.168.1.10",   # IP do switch
    "username": "admin",
    "password": "cisco",
    "secret": "cisco",        # enable password
}

# Conectar ao switch
connection = ConnectHandler(**switch)

# Entrar em modo enable
connection.enable()

# Comandos de configuração
config_commands = [
    # Hostname
    "hostname SW-L3",

    # Criar VLAN
    "vlan 10",
    "name USERS",

    # Interface VLAN (SVI)
    "interface vlan 10",
    "ip address 192.168.10.1 255.255.255.0",
    "no shutdown",

    # Porta física
    "interface gigabitEthernet 0/1",
    "switchport mode access",
    "switchport access vlan 10",
    "no shutdown",

    # Roteamento
    "ip routing",

    # Rota padrão
    "ip route 0.0.0.0 0.0.0.0 192.168.1.1",

    # SSH
    "ip domain-name lab.local",
    "crypto key generate rsa modulus 1024",
    "username admin privilege 15 secret cisco",
    "line vty 0 4",
    "transport input ssh",
    "login local"
]

# Enviar configurações
output = connection.send_config_set(config_commands)

# Salvar configuração
connection.save_config()

# Fechar conexão
connection.disconnect()

print("Configuração aplicada com sucesso!")