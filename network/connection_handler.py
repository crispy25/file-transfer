from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from threading import Thread
from io import BytesIO, SEEK_SET, SEEK_END
from shutil import disk_usage

NOT_CONNECTED=0
CONNECTED=1
CONNECTING=2

class ConnectionHandler:
    """ 
    Handler for basic networking acions.
    """

    def __init__(self) -> None:
        self.connection = {'status' : NOT_CONNECTED}

    def host(self, ip: str, port: int) -> socket:
        """ Host and listen on IP:PORT. Returns created socket. """
        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind((ip, port))
        sock.settimeout(10)
        sock.listen()
        return sock

    def accept_connection_from(self, app, sock: socket, ip: str) -> None:
        """ Accept connection from IP. """

        def wait_for_connection(app, sock: socket, ip: str) -> None:
            try:
                conn, addr = sock.accept()
                if addr[0] == ip:
                    app.socket = conn
                    app.show_transfer_ui()
                    self.connection['status'] = CONNECTED
            except Exception as e:
                self.connection['status'] = NOT_CONNECTED
                app.show_error("Couldn't connect to sender: " + str(e))

        if self.connection['status'] != CONNECTING:
            self.connection['status'] = CONNECTING
            thread = Thread(target=wait_for_connection, args=(app, sock, ip))
            thread.start()

    def connect_to_host(self, app, ip: str, port: int) -> None:
        """ Connect to IP:PORT. """

        def wait_for_connection(app, ip: str, port: int) -> None:
            try:
                app.socket = socket(AF_INET, SOCK_STREAM)
                app.socket.connect((ip, port))
                app.show_file_ui()
                self.connection['status'] = CONNECTED
            except Exception as e:
                self.connection['status'] = NOT_CONNECTED
                app.show_error("Couldn't connect to receiver: " + str(e))

        if self.connection['status'] != CONNECTING:
            self.connection['status'] = CONNECTING
            thread = Thread(target=wait_for_connection, args=(app, ip, port))
            thread.start()

    def get_host_ip(self) -> str:
        """ Get the IP of the host. """
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.connect(('8.8.8.8', 1))
        ip = sock.getsockname()[0]
        sock.close()
        return ip

    def send_file(self, sock: socket, file) -> None:
        """ Send the file to the receiver. """
        file_name: str = file.name.split('/')[-1]
        file.seek(0, SEEK_END)
        size = file.tell()
        file.seek(0, SEEK_SET)

        # send name length
        length = len(file_name)
        data_to_send = length.to_bytes(16, 'little')
        sock.sendall(data_to_send)

        # send name
        sock.sendall(file_name.encode())

        # send file size
        data_to_send = size.to_bytes(16, 'little')
        sock.sendall(data_to_send)

        while True:
            bytes_sent = sock.sendfile(file)
            if bytes_sent == 0:
                break

        sock.close()

    def recv_file(self, sock: socket) -> None:
        """ Receive the file and write it on disk. """

        def recv_n_bytes(sock: socket, bytes_to_recv: int) -> bytes:
            buf = BytesIO()

            while bytes_to_recv:
                data = sock.recv(bytes_to_recv)
                if not data:
                    break
                buf.write(data)
                bytes_to_recv -= len(data)

            return buf.getvalue()

        file_name_length = int.from_bytes(recv_n_bytes(sock, 16), 'little')
        file_name = recv_n_bytes(sock, file_name_length).decode()
        file_size = int.from_bytes(recv_n_bytes(sock, 16), 'little')

        _, _, free_space = disk_usage('.')
        if file_size > free_space:
            raise Exception('Not enough space to receive the file')

        with open(file_name, 'wb+') as out:
            while True:
                data = sock.recv(1024)

                if not data:
                    break

                out.write(data)

        sock.close()
