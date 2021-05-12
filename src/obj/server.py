import json
import socket
import threading
from threading import Thread

from data.serverConfig import *


class Server:
    def __init__(self, serverConfig: ServerConfig):
        self.clientSockets = list()
        self.serverConfig = serverConfig
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((self.serverConfig.IP, self.serverConfig.PORT))
        self.serverSocket.listen()

    def run(self):
        print(f'Listening {self.serverConfig.IP}:{self.serverConfig.PORT}')
        try:
            while True:
                clientSocket, clientAddress = self.serverSocket.accept()
                print(f"New connection from {clientAddress[0]}:{clientAddress[1]}")
                threading.Thread(target=self.recv_send_request, args=(clientSocket, clientAddress), daemon=True).start()
                self.clientSockets.append(clientSocket)
        except Exception as e:
            print(e)

    def recv_send_request(self, clientSocket, clientAddress):
        while True:
            try:
                recv = clientSocket.recv(self.serverConfig.BLOCK_LENGTH).decode(self.serverConfig.CODE)
                if recv:
                    self.do(recv, clientSocket)
                else:
                    self.close_client(clientSocket, clientAddress)
                    break
            except ConnectionResetError:
                self.close_client(clientSocket, clientAddress)
                break

    def do(self, recv, clientSocket):
        recv = json.loads(recv)
        self.send(recv, clientSocket)

    def send(self, recv, clientSocket):
        answer = {"recv": recv}
        json_request = json.dumps(answer).encode(self.serverConfig.CODE)
        clientSocket.send(json_request)

    def close_server(self):
        for cs in self.clientSockets:
            cs.close()
        self.serverSocket.close()
        print('Server is closed')

    def close_client(self, clientSocket, clientAddress):
        print(f'Closed connection: {clientAddress}')
        self.clientSockets.remove(clientSocket)
        clientSocket.shutdown(socket.SHUT_RDWR)
        clientSocket.close()
