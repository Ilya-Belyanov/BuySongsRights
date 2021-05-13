import json
import socket
import threading

from data.clientConfig import *
from data.serverConfig import *


class Client:
    def __init__(self, clientConfig: ClientConfig):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientConfig = clientConfig
        self.isConnect = False
        self.id = -1

    def run(self):
        try:
            self.client.connect((self.clientConfig.SERVER_IP, self.clientConfig.SERVER_PORT))
            self.isConnect = True
        except ConnectionRefusedError:
            print(f"Server ({self.clientConfig.SERVER_IP}:{self.clientConfig.SERVER_PORT}) is not available")
            return
        writeThread = threading.Thread(target=self.__receive)
        writeThread.start()
        self.__login()

    def __receive(self):
        try:
            while self.isConnect:
                # Получаем пакет с информацией от сервера
                packet = json.loads(self.client.recv(self.clientConfig.HEADER).decode("utf-8"))
                self.__checkServerReceive(packet)
        except (ConnectionAbortedError, ConnectionResetError, ValueError):
            self.__disconnect()

    def __login(self):
        while True:
            choose = input('\n'
                           f'Введите {ClientKeyWords.REG} для регистрации \n'
                           f'Введите {ClientKeyWords.AUTH} для авторизации \n'
                           f'Выход: {ClientKeyWords.REQ_DISC}\n'
                           ':')

            if choose == ClientKeyWords.REG or choose == ClientKeyWords.AUTH:
                msg = {
                    ClientPacketKeyWords.TYPE: clientKeyWordsToTypes[choose],
                    ClientPacketKeyWords.NAME: input("Введите логин:  "),
                    ClientPacketKeyWords.PASS: input("Введите пароль: ")
                }
                self.__sendPacket(msg)
                break
            elif choose == ClientKeyWords.REQ_DISC:
                self.__disconnectRequest()
                break
            else:
                print('Что-то вы не то ввели!')

    def __startWork(self):
        try:
            self.printCommands()
            command = input("")
            self.__checkClientEnter(command)
        except (KeyboardInterrupt, EOFError):
            self.__disconnectRequest()

    def __checkClientEnter(self, command: str):
        if command == ClientKeyWords.REQ_DISC:
            self.__disconnectRequest()
        else:
            print("Команда не найдена")
            self.__startWork()

    def __checkServerReceive(self, packet: dict):
        print("~~~Пришел пакет: ", packet, "~~~")
        if packet[ServerPacketKeyWords.TYPE] == ServerTypes.REQ_DISC:
            print("Сервер запросил разрыв соединения")
            self.__sendPacket({ClientPacketKeyWords.TYPE: ClientTypes.PROOF_DISC})
            self.__disconnect()

        elif packet[ServerPacketKeyWords.TYPE] == ServerTypes.PROOF_DISC:
            self.__disconnect()

        elif packet[ServerPacketKeyWords.TYPE] == ServerTypes.ERR_REG_AUTH:
            print(packet[ServerPacketKeyWords.MESSAGE])
            self.__login()

        elif packet[ServerPacketKeyWords.TYPE] == ServerTypes.SUCCESS_REG or packet[ServerPacketKeyWords.TYPE] == ServerTypes.SUCCESS_AUTH:
            print(packet[ServerPacketKeyWords.MESSAGE])
            self.id = packet[ServerPacketKeyWords.ID]
            self.__startWork()

    def __sendPacket(self, packetDict):
        packet = bytes(json.dumps(packetDict), encoding="utf-8")
        self.client.sendall(packet)

    def __disconnectRequest(self):
        if self.isConnect:
            self.__sendPacket({ClientPacketKeyWords.TYPE: ClientTypes.REQ_DISC})

    def __disconnect(self):
        if self.isConnect:
            self.isConnect = False
            self.client.close()

    @staticmethod
    def printCommands():
        print("Команды:")
        print("Выход: !exit")
