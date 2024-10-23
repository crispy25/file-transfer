from network.connection_handler import ConnectionHandler
from app.app import App

app = App(ConnectionHandler())

if __name__ == '__main__':
    app.run()
