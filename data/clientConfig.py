class ClientConfig:
    HEADER = 4096
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 7777


class ClientCommand:
    AUTH = "auth"
    REG = "reg"
    ALL_SONGS = "all songs"
    ADD_SONG = "add song"
    ALL_TAGS = "all tags"
    MY_SONGS = "my songs"
    BUY_SONG = "buy song"
    BUYING_SONGS = "buying songs"
    REQ_DISC = "!exit"
    HELP = "help"


class ClientTypes:
    REQ_DISC = -1
    PROOF_DISC = 0
    REG = 1
    AUTH = 2
    ALL_SONGS = 3
    ADD_SONG = 4
    ALL_TAGS = 5
    MY_SONGS = 6
    BUYING_SONGS = 7
    BUY_SONG = 8


clientKeyWordsToTypes = {
    ClientCommand.REG: ClientTypes.REG,
    ClientCommand.AUTH: ClientTypes.AUTH,
    ClientCommand.REQ_DISC: ClientTypes.REQ_DISC,
    ClientCommand.ALL_SONGS: ClientTypes.ALL_SONGS
    }


class ClientPacketKey:
    TYPE = "type"
    NAME = "name"
    PASS = "password"
    ID = "id"
    TAGS = "tags"
    AUTHOR = "author"
