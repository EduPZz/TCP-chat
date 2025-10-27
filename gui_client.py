import socket
import json
import threading

import tkinter as tk
from tkinter import scrolledtext, messagebox


class TCPChat:
    def __init__(self, root):
        self.root = root

        self.root.title("TCP Chat")
        self.root.geometry("500x600")
        self.root.configure(bg="#2b2b2b")
        self.main_font = ("Arial", 18)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ("localhost", 10000)
        self.connected = False
        self.nickname = None
        self.set_up_ui()

    def set_up_ui(self):
        self.create_nickname_section()
        self.create_chat_display()
        self.create_input_section()


    def create_nickname_section(self):
        """Cria o campo de nickname e o botão de conexão."""
        self.nickname_frame = tk.Frame(self.root, bg="#2b2b2b")
        self.nickname_frame.pack(pady=20)
        
        tk.Label(
            self.nickname_frame,
            text="nickname:",
            bg="#2b2b2b",
            fg="white",
            font=("Arial", 12)
        ).pack(side=tk.LEFT, padx=5)

        self.nickname_entry = tk.Entry(
            self.nickname_frame,
            font=("Arial", 12),
            width=20
        )
        self.nickname_entry.pack(side=tk.LEFT, padx=5)
        
        self.connection_button = tk.Button(
            self.nickname_frame,
            text="Connect",
            font=("Arial", 14, "bold"),
            bg="white",
            activebackground="gray",
            fg="black",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=20,
            pady=10,
            command=self.connect,
            disabledforeground="gray",
        )
        self.connection_button.pack(padx=10, pady=10)


    def create_chat_display(self):
        """Cria o display de chat (área de mensagens)."""
        self.chat_frame = tk.Frame(self.root, bg="#3a3a3a")
        self.chat_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            width=50,
            height=20,
            font=("Arial", 10),
            bg="#1e1e1e",
            fg="white",
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        self.chat_display.tag_config("incoming", foreground="#4CAF50")
        self.chat_display.tag_config("outgoing", foreground="#2196F3", justify="right")
        self.chat_display.tag_config("system", foreground="#FFA726", justify="center")


    def create_input_section(self):
        """Cria o campo de entrada e botão de envio."""
        self.input_frame = tk.Frame(self.root, bg="#2b2b2b")
        self.input_frame.pack(pady=10, padx=10, fill=tk.X)

        self.message_entry = tk.Entry(
            self.input_frame,
            font=("Arial", 12),
            state=tk.DISABLED
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.message_entry.bind("<Return>", lambda e: self.send_message())

        self.send_btn = tk.Button(
            self.input_frame,
            text="Send",
            command=self.send_message,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            state=tk.DISABLED
        )
        self.send_btn.pack(side=tk.RIGHT)

    
    def receive_messages(self):
        while self.connected:
            try:
                data = self.sock.recv(256)
                if data:
                    message_dict = json.loads(data.decode())
                    if message_dict["type"] == "system":
                        self.add_system_message(message_dict["content"])
                    elif message_dict["type"] == "incoming":
                        self.add_incoming_message(message_dict["content"])
                else:
                    break
            except:
                break
        
        if self.connected:
            self.add_system_message("Disconnected from server")
            self.connected = False
    
    def send_message(self):
        message = self.message_entry.get().strip()
        if not message:
            return
        
        if message.lower() == "exit":
            self.close_connection()
            return
        
        try:
            message_json = json.dumps({"messageType": "message", "content": message})
            self.sock.sendall(message_json.encode())
            self.add_outgoing_message(message)
            self.message_entry.delete(0, tk.END)
        except Exception as e:
            print(f"Error sending message: {e}")
            self.add_system_message("Failed to send message")
    
    def connect(self):
        try:
            self.nickname = self.nickname_entry.get().strip()
            if not self.nickname:
                messagebox.showinfo(
                    title="Erro", message="insira um nickname para se conectar!"
                )
                return
            self.sock.connect(self.server_address)
            
            self.sendNickname()

            self.connected = True
            self.add_system_message(f"Connected as {self.nickname}")

            self.connection_button.config(state=tk.DISABLED)
            self.message_entry.config(state=tk.NORMAL)
            self.send_btn.config(state=tk.NORMAL)
            self.message_entry.focus()

            messagebox.showinfo(title="Success", message="Conectado ao servidor!")
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except ConnectionRefusedError as e:
            print(f"Connection error: {e}")
            messagebox.showinfo(title="Erro", message="Erro ao conectar ao servidor!")

    def add_message(self, message, tag):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{message}\n", tag)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def add_outgoing_message(self, message):
        self.add_message(f"You: {message}", "outgoing")
        
    def add_incoming_message(self, message):
        self.add_message(message, "incoming")
        
    def add_system_message(self, message):
        self.add_message(f"--- {message} ---", "system")
    
    def sendNickname(self):
        message = json.dumps({"messageType": "nickname", "content": self.nickname})
        self.sock.sendall(message.encode())
    
    def close_connection(self):
        self.connected = False
        if self.sock:
            self.sock.close()
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = TCPChat(root)
    root.protocol("WM_DELETE_WINDOW", app.close_connection)
    root.mainloop()
