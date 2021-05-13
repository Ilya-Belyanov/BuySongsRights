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


class ServerPacketKeyWords:
    TYPE = "type"
    MESSAGE = "message"
    ID = "id"
