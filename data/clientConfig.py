class ClientConfig:
    HEADER = 4096
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 7777


class ClientKeyWords:
    AUTH = "auth"
    REG = "reg"
    REQ_DISC = "!exit"


class ClientTypes:
    REQ_DISC = -1
    PROOF_DISC = 0
    REG = 1
    AUTH = 2


clientKeyWordsToTypes = {
    ClientKeyWords.REG: ClientTypes.REG,
    ClientKeyWords.AUTH: ClientTypes.AUTH,
    ClientKeyWords.REQ_DISC: ClientTypes.REQ_DISC
    }


class ClientPacketKeyWords:
    TYPE = "type"
    NAME = "name"
    PASS = "password"
