from netmiko import ConnectHandler

def configurar_vlan(VLAN_NUMBER, INTERFACE_SWITCH, VLAN_VALUE, VLAN_MASK):

    switch = {
        "device_type": "cisco_ios",
        "host": "192.168.200.1",
        "username": "admin",
        "password": "admin",
        "secret": "admin",
    }

    connection = ConnectHandler(**switch)
    connection.enable()

    config_commands = [
        f"vlan {VLAN_NUMBER}",
        f"name VLAN_{VLAN_NUMBER}",

        f"interface vlan {VLAN_NUMBER}",
        f"ip address {VLAN_VALUE} {VLAN_MASK}",
        "no shutdown",

        f"interface {INTERFACE_SWITCH}",
        "switchport mode access",
        f"switchport access vlan {VLAN_NUMBER}",
        "no shutdown",
    ]

    output = connection.send_config_set(config_commands)
    connection.save_config()
    connection.disconnect()

    return output