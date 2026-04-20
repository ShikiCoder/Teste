from main import configurar_switch

print("=== CONFIGURADOR DE SWITCH ===\n")

HOSTNAME = input("Nome do Equipamento: ")
VLAN = input("Configurar a VLAN: ")
INTERFACE_VLAN = input("Interface da VLAN (ex: vlan 10): ")
INTERFACE_SWITCH = input("Porta do Switch (ex: g0/1): ")
VLAN_VALUE = input("IP da VLAN: ")
VLAN_MASK = input("Máscara IP da VLAN: ")

print("\nAplicando configuração...\n")

resultado = configurar_switch(
    HOSTNAME,
    VLAN,
    INTERFACE_VLAN,
    INTERFACE_SWITCH,
    VLAN_VALUE,
    VLAN_MASK
)

print("Configuração concluída!\n")
print(resultado)