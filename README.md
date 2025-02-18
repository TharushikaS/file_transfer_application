**File Transfer Application Project**

The File Transfer Application is a Python-based client-server system that enables file sharing over a network using socket programming. The server manages file storage and client requests, while the client can list available files, upload files to the server, download files from the server, and close the connection.

How It Works:
1. Start the server: python server.py
2. Start the client: python client.py
3. Use commands:
* LIST → View available files on the server
* UPLOAD <source_file_path> → Upload a file to the server (Ex: UPLOAD test_files/test2.txt )
* DOWNLOAD <file_name> <save_path> → Download a file from the server (Ex: DOWNLOAD test3.txt test_files/downloaded_test3.txt )
* QUIT → Disconnect from the server


The File Transfer Application uses multithreading to handle multiple client connections simultaneously. The server handles multiple clients simultaneously using threads, ensuring smooth and efficient file transfers. Each client request is managed in a separate thread, allowing multiple users to interact with the server without blocking others.

Benefits of Multithreading in This Application:
* Concurrent File Transfers → Multiple clients can upload and download files at the same time.
* Non-Blocking Server → The server remains responsive, even with multiple active clients.
* Efficient Resource Utilization → Threads allow better CPU and network resource management.
