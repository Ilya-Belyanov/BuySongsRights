import json
import socket
import threading

from data.clientConfig import *
from data.serverConfig import *
from ..core.beautyPrint import *
from ..core.clientEnterParse import *


class Client:
    def __init__(self, clientConfig: ClientConfig):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientConfig = clientConfig
        self.isConnect = False
        self.id = -1
        self.isStaff = False
        self.clientInput = threading.Event()

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
                self.clientInput.set()
        except (ConnectionAbortedError, ConnectionResetError, ValueError):
            self.__disconnect()

    def __login(self):
        while True:
            choose = input('\n'
                           'Команды\n'
                           f'Регистрация: {ClientCommand.REG} \n'
                           f'Авторизация: {ClientCommand.AUTH}\n'
                           f'Выход: {ClientCommand.REQ_DISC}\n'
                           ': ')

            if choose == ClientCommand.REG or choose == ClientCommand.AUTH:
                msg = {
                    ClientPacketKey.TYPE: clientKeyWordsToTypes[choose],
                    ClientPacketKey.NAME: input("Введите логин:  "),
                    ClientPacketKey.PASS: input("Введите пароль: ")
                }
                self.__sendPacket(msg)
                break
            elif choose == ClientCommand.REQ_DISC:
                self.__disconnectRequest()
                break
            else:
                print('Что-то вы не то ввели!')

    def __startWork(self):
        try:
            self.__printCommands()
            while self.isConnect:
                command = input("Команда (help - список команд): ")
                print("")
                self.clientInput.clear()
                self.__checkClientEnter(command.lower())
                self.clientInput.wait()
        except (KeyboardInterrupt, EOFError):
            self.__disconnectRequest()

    def __checkClientEnter(self, command: str):
        if command == ClientCommand.HELP:
            self.__printCommands()
            self.clientInput.set()

        elif command == ClientCommand.REQ_DISC:
            self.__disconnectRequest()

        elif command == ClientCommand.ALL_SONGS:
            self.__sendPacket({ClientPacketKey.TYPE: clientKeyWordsToTypes[command]})

        elif command == ClientCommand.ALL_TAGS:
            self.__requestAllTags()

        elif command == ClientCommand.ADD_SONG:
            self.__addSong()

        elif command == ClientCommand.MY_SONGS:
            msg = {
                ClientPacketKey.TYPE: ClientTypes.MY_SONGS,
                ClientPacketKey.ID: self.id
            }
            self.__sendPacket(msg)

        elif command == ClientCommand.BUYING_SONGS:
            msg = {
                ClientPacketKey.TYPE: ClientTypes.BUYING_SONGS,
                ClientPacketKey.ID: self.id
            }
            self.__sendPacket(msg)

        elif command == ClientCommand.BUY_SONG:
            self.__buySong()

        else:
            print("Команда не найдена", end="\n\n")
            self.clientInput.set()

    def __checkServerReceive(self, packet: dict):
        # print("~~~Пришел пакет: ", packet, "~~~")
        if packet[ServerPacketKey.TYPE] == ServerTypes.REQ_DISC:
            print("Сервер запросил разрыв соединения")
            self.__sendPacket({ClientPacketKey.TYPE: ClientTypes.PROOF_DISC})
            self.__disconnect()

        elif packet[ServerPacketKey.TYPE] == ServerTypes.PROOF_DISC:
            self.__disconnect()

        elif packet[ServerPacketKey.TYPE] == ServerTypes.ERR_REG_AUTH:
            print(packet[ServerPacketKey.MESSAGE])
            writeThread = threading.Thread(target=self.__login)
            writeThread.start()

        elif packet[ServerPacketKey.TYPE] == ServerTypes.SUCCESS_REG or \
                packet[ServerPacketKey.TYPE] == ServerTypes.SUCCESS_AUTH:

            print(packet[ServerPacketKey.MESSAGE], end="\n\n")
            self.id = packet[ServerPacketKey.ID]
            self.isStaff = packet[ServerPacketKey.IS_STAFF]
            writeThread = threading.Thread(target=self.__startWork)
            writeThread.start()

        elif packet[ServerPacketKey.TYPE] == ServerTypes.ALL_SONGS:
            printAllSongs(packet[ServerPacketKey.SONGS],
                          packet[ServerPacketKey.AUTHORS],
                          packet[ServerPacketKey.TAGS])

        elif packet[ServerPacketKey.TYPE] == ServerTypes.ADD_SONG:
            print("Успешно!" if packet[ServerPacketKey.RESULT] else "Неудача(Возможно такая песня у вас уже есть",
                  end="\n\n")

        elif packet[ServerPacketKey.TYPE] == ServerTypes.ALL_TAGS:
            printAllTags(packet[ServerPacketKey.TAGS])

        elif packet[ServerPacketKey.TYPE] == ServerTypes.USER_SONGS:
            printMySongs(packet[ServerPacketKey.SONGS], packet[ServerPacketKey.TAGS])

        elif packet[ServerPacketKey.TYPE] == ServerTypes.USER_BUYING_SONGS:
            printBuyingSongs(packet[ServerPacketKey.SONGS],
                             packet[ServerPacketKey.AUTHORS],
                             packet[ServerPacketKey.TAGS])

        elif packet[ServerPacketKey.TYPE] == ServerTypes.USER_BUY_SONG:
            print("Успешно!" if packet[ServerPacketKey.RESULT] else packet[ServerPacketKey.ERROR], end="\n\n")

    def __addSong(self):
        while True:
            tags = input(f"Введите теги через запятую (или '{ClientCommand.ALL_TAGS}' для получения всех тегов): ")
            if tags == ClientCommand.ALL_TAGS:
                self.__requestAllTags()
                self.clientInput.clear()
                self.clientInput.wait()
            else:
                break
        msg = {
            ClientPacketKey.TYPE: ClientTypes.ADD_SONG,
            ClientPacketKey.ID: self.id,
            ClientPacketKey.NAME: input("Введите имя песни: "),
            ClientPacketKey.TAGS: seekTags(tags)
        }
        self.__sendPacket(msg)

    def __requestAllTags(self):
        msg = {
            ClientPacketKey.TYPE: ClientTypes.ALL_TAGS
        }
        self.__sendPacket(msg)

    def __buySong(self):
        msg = {
            ClientPacketKey.TYPE: ClientTypes.BUY_SONG,
            ClientPacketKey.ID: self.id,
            ClientPacketKey.NAME: input("Введите имя песни: "),
            ClientPacketKey.AUTHOR: input("Введите имя автора: ")
        }
        self.__sendPacket(msg)

    def __sendPacket(self, packetDict):
        packet = bytes(json.dumps(packetDict), encoding="utf-8")
        self.client.sendall(packet)

    def __disconnectRequest(self):
        if self.isConnect:
            self.__sendPacket({ClientPacketKey.TYPE: ClientTypes.REQ_DISC})

    def __disconnect(self):
        if self.isConnect:
            self.isConnect = False
            self.client.close()

    @staticmethod
    def __printCommands():
        print("\nКоманды:")
        print(f"1) Список песен: {ClientCommand.ALL_SONGS}")
        print(f"2) Добавить песню: {ClientCommand.ADD_SONG}")
        print(f"3) Список тэгов: {ClientCommand.ALL_TAGS}")
        print(f"4) Список моих песен: {ClientCommand.MY_SONGS}")
        print(f"5) Список купленных песен: {ClientCommand.BUYING_SONGS}")
        print(f"6) Купить песню: {ClientCommand.BUY_SONG}")
        print(f"Выход: {ClientCommand.REQ_DISC}\n")
