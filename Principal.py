from netmiko import ConnectHandler

def configurar_switch(HOSTNAME, VLAN, INTERFACE_VLAN, INTERFACE_SWITCH, VLAN_VALUE, VLAN_MASK):

    switch = {
        "device_type": "cisco_ios",
        "host": "192.168.200.1",
        "username": "admin",
        "password": "cisco",
        "secret": "cisco",
    }

    connection = ConnectHandler(**switch)
    connection.enable()

    config_commands = [
        f"hostname {HOSTNAME}",

        f"vlan {VLAN}",
        f"name VLAN_{VLAN}",

        f"interface {INTERFACE_VLAN}",
        f"ip address {VLAN_VALUE} {VLAN_MASK}",
        "no shutdown",

        f"interface {INTERFACE_SWITCH}",
        "switchport mode access",
        f"switchport access vlan {VLAN}",
        "no shutdown",
    ]

    output = connection.send_config_set(config_commands)
    connection.save_config()
    connection.disconnect()

    return output