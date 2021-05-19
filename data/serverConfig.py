class ServerConfig:
    IP = "127.0.0.1"
    PORT = 7777
    CODE = 'utf-8'
    BLOCK_LENGTH = 512


class ServerTypes:
    REQ_DISC = -1
    PROOF_DISC = 0
    SUCCESS_REG = 1
    SUCCESS_AUTH = 2
    ERR_REG_AUTH = 3
    ALL_SONGS = 4
    ADD_SONG = 5
    ALL_TAGS = 6
    USER_SONGS = 7
    USER_BUYING_SONGS = 8
    USER_BUY_SONG = 9


class ServerPacketKey:
    TYPE = "type"
    MESSAGE = "message"
    ERROR = "error"
    ID = "id"
    IS_STAFF = "is_staff"
    SONGS = "songs"
    AUTHORS = "authors"
    RESULT = "result"
    TAGS = "tags"
