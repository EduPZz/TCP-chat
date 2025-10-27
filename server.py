import socket
import sys
import threading
import os
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ("localhost", 10000)

sock.bind(server_address)

sock.listen(5)  # Allow up to 5 pending connections

clients = []

def printMessage(message):
    content = message["content"]
    separator = os.get_terminal_size().columns - len(content)
    separator = separator // 3

    if message["type"] == "incoming":
        print(content)
    else:
        print(f"{' ' * separator}{content}")


def findClientIndex(clientId):
    isSameId = lambda client: client["id"] == clientId
    client = next(filter(isSameId, clients), None)
    if client:
        return clients.index(client)
    else:
        return -1


def receiveClientMessages(connection, client_address):
    try:
        clientId = len(clients)
        clients.append(
            {"id": clientId, "client_address": client_address, "connection": connection, "nickname": None}
        )

        while True:
            data = connection.recv(256)

            if data:
                digestMessage(data, clientId)
            else:
                print(
                    "No data left from {0} closing connection.".format(client_address)
                )
                break
    except ConnectionResetError:
        print("Client {0} disconnected.".format(client_address))
    finally:
        # Get nickname before removing client
        disconnectedNick = None
        try:
            client = clients[findClientIndex(clientId)]
            disconnectedNick = client.get("nickname")
        except:
            pass
        
        # Notify other clients about the disconnection
        if disconnectedNick:
            clientsToNotify = list(
                filter(lambda client: client["id"] != clientId, clients)
            )
            for client in clientsToNotify:
                notification = json.dumps(
                    {
                        "type": "system",
                        "content": f"--- {disconnectedNick} left the chat ---",
                    }
                )
                try:
                    client["connection"].sendall(notification.encode())
                except:
                    pass
        
        clients.pop(findClientIndex(clientId))
        connection.close()


def digestMessage(data, clientId):
    messageString = data.decode()
    messageDict = json.loads(messageString)
    
    messageType = messageDict["messageType"]

    if messageType == 'nickname':
        clients[findClientIndex(clientId)]["nickname"] = messageDict["content"]
        print(f"User {messageDict['content']} connected!")
        
        newUserNick = messageDict["content"]
        clientsToNotify = list(
            filter(lambda client: client["id"] != clientId, clients)
        )
        for client in clientsToNotify:
            notification = json.dumps(
                {
                    "type": "system",
                    "content": f"--- {newUserNick} joined the chat ---",
                }
            )
            try:
                client["connection"].sendall(notification.encode())
            except:
                pass
    if messageType == "message":
        clientsToSend = list(
            filter(lambda client: client["id"] != clientId, clients)
        )
        senderNickname = clients[findClientIndex(clientId)]["nickname"]
        for client in clientsToSend:
            messageToSend = json.dumps(
                {
                    "type": "incoming",
                    "content": f"{senderNickname}: {messageDict['content']}",
                }
            )
            client["connection"].sendall(messageToSend.encode())


def listenToConnections():
    while True:
        connection, client_address = sock.accept()

        threading.Thread(
            target=receiveClientMessages, args=(connection, client_address), kwargs={}
        ).start()


threading.Thread(target=listenToConnections, args=(), kwargs={}).start()
