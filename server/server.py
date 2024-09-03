import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import ctypes
import sys

class ChatServer:
    def __init__(self, master, server_ip, port):
        self.master = master
        self.server_ip = server_ip
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_ip, self.port))
        self.server_socket.listen(2)
        self.clients = []

        self.master.title("Futuristic Chat Server")
        self.master.geometry("400x500")
        self.master.configure(bg='#5a0a5a')

        self.chat_window = scrolledtext.ScrolledText(master, state=tk.DISABLED, bg='#2e2e2e', fg='#dcdcdc', font=("Arial", 12), insertbackground='white')
        self.chat_window.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.accept_thread = threading.Thread(target=self.accept_connections, daemon=True)
        self.accept_thread.start()

    def accept_connections(self):
        self.chat_window.config(state=tk.NORMAL)
        self.chat_window.insert(tk.END, "Server listening...\n")
        self.chat_window.config(state=tk.DISABLED)

        while len(self.clients) < 2:
            client_socket, client_address = self.server_socket.accept()
            self.clients.append(client_socket)
            self.chat_window.config(state=tk.NORMAL)
            self.chat_window.insert(tk.END, f"Client {client_address} connected.\n")
            self.chat_window.config(state=tk.DISABLED)
        
        self.chat_window.config(state=tk.NORMAL)
        self.chat_window.insert(tk.END, "Both clients connected.\n")
        self.chat_window.config(state=tk.DISABLED)

        # Start threads for each client
        for client in self.clients:
            threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()

    def handle_client(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message:
                    self.chat_window.config(state=tk.NORMAL)
                    self.chat_window.insert(tk.END, f"Client: {message}\n")
                    self.chat_window.config(state=tk.DISABLED)
                    
                    # Relay message to all other clients
                    for client in self.clients:
                        if client != client_socket:
                            try:
                                client.send(message.encode('utf-8'))
                            except:
                                pass
            except Exception as e:
                print(f"Error handling client: {e}")
                break

    def close(self):
        for client in self.clients:
            client.close()
        self.server_socket.close()
        self.master.destroy()

def hide_console():
    if sys.platform == "win32":
        ctypes.windll.kernel32.SetConsoleTitleW("Hidden Console Window")
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def main():
    hide_console()
    server_ip = "192.168.1.33"  # Replace with your server's IP address
    port = 12345

    root = tk.Tk()
    server = ChatServer(root, server_ip, port)
    root.protocol("WM_DELETE_WINDOW", server.close)
    root.mainloop()

if __name__ == "__main__":
    main()