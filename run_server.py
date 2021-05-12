from src.obj.server import Server
from data.serverConfig import ServerConfig

if __name__ == '__main__':
    server = Server(ServerConfig)
    server.run()
