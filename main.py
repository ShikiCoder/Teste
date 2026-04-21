from netmiko import ConnectHandler

def CONNECT(HOST):
    DEVICE = {
        "device_type": "cisco_ios",
        "host": HOST,
        "username": "admin",
        "password": "admin",
        "secret": "admin",
    }

    CONNECTION = ConnectHandler(**DEVICE)
    CONNECTION.enable()
    return CONNECTION


# 🔹 1 - CONFIGURAÇÃO COMPLETA DE VLAN
def CONFIGURE_VLAN(HOST, VLAN, VLAN_NAME, INTERFACE_VLAN, INTERFACE_SWITCH, VLAN_IP, VLAN_MASK):
    CONNECTION = CONNECT(HOST)

    COMMANDS = [
        f"vlan {VLAN}",
        f"name {VLAN_NAME}",
        f"interface vlan {INTERFACE_VLAN}",
        f"ip address {VLAN_IP} {VLAN_MASK}",
        "no shutdown",
        f"interface {INTERFACE_SWITCH}",
        "switchport mode access",
        f"switchport access vlan {VLAN}",
        "no shutdown"
    ]

    OUTPUT = CONNECTION.send_config_set(COMMANDS)
    CONNECTION.save_config()
    CONNECTION.disconnect()

    return OUTPUT


# 🔹 2 - REGISTRAR VLAN
def REGISTER_VLAN(HOST, VLAN, VLAN_NAME):
    CONNECTION = CONNECT(HOST)

    COMMANDS = [
        f"vlan {VLAN}",
        f"name {VLAN_NAME}"
    ]

    OUTPUT = CONNECTION.send_config_set(COMMANDS)
    CONNECTION.save_config()
    CONNECTION.disconnect()

    return OUTPUT


# 🔹 3 - ATIVAR/DESATIVAR INTERFACE
def SET_INTERFACE_STATE(HOST, INTERFACE, STATE):
    CONNECTION = CONNECT(HOST)

    COMMAND = "no shutdown" if STATE == "UP" else "shutdown"

    COMMANDS = [
        f"interface {INTERFACE}",
        COMMAND
    ]

    OUTPUT = CONNECTION.send_config_set(COMMANDS)
    CONNECTION.save_config()
    CONNECTION.disconnect()

    return OUTPUT


# 🔹 4 - CONFIGURAR INTERFACE
def CONFIGURE_INTERFACE(HOST, INTERFACE, VLAN, DESCRIPTION):
    CONNECTION = CONNECT(HOST)

    COMMANDS = [
        f"interface {INTERFACE}",
        f"description {DESCRIPTION}",
        "switchport mode access",
        f"switchport access vlan {VLAN}",
        "no shutdown"
    ]

    OUTPUT = CONNECTION.send_config_set(COMMANDS)
    CONNECTION.save_config()
    CONNECTION.disconnect()

    return OUTPUT


# 🔹 5 - CONFIGURAR TRUNK
def CONFIGURE_TRUNK(HOST, INTERFACE, VLANS):
    CONNECTION = CONNECT(HOST)

    COMMANDS = [
        f"interface {INTERFACE}",
        "switchport mode trunk",
        f"switchport trunk allowed vlan {VLANS}",
        "no shutdown"
    ]

    OUTPUT = CONNECTION.send_config_set(COMMANDS)
    CONNECTION.save_config()
    CONNECTION.disconnect()

    return OUTPUT