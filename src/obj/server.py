import os
import json
import socket
import threading

from data.serverConfig import *
from data.clientConfig import *
from src.obj.pymysql_adapter import PyMySQLAdapter


class Server:
    def __init__(self, serverConfig: ServerConfig):
        self.clientSockets = list()
        self.serverConfig = serverConfig
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((self.serverConfig.IP, self.serverConfig.PORT))
        self.serverSocket.listen()

        confDir = os.getcwd() + "\\data\\"
        with open(confDir + "config.txt") as f:
            config = json.load(f)
        self.dataBase = PyMySQLAdapter(config)

    def run(self):
        print(f'Listening {self.serverConfig.IP}:{self.serverConfig.PORT}')
        try:
            while True:
                clientSocket, clientAddress = self.serverSocket.accept()
                print(f"New connection from {clientAddress[0]}:{clientAddress[1]}")
                threading.Thread(target=self.__clientRequest, args=(clientSocket, clientAddress), daemon=True).start()
                self.clientSockets.append(clientSocket)
        except Exception as e:
            print(e)

    def __clientRequest(self, clientSocket, clientAddress):
        while True:
            try:
                recv = clientSocket.recv(self.serverConfig.BLOCK_LENGTH).decode(self.serverConfig.CODE)
                if recv:
                    recv = json.loads(recv)
                    self.__checkClientPacket(recv, clientSocket, clientAddress)
                    if not self.__isContinueWork(recv):
                        break
                else:
                    self.__disconnectClient(clientSocket, clientAddress)
                    break
            except ConnectionResetError:
                self.__disconnectClient(clientSocket, clientAddress)
                break

    def __checkClientPacket(self, recv, clientSocket, clientAddress):
        print("~~~Клиент прислал: ", recv, "~~~")
        if recv[ClientPacketKeyWords.TYPE] == ClientTypes.REG:
            self.__tryRegister(recv, clientSocket)
        elif recv[ClientPacketKeyWords.TYPE] == ClientTypes.AUTH:
            self.__tryAuthorization(recv, clientSocket)
        elif recv[ClientPacketKeyWords.TYPE] == ClientTypes.REQ_DISC:
            self.__proofDisconnectClient(clientSocket, clientAddress)

    @staticmethod
    def __isContinueWork(recv):
        if recv[ClientPacketKeyWords.TYPE] == ClientTypes.REQ_DISC:
            return False
        return True

    def __tryRegister(self, recv, clientSocket):
        user = {"name": recv[ClientPacketKeyWords.NAME], "password": recv[ClientPacketKeyWords.PASS]}
        users = self.dataBase.getTable("users", where=f"name = '{recv[ClientPacketKeyWords.NAME]}'")
        if len(users) != 0:
            msg = {
                ServerPacketKeyWords.TYPE: ServerTypes.ERR_REG_AUTH,
                ServerPacketKeyWords.MESSAGE: f"Имя {recv[ClientPacketKeyWords.NAME]} занято"
            }
        elif self.dataBase.intoTable("users", user):
            msg = {
                ServerPacketKeyWords.TYPE: ServerTypes.SUCCESS_REG,
                ServerPacketKeyWords.MESSAGE: f"Успешно зарегистрирован {recv[ClientPacketKeyWords.NAME]} с паролем {recv[ClientPacketKeyWords.PASS]}",
                ServerPacketKeyWords.ID: self.dataBase.getKeyLastElement("users")
            }
        else:
            msg = {
                ServerPacketKeyWords.TYPE: ServerTypes.ERR_REG_AUTH,
                ServerPacketKeyWords.MESSAGE: f"Ошибка со стороны Базы данных"
            }
        self.__sendPacket(msg, clientSocket)

    def __tryAuthorization(self, recv, clientSocket):
        user = self.dataBase.getTable("users", where=f"name = '{recv[ClientPacketKeyWords.NAME]}'")
        if len(user) != 0 and recv[ClientPacketKeyWords.PASS] == user[0]["password"]:
            msg = {
                ServerPacketKeyWords.TYPE: ServerTypes.SUCCESS_AUTH,
                ServerPacketKeyWords.MESSAGE: f"Успешно вошел {recv[ClientPacketKeyWords.NAME]}",
                ServerPacketKeyWords.ID: user[0]["id"]
            }
        elif len(user) != 0 and recv[ClientPacketKeyWords.PASS] != user[0]["password"]:
            msg = {
                ServerPacketKeyWords.TYPE: ServerTypes.ERR_REG_AUTH,
                ServerPacketKeyWords.MESSAGE: "Неверный пароль!"
            }
        else:
            msg = {
                ServerPacketKeyWords.TYPE: ServerTypes.ERR_REG_AUTH,
                ServerPacketKeyWords.MESSAGE: f"Имя {recv[ClientPacketKeyWords.NAME]} не найдено!"
            }
        self.__sendPacket(msg, clientSocket)

    def __proofDisconnectClient(self, clientSocket, clientAddress):
        msg = {ServerPacketKeyWords.TYPE: ServerTypes.PROOF_DISC}
        self.__sendPacket(msg, clientSocket)
        self.__disconnectClient(clientSocket, clientAddress)

    def __sendPacket(self, msg, clientSocket):
        json_request = json.dumps(msg).encode(self.serverConfig.CODE)
        clientSocket.send(json_request)

    def __disconnectClient(self, clientSocket, clientAddress):
        print(f'Closed connection: {clientAddress}')
        self.clientSockets.remove(clientSocket)
        clientSocket.shutdown(socket.SHUT_RDWR)
        clientSocket.close()

    def close_server(self):
        for cs in self.clientSockets:
            cs.close()
        self.serverSocket.close()
        print('Server is closed')
