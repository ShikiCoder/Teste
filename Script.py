from netmiko import ConnectHandler

# Dados do switch
switch = {
    "device_type": "cisco_ios",
    "host": "192.168.200.1",   # IP do switch
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
    "vlan 12",
    "name USERS",

    # Interface VLAN (SVI)
    "interface vlan 12",
    "ip address 192.168.10.1 255.255.255.0",
    "no shutdown",

    # Porta física
    "interface Ethernet 0/4",
    "switchport mode access",
    "switchport access vlan 12",
    "no shutdown",

    # SSH
    "ip domain-name lab.local",
    "crypto key generate rsa modulus 1024",
    "username admin privilege 15 secret admin",
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