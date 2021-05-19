import os
import json
import socket
import threading

from data.serverConfig import *
from data.clientConfig import *
from data.DataBaseKeyWords import *
from src.obj.pymysql_adapter import PyMySQLAdapter


class Server:
    def __init__(self, serverConfig: ServerConfig):
        self.clientSockets = list()
        self.serverConfig = serverConfig
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((self.serverConfig.IP, self.serverConfig.PORT))
        self.serverSocket.listen()
        self.isWork = False
        confDir = os.getcwd() + "\\data\\"
        with open(confDir + "config.txt") as f:
            config = json.load(f)
        self.dataBase = PyMySQLAdapter(config)

    def run(self):
        print(f'Listening {self.serverConfig.IP}:{self.serverConfig.PORT}')
        self.isWork = True
        try:
            while self.isWork:
                clientSocket, clientAddress = self.serverSocket.accept()
                print(f"New connection from {clientAddress[0]}:{clientAddress[1]}")
                threading.Thread(target=self.__clientRequest, args=(clientSocket, clientAddress), daemon=True).start()
                self.clientSockets.append(clientSocket)
        except Exception as e:
            print(e)
            self.closeServer()

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
        if recv[ClientPacketKey.TYPE] == ClientTypes.REG:
            self.__tryRegister(recv, clientSocket)
        elif recv[ClientPacketKey.TYPE] == ClientTypes.AUTH:
            self.__tryAuthorization(recv, clientSocket)
        elif recv[ClientPacketKey.TYPE] == ClientTypes.ALL_SONGS:
            self.__showAllSongs(clientSocket)
        elif recv[ClientPacketKey.TYPE] == ClientTypes.ADD_SONG:
            self.__addSongs(recv, clientSocket)
        elif recv[ClientPacketKey.TYPE] == ClientTypes.ALL_TAGS:
            self.__showAllTags(clientSocket)
        elif recv[ClientPacketKey.TYPE] == ClientTypes.MY_SONGS:
            self.__showUserSongs(recv, clientSocket)
        elif recv[ClientPacketKey.TYPE] == ClientTypes.BUYING_SONGS:
            self.__showUserBuyingSongs(recv, clientSocket)
        elif recv[ClientPacketKey.TYPE] == ClientTypes.BUY_SONG:
            self.__buySong(recv, clientSocket)
        elif recv[ClientPacketKey.TYPE] == ClientTypes.REQ_DISC:
            self.__proofDisconnectClient(clientSocket, clientAddress)

    @staticmethod
    def __isContinueWork(recv: dict) -> bool:
        return not recv[ClientPacketKey.TYPE] == ClientTypes.REQ_DISC

    def __tryRegister(self, recv: dict, clientSocket):
        user = {UserFields.NAME: recv[ClientPacketKey.NAME], UserFields.PASS: recv[ClientPacketKey.PASS]}
        users = self.dataBase.getTable(DataBaseTables.USERS,
                                       where=f"{UserFields.NAME} = '{recv[ClientPacketKey.NAME]}'")
        if len(users) != 0:
            msg = {
                ServerPacketKey.TYPE: ServerTypes.ERR_REG_AUTH,
                ServerPacketKey.MESSAGE: f"Имя {recv[ClientPacketKey.NAME]} занято"
            }
        elif self.dataBase.intoTable(DataBaseTables.USERS, user):
            userId = self.dataBase.getKeyLastElement(DataBaseTables.USERS)
            msg = {
                ServerPacketKey.TYPE: ServerTypes.SUCCESS_REG,
                ServerPacketKey.MESSAGE: f"Успешно зарегистрирован {recv[ClientPacketKey.NAME]} с паролем {recv[ClientPacketKey.PASS]}",
                ServerPacketKey.ID: userId,
                ServerPacketKey.IS_STAFF: self.isStaff(userId)
            }
        else:
            msg = {
                ServerPacketKey.TYPE: ServerTypes.ERR_REG_AUTH,
                ServerPacketKey.MESSAGE: f"Ошибка со стороны Базы данных"
            }
        self.__sendPacket(msg, clientSocket)

    def __tryAuthorization(self, recv: dict, clientSocket):
        user = self.dataBase.getTable(DataBaseTables.USERS,
                                      where=f"{UserFields.NAME} = '{recv[ClientPacketKey.NAME]}'")
        if len(user) != 0 and recv[ClientPacketKey.PASS] == user[0][UserFields.PASS]:
            msg = {
                ServerPacketKey.TYPE: ServerTypes.SUCCESS_AUTH,
                ServerPacketKey.MESSAGE: f"Успешно вошел {recv[ClientPacketKey.NAME]}",
                ServerPacketKey.ID: user[0][UserFields.ID],
                ServerPacketKey.IS_STAFF: self.isStaff(user[0][UserFields.ID])
            }
        elif len(user) != 0 and recv[ClientPacketKey.PASS] != user[0][UserFields.PASS]:
            msg = {
                ServerPacketKey.TYPE: ServerTypes.ERR_REG_AUTH,
                ServerPacketKey.MESSAGE: "Неверный пароль!"
            }
        else:
            msg = {
                ServerPacketKey.TYPE: ServerTypes.ERR_REG_AUTH,
                ServerPacketKey.MESSAGE: f"Имя {recv[ClientPacketKey.NAME]} не найдено!"
            }
        self.__sendPacket(msg, clientSocket)

    def isStaff(self, userId: int):
        return len(self.dataBase.getTable(DataBaseTables.STAFF, where=f"{StaffFields.USER_ID} = '{userId}'")) > 0

    def __showAllSongs(self, clientSocket):
        tableSongs = self.dataBase.getTable(DataBaseTables.SONGS,
                                            innerJoin=[DataBaseTables.USERS, UserFields.ID, SongFields.OWNER_ID])
        msg = {
            ServerPacketKey.TYPE: ServerTypes.ALL_SONGS,
            ServerPacketKey.SONGS: [song[SongFields.NAME] for song in tableSongs],
            ServerPacketKey.AUTHORS: [song[DataBaseTables.USERS + "." + UserFields.NAME] for song in tableSongs],
            ServerPacketKey.TAGS: self.__songsTags(tableSongs)
        }
        self.__sendPacket(msg, clientSocket)

    def __songsTags(self, songs: list) -> list:
        tags = list()
        for song in songs:
            songsToTag = self.dataBase.getTable(DataBaseTables.SONG_TO_TAG,
                                                where=f"{SongToTagFields.SONG_ID} = {song[SongFields.ID]}")
            tags.append([tag[SongToTagFields.TAG_NAME] for tag in songsToTag])
        return tags

    def __songsAuthors(self, songs: list) -> list:
        authors = list()
        for song in songs:
            songsAuthor = self.dataBase.getTable(DataBaseTables.SONGS,
                                                 innerJoin=[DataBaseTables.USERS, UserFields.ID, SongFields.OWNER_ID],
                                                 where=f"{SongFields.OWNER_ID} = {song[SongFields.OWNER_ID]}")
            authors.append(songsAuthor[0][DataBaseTables.USERS + "." + UserFields.NAME])
        return authors

    def __addSongs(self, recv: dict, clientSocket):
        if self.__isExistSong(recv[ClientPacketKey.NAME], recv[ClientPacketKey.ID]):
            result = False
        else:
            result = True
            song = {SongFields.NAME: recv[ClientPacketKey.NAME],
                    SongFields.OWNER_ID: recv[ClientPacketKey.ID]}
            self.dataBase.intoTable(DataBaseTables.SONGS, song)
            tags = self.__parseTags(recv[ClientPacketKey.TAGS])
            self.__addTagsToSong(self.dataBase.getKeyLastElement(DataBaseTables.SONGS), tags)

        msg = {
            ServerPacketKey.TYPE: ServerTypes.ADD_SONG,
            ServerPacketKey.RESULT: result
        }
        self.__sendPacket(msg, clientSocket)

    def __showAllTags(self, clientSocket):
        dataBaseTags = [tag[TagFields.NAME] for tag in self.dataBase.getTable(DataBaseTables.TAGS)]
        msg = {
            ServerPacketKey.TYPE: ServerTypes.ALL_TAGS,
            ServerPacketKey.TAGS: dataBaseTags
        }
        self.__sendPacket(msg, clientSocket)

    def __showUserSongs(self, recv: dict, clientSocket):
        tableSongs = self.dataBase.getTable(DataBaseTables.SONGS,
                                            innerJoin=[DataBaseTables.USERS, UserFields.ID, SongFields.OWNER_ID],
                                            where=f"{SongFields.OWNER_ID} = {recv[ClientPacketKey.ID]}")
        msg = {
            ServerPacketKey.TYPE: ServerTypes.USER_SONGS,
            ServerPacketKey.SONGS: [song[SongFields.NAME] for song in tableSongs],
            ServerPacketKey.TAGS: self.__songsTags(tableSongs)
        }
        self.__sendPacket(msg, clientSocket)

    def __showUserBuyingSongs(self, recv: dict, clientSocket):
        tableSongs = self.dataBase.getTable(DataBaseTables.USER_BUY_SONG,
                                            innerJoin=[DataBaseTables.SONGS, SongFields.ID, UserBuySong.SONG_ID],
                                            where=f"{UserBuySong.USER_ID} = {recv[ClientPacketKey.ID]}")
        msg = {
            ServerPacketKey.TYPE: ServerTypes.USER_BUYING_SONGS,
            ServerPacketKey.SONGS: [song[SongFields.NAME] for song in tableSongs],
            ServerPacketKey.AUTHORS: self.__songsAuthors(tableSongs),
            ServerPacketKey.TAGS: self.__songsTags(tableSongs)
        }
        self.__sendPacket(msg, clientSocket)

    def __buySong(self, recv, clientSocket):
        res, message = self.__tryBuySong(recv)
        msg = {
            ServerPacketKey.TYPE: ServerTypes.USER_BUY_SONG,
            ServerPacketKey.RESULT: res,
            ServerPacketKey.ERROR: message
        }
        self.__sendPacket(msg, clientSocket)

    def __tryBuySong(self, recv):
        tableSongs = self.dataBase.getTable(DataBaseTables.SONGS,
                                            innerJoin=[DataBaseTables.USERS, UserFields.ID, SongFields.OWNER_ID],
                                            where=f"{DataBaseTables.USERS}.{UserFields.NAME} = '{recv[ClientPacketKey.AUTHOR]}' "
                                                  f"AND {DataBaseTables.SONGS}.{SongFields.NAME} = '{recv[ClientPacketKey.NAME]}'")

        res = False
        if len(tableSongs) == 0:
            message = "Песня не найдена!"
            return res, message

        tableBuySongs = self.dataBase.getTable(DataBaseTables.USER_BUY_SONG,
                                               innerJoin=[DataBaseTables.SONGS, SongFields.ID, UserBuySong.SONG_ID],
                                               where=f"{UserBuySong.USER_ID} = {recv[ClientPacketKey.ID]} AND "
                                                     f"{UserBuySong.SONG_ID} = {tableSongs[0][SongFields.ID]}")
        if len(tableBuySongs) != 0:
            message = "Песня уже в вашем списке!"
            return res, message

        songOwner = self.dataBase.getTable(DataBaseTables.SONGS,
                                           where=f"{SongFields.OWNER_ID} = {recv[ClientPacketKey.ID]} AND "
                                                 f"{SongFields.NAME} = '{recv[ClientPacketKey.NAME]}'")

        if len(songOwner) != 0:
            message = "Вы автор песни!"
            return res, message

        userBuySong = {UserBuySong.SONG_ID: tableSongs[0][SongFields.ID],
                       UserBuySong.USER_ID: recv[ClientPacketKey.ID]}
        res = self.dataBase.intoTable(DataBaseTables.USER_BUY_SONG, userBuySong)
        message = ""
        return res, message

    def __parseTags(self, tags: list) -> list:
        dataBaseTags = [tag[TagFields.NAME] for tag in self.dataBase.getTable(DataBaseTables.TAGS)]
        return [tag for tag in tags if (tag in dataBaseTags)]

    def __addTagsToSong(self, songId: int, tags: list):
        for tag in tags:
            songtotag = {SongToTagFields.SONG_ID: songId, SongToTagFields.TAG_NAME: tag}
            self.dataBase.intoTable(DataBaseTables.SONG_TO_TAG, songtotag)

    def __isExistSong(self, songName: str, userId: int) -> bool:
        return len(self.dataBase.getTable(DataBaseTables.SONGS,
                                          where=f"{SongFields.NAME} = '{songName}' AND {SongFields.OWNER_ID} = '{userId}'")) > 0

    def __proofDisconnectClient(self, clientSocket, clientAddress):
        msg = {ServerPacketKey.TYPE: ServerTypes.PROOF_DISC}
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
        self.checkEndWork()

    def closeServer(self):
        for client in self.clientSockets:
            msg = {ServerPacketKey.TYPE: ServerTypes.REQ_DISC}
            self.__sendPacket(msg, client)
        self.isWork = False

    def checkEndWork(self):
        if len(self.clientSockets) == 0 and not self.isWork:
            self.serverSocket.close()
            print('Server is closed')
