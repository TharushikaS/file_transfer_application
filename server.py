import socket
import threading
import os

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5000
SERVER_DATA_PATH = 'server_files'  # Folder for storing files
active_threads = 0  # Track active threads

# Function to handle client requests
def handle_client(client_socket, address):
    global active_threads
    print(f"[📡] New client connected: {address}")
    
    while True:
        try:
            command = client_socket.recv(1024).decode()
            if not command:
                break

            if command == 'LIST':
                files = os.listdir(SERVER_DATA_PATH)
                client_socket.send('\n'.join(files).encode() if files else "[⚠️] No files available.".encode())

            elif command.startswith('UPLOAD'):
                filename = command.split()[1]
                client_socket.send("READY".encode())  # Acknowledge

                filesize = int(client_socket.recv(1024).decode().strip())
                file_path = os.path.join(SERVER_DATA_PATH, filename)

                with open(file_path, 'wb') as f:
                    received = 0
                    while received < filesize:
                        chunk = client_socket.recv(min(1024, filesize - received))
                        if not chunk:
                            break
                        f.write(chunk)
                        received += len(chunk)
                        print(f"[📥] Receiving {filename}... {int((received/filesize)*100)}% complete", end="\r")

                print(f"\n[✅] Upload complete: {filename}")
                client_socket.send("[✅] File uploaded successfully.".encode())

            elif command.startswith('DOWNLOAD'):
                filename = command.split()[1]
                file_path = os.path.join(SERVER_DATA_PATH, filename)

                if os.path.exists(file_path):
                    filesize = os.path.getsize(file_path)
                    client_socket.send(f"{filesize}\n".encode())

                    with open(file_path, 'rb') as f:
                        client_socket.sendall(f.read())

                    print(f"[📤] File sent successfully: {filename}")

                else:
                    client_socket.send("File not found".encode())

            elif command == 'QUIT':
                break

        except Exception as e:
            print(f"[❌] Error handling client {address}: {e}")
            break

    print(f"[🔌] Client disconnected: {address}")
    client_socket.close()
    
    # Decrease active thread count
    active_threads -= 1
    print(f"[🔻] Active threads: {active_threads}")

# Function to start the server
def start_server():
    global active_threads

    if not os.path.exists(SERVER_DATA_PATH):
        os.makedirs(SERVER_DATA_PATH)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"[🚀] Server listening on {SERVER_HOST}:{SERVER_PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"[🧵] Creating new thread for client: {addr}")

        # Increase active thread count
        active_threads += 1
        print(f"[🔺] Active threads: {active_threads}")

        threading.Thread(target=handle_client, args=(client_socket, addr)).start()

if __name__ == '__main__':
    start_server()
