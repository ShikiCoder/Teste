from main import (
    CONFIGURE_VLAN,
    SHOW_VLAN,
    SET_INTERFACE_STATE,
    CONFIGURE_INTERFACE,
    CONFIGURE_TRUNK
)


def MENU():
    print("\n=== MENU DE CONFIGURAÇÃO DE SWITCH ===")
    print("1 - Configuração completa de VLAN")
    print("2 - Mostrar VLANs (show vlan brief)")
    print("3 - Ativar/Desativar Interface")
    print("4 - Configurar Interface")
    print("5 - Configurar Trunk")
    print("0 - Sair")


def OBTER_IP():
    HOST = input("\nDigite o IP do Switch: ")
    return HOST


# 🔹 1
def OPCAO_CONFIGURAR_VLAN():
    HOST = OBTER_IP()
    VLAN = input("ID da VLAN: ")
    VLAN_NAME = input("Nome da VLAN: ")
    INTERFACE_VLAN = input("Interface VLAN (ex: 10): ")
    INTERFACE_SWITCH = input("Porta do Switch (ex: g0/1): ")
    VLAN_IP = input("IP da VLAN: ")
    VLAN_MASK = input("Máscara da VLAN: ")

    print("\nAplicando configuração...\n")
    print(CONFIGURE_VLAN(HOST, VLAN, VLAN_NAME, INTERFACE_VLAN, INTERFACE_SWITCH, VLAN_IP, VLAN_MASK))


# 🔹 2
def OPCAO_MOSTRAR_VLAN():
    HOST = OBTER_IP()

    print("\nBuscando VLANs...\n")
    print(SHOW_VLAN(HOST))


# 🔹 3
def OPCAO_INTERFACE_ESTADO():
    HOST = OBTER_IP()
    INTERFACE = input("Interface: ")
    STATE = input("Estado (UP/DOWN): ").upper()

    print("\nAplicando configuração...\n")
    print(SET_INTERFACE_STATE(HOST, INTERFACE, STATE))


# 🔹 4
def OPCAO_CONFIGURAR_INTERFACE():
    HOST = OBTER_IP()
    INTERFACE = input("Interface: ")
    VLAN = input("VLAN: ")
    DESCRIPTION = input("Descrição: ")

    print("\nAplicando configuração...\n")
    print(CONFIGURE_INTERFACE(HOST, INTERFACE, VLAN, DESCRIPTION))


# 🔹 5
def OPCAO_TRUNK():
    HOST = OBTER_IP()
    INTERFACE = input("Interface: ")
    VLANS = input("VLANs permitidas (ex: 10,20,30): ")

    print("\nAplicando configuração...\n")
    print(CONFIGURE_TRUNK(HOST, INTERFACE, VLANS))


# 🔁 LOOP PRINCIPAL
while True:
    MENU()
    OPCAO = input("\nEscolha uma opção: ")

    if OPCAO == "1":
        OPCAO_CONFIGURAR_VLAN()

    elif OPCAO == "2":
        OPCAO_MOSTRAR_VLAN()

    elif OPCAO == "3":
        OPCAO_INTERFACE_ESTADO()

    elif OPCAO == "4":
        OPCAO_CONFIGURAR_INTERFACE()

    elif OPCAO == "5":
        OPCAO_TRUNK()

    elif OPCAO == "0":
        print("Saindo...")
        break

    else:
        print("❌ Opção inválida")

    CONTINUAR = input("\nDeseja continuar? (S/N): ").upper()
    if CONTINUAR != "S":
        break