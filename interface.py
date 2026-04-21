from main import configurar_vlan

def menu():
    print("\n=== CONFIGURADOR DE SWITCH ===")
    print("1 - Configurar VLAN")
    print("0 - Sair")

def configurar_vlan_interface():
    VLAN = input("Número da VLAN: ")
    INTERFACE_SWITCH = input("Porta do Switch (ex: Ethernet0/1): ")
    IP = input("IP da VLAN: ")
    MASK = input("Máscara (ex: 255.255.255.0): ")

    print("\nAplicando configuração...\n")

    resultado = configurar_vlan(VLAN, INTERFACE_SWITCH, IP, MASK)

    print("\n✅ Configuração concluída!")
    print(resultado)


# LOOP PRINCIPAL
while True:
    menu()
    opcao = input("\nEscolha uma opção: ")

    if opcao == "1":
        configurar_vlan_interface()

    elif opcao == "0":
        print("Saindo...")
        break

    else:
        print("❌ Opção inválida!")

    continuar = input("\nDeseja fazer outra configuração? (s/n): ").lower()

    if continuar != "s":
        print("Encerrando...")
        break