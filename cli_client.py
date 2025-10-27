import socket
import json
import threading

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ("localhost", 10000)
print(f"Connecting to the port {format(server_address)}")

connectionTries = 0


def chooseNickname():
    while True:
        nickName = input("Choose your nickname: ")
        if nickName:
            message = json.dumps({"messageType": "nickname", "content": nickName})
            sock.sendall(message.encode())
            break


while True:
    try:
        sock.connect(server_address)
        chooseNickname()
        break
    except ConnectionRefusedError:
        print("Connection refused, retrying...")
        connectionTries += 1
        if connectionTries >= 5:
            print("Max connection attempts reached, exiting.")
            exit()
        continue

def receiveMessages():
    while True:
        data = sock.recv(256)
        if data:
            message_dict = json.loads(data.decode())
            message_type = message_dict.get("type", "incoming")
            if message_type == "system":
                print(message_dict["content"])
            else:
                print(message_dict["content"])
            
try:
    message = ""
    threading.Thread(target=receiveMessages, args=(), kwargs={}).start()
    while message != "exit":
        message = input("Send a message: ")
        message = json.dumps({"messageType": "message", "content": message})
        sock.sendall(message.encode())

        amount_received = 0
        amount_expected = len(message)
finally:
    print("Closing the connection")
    sock.close()
