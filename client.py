import socket
import os
import threading

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000

class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((SERVER_HOST, SERVER_PORT))
        print("[✅] Connected to the server.")

    def list_files(self):
        """Requests a list of available files from the server."""
        self.socket.send('LIST'.encode())
        files = self.socket.recv(1024).decode()
        return files.split('\n') if files else []

    def send_file(self, filepath):
        """Uploads a file to the server using a separate thread."""
        thread = threading.Thread(target=self._upload_file, args=(filepath,))
        thread.start()

    def _upload_file(self, filepath):
        """Handles file upload process."""
        if not os.path.exists(filepath):
            print("[❌] Error: File does not exist!")
            return

        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)

        try:
            self.socket.send(f'UPLOAD {filename}'.encode())
            self.socket.recv(1024)  # Acknowledgment from server
            self.socket.send(f"{filesize}\n".encode())

            with open(filepath, 'rb') as f:
                sent = 0
                while chunk := f.read(1024):
                    self.socket.sendall(chunk)
                    sent += len(chunk)
                    print(f"[📤] Uploading... {int((sent/filesize)*100)}% complete", end="\r")

            print("\n[✅] Upload complete!")
            print(self.socket.recv(1024).decode())  # Server confirmation

        except Exception as e:
            print(f"[❌] Error during upload: {e}")

    def receive_file(self, filename, save_path):
        """Downloads a file from the server using a separate thread."""
        thread = threading.Thread(target=self._download_file, args=(filename, save_path))
        thread.start()

    def _download_file(self, filename, save_path):
        """Handles file download process."""
        self.socket.send(f'DOWNLOAD {filename}'.encode())
        response = self.socket.recv(1024).decode()

        if response.startswith('File not found'):
            print("[❌] " + response)
            return

        try:
            filesize, filedata = response.split("\n", 1)
            filesize = int(filesize)

            with open(save_path, 'wb') as f:
                f.write(filedata.encode())  # Initial data chunk
                received = len(filedata)

                while received < filesize:
                    chunk = self.socket.recv(min(1024, filesize - received))
                    f.write(chunk)
                    received += len(chunk)
                    print(f"[📥] Downloading... {int((received/filesize)*100)}% complete", end="\r")

            print(f"\n[✅] File downloaded successfully: {save_path}")

        except Exception as e:
            print(f"[❌] Error during download: {e}")

    def close(self):
        """Closes the client connection."""
        self.socket.send('QUIT'.encode())
        self.socket.close()
        print("[🔌] Connection closed.")

if __name__ == '__main__':
    client = Client()

    while True:
        command = input("\nEnter command (LIST, UPLOAD <file>, DOWNLOAD <file> <save_path>, QUIT): ").strip()
        parts = command.split(maxsplit=2)

        if command == "LIST":
            files = client.list_files()
            print("[📁] Available files on server:\n" + "\n".join(files) if files else "[⚠️] No files available.")

        elif parts[0] == "UPLOAD" and len(parts) == 2:
            client.send_file(parts[1])

        elif parts[0] == "DOWNLOAD" and len(parts) == 3:
            client.receive_file(parts[1], parts[2])

        elif command == "QUIT":
            client.close()
            break

        else:
            print("[⚠️] Invalid command! Use LIST, UPLOAD <file>, DOWNLOAD <file> <save_path>, or QUIT.")
