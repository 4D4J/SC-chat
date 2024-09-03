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
        self.server_socket.listen(1)
        self.client_socket = None

        self.master.title("Chat Server")
        self.master.geometry("500x600")
        self.master.configure(bg='#1e1e1e')

        # Chat window
        self.chat_window = scrolledtext.ScrolledText(master, state=tk.DISABLED, bg='#2e2e2e', fg='#dcdcdc', font=("Arial", 12), insertbackground='white')
        self.chat_window.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Entry frame
        self.entry_frame = tk.Frame(master, bg='#1e1e1e')
        self.entry_frame.pack(padx=10, pady=10, fill=tk.X)

        self.entry = tk.Entry(self.entry_frame, bg='#3e3e3e', fg='#dcdcdc', font=("Arial", 12), insertbackground='white')
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.entry.bind("<Return>", self.send_message)  # Bind Enter key to send message

        self.send_button = tk.Button(self.entry_frame, text="Send", command=self.send_message, bg='#4e4e4e', fg='#dcdcdc', font=("Arial", 12), relief=tk.FLAT, padx=10, pady=5)
        self.send_button.pack(side=tk.RIGHT, padx=5)

        self.accept_thread = threading.Thread(target=self.accept_connections, daemon=True)
        self.accept_thread.start()

    def accept_connections(self):
        self.chat_window.config(state=tk.NORMAL)
        self.chat_window.insert(tk.END, "Server listening...\n")
        self.chat_window.config(state=tk.DISABLED)
        
        self.client_socket, client_address = self.server_socket.accept()
        self.chat_window.config(state=tk.NORMAL)
        self.chat_window.insert(tk.END, f"Connection established with {client_address}\n")
        self.chat_window.config(state=tk.DISABLED)
        
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.chat_window.config(state=tk.NORMAL)
                    self.chat_window.insert(tk.END, f"Client: {message}\n")
                    self.chat_window.config(state=tk.DISABLED)
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def send_message(self, event=None):
        reply = self.entry.get()
        if reply:
            try:
                self.client_socket.send(reply.encode('utf-8'))
                self.chat_window.config(state=tk.NORMAL)
                self.chat_window.insert(tk.END, f"You: {reply}\n")
                self.chat_window.config(state=tk.DISABLED)
                self.entry.delete(0, tk.END)
            except Exception as e:
                print(f"Error sending message: {e}")

    def close(self):
        if self.client_socket:
            self.client_socket.close()
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
    root.protocol("WM_DELETE_WINDOW", server.close)  # Handle window close event
    root.mainloop()

if __name__ == "__main__":
    main()
