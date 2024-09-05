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
        self.server_socket.listen(5)  
        self.clients = {}
        self.usernames = {}

        self.master.title("Futuristic Chat Server")
        self.master.geometry("400x500")
        self.master.configure(bg='#5a5a5a')

        self.chat_window = scrolledtext.ScrolledText(master, state=tk.DISABLED, bg='#2e2e2e', fg='#dcdcdc', font=("Arial", 12), insertbackground='white')
        self.chat_window.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.accept_thread = threading.Thread(target=self.accept_connections, daemon=True)
        self.accept_thread.start()

    def accept_connections(self):
        self.chat_window.config(state=tk.NORMAL)
        self.chat_window.insert(tk.END, "Server listening...\n")
        self.chat_window.config(state=tk.DISABLED)

        while True:
            client_socket, client_address = self.server_socket.accept()
            self.clients[client_socket] = client_address
            self.usernames[client_socket] = f"User {len(self.clients)}"

            self.chat_window.config(state=tk.NORMAL)
            self.chat_window.insert(tk.END, f"{self.usernames[client_socket]} connected from {client_address}\n")
            self.chat_window.config(state=tk.DISABLED)

            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()

            # Notify all clients of the new connection
            self.broadcast_presence()

    def handle_client(self, client_socket):
        try:
            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if message:
                    print(f"Received from {self.usernames[client_socket]}: {message}") 
                    self.chat_window.config(state=tk.NORMAL)
                    self.chat_window.insert(tk.END, f"{self.usernames[client_socket]}: {message}\n")
                    self.chat_window.config(state=tk.DISABLED)

                    # Relay message to all other clients
                    self.broadcast_message(message, client_socket)
        except Exception as e:
            print(f"Error in handling client: {e}")  
        finally:
            self.remove_client(client_socket)
    

    def broadcast_message(self, message, sender_socket):
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(f"{self.usernames[sender_socket]}: {message}".encode('utf-8'))
                except:
                    pass

    def broadcast_presence(self):
        presence_message = "Presence Update: " + ", ".join([f"{self.usernames[client]} (Online)" for client in self.clients])
        for client in self.clients:
            try:
                client.send(presence_message.encode('utf-8'))
            except:
                pass

    def remove_client(self, client_socket):
        username = self.usernames.pop(client_socket, None)
        self.clients.pop(client_socket, None)
        client_socket.close()

        self.chat_window.config(state=tk.NORMAL)
        self.chat_window.insert(tk.END, f"{username} has disconnected.\n")
        self.chat_window.config(state=tk.DISABLED)

        # Notify remaining clients of the disconnection
        self.broadcast_presence()

    def close(self):
        for client in self.clients.keys():
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
