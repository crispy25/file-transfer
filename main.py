from network.connection_handler import ConnectionHandler
from ui.app import App

app = App(ConnectionHandler())

if __name__ == '__main__':
    app.run()
