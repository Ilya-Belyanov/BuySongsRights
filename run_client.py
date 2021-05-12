from src.obj.client import Client
from data.clientConfig import ClientConfig

if __name__ == '__main__':
    client = Client(ClientConfig)
    client.run()
