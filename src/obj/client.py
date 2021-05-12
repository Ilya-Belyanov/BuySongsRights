import json
import socket
import threading

from data.clientConfig import *


class Client:
    def __init__(self, clientConfig: ClientConfig):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientConfig = clientConfig
        self.work = True

    def run(self):
        try:
            self.client.connect((self.clientConfig.SERVER_IP, self.clientConfig.SERVER_PORT))
        except ConnectionRefusedError:
            print(f"Server ({self.clientConfig.SERVER_IP}:{self.clientConfig.SERVER_PORT}) is not available")
            return
        writeThread = threading.Thread(target=self.write)
        writeThread.start()
        self.receive()

    def write(self):
        try:
            self.printCommands()
            while True:
                command = input("")
                self.sendPacket(command)
        except (KeyboardInterrupt, EOFError):
            self.disconnect()

    def receive(self):
        try:
            while self.work:
                # Получаем пакет с информацией от сервера
                packet = json.loads(self.client.recv(self.clientConfig.HEADER).decode("utf-8"))
                print(packet)
        except (ConnectionAbortedError, ConnectionResetError, ValueError):
            self.disconnect()

    def sendPacket(self, packetDict):
        packet = bytes(json.dumps(packetDict), encoding="utf-8")
        self.client.sendall(packet)

    # Отправка пакета на сервер ***
    def disconnect(self):
        self.work = False
        self.client.close()

    @staticmethod
    def printCommands():
        print("Команды:")
