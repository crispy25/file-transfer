import tkinter as tk
from tkinter import Tk, Frame, Button, Label, Entry, StringVar, filedialog
from network.connection_handler import ConnectionHandler

BACKGROUND_COLOR='black'
FONT_COLOR='white'
DEFAULT_PORT=9999
WIDTH=400
HEIGHT=240

class App:
    """
    This class allows for file transfer via TCP sockets using a basic GUI.
    """

    def __init__(self, connection_handler: ConnectionHandler) -> None:
        self.root = Tk()
        self.root.resizable(False, False)
        self.root.title('File transfer')
        x = self.root.winfo_screenwidth() // 2 - WIDTH // 2
        y = self.root.winfo_screenheight() // 2 - HEIGHT // 2
        self.root.geometry(f'{WIDTH}x{HEIGHT}+{x}+{y}')

        self.frame = Frame(self.root, bg=BACKGROUND_COLOR, name='main-frame')
        self.frame.pack(expand=True, fill='both')

        self.connection_handler = connection_handler
        self.socket = None

    def run(self) -> None:
        """ Start the app """
        self.pick_sender_receiver()
        self.root.mainloop()

    def connect_btn_click(self, ip: str) -> None:
        """ Connect to the given ip on user click """
        self.connection_handler.connect_to_host(self, ip, DEFAULT_PORT)

    def accept_btn_click(self, ip: str, sock) -> None:
        """ Accept the connection from the given ip on user click """
        self.connection_handler.accept_connection_from(self, sock, ip)

    def pick_sender_receiver(self) -> None:
        """ Show the UI that allows the user to pick between host and sender. """
        send_btn = Button(self.frame, text='Send file', name='send_btn',
                          width=24, height=4, command=self.show_connect_ui)
        send_btn.pack(side='left', expand=False, fill='x', padx=10)

        recv_btn = Button(self.frame, text='Receive file', name='recv_btn',
                          width=24, height=4, command=self.show_host_ui)
        recv_btn.pack(side='left', expand=False, fill='x', padx=10)

    def show_host_ui(self) -> None:
        """ Show the host UI. """
        self.frame.children['send_btn'].destroy()
        self.frame.children['recv_btn'].destroy()

        try:
            host_ip = self.connection_handler.get_host_ip()
            sock = self.connection_handler.host(host_ip, DEFAULT_PORT)
        except Exception as e:
            self.show_error(e)
            return

        conn_label = Label(self.frame, text='Enter sender ip', name='conn-label',
                           fg=FONT_COLOR, bg=BACKGROUND_COLOR, font=10)
        conn_label.pack(pady=24)

        ip_frame = Frame(self.frame, name='ip-frame', bg=BACKGROUND_COLOR)
        ip = StringVar()

        ip_entry = Entry(ip_frame, textvariable=ip, width=24, justify=tk.CENTER)
        ip_entry.grid(row=0, column=0)

        confirm_conn_label = Button(ip_frame, text='Connect',
                                    command=lambda: self.accept_btn_click(ip.get(), sock))
        confirm_conn_label.grid(row=0, column=1)
        ip_frame.pack()

    def show_connect_ui(self) -> None:
        """ Show the sender UI. """
        self.frame.children['send_btn'].destroy()
        self.frame.children['recv_btn'].destroy()

        if 'error-label' in self.root.children:
            self.root.children['error-label'].destroy()

        conn_label = Label(self.frame, text='Connect to host', name='conn-label',
                           fg=FONT_COLOR, bg=BACKGROUND_COLOR, font=10)
        conn_label.pack(pady=24)

        ip_frame = Frame(self.frame, name='ip-frame', bg=BACKGROUND_COLOR)
        ip = StringVar()

        ip_entry = Entry(ip_frame, textvariable=ip, width=24, justify=tk.CENTER)
        ip_entry.grid(row=0, column=0)

        confirm_conn_label = Button(ip_frame, text='Connect',
                                    command=lambda: self.connect_btn_click(ip.get()))
        confirm_conn_label.grid(row=0, column=1)
        ip_frame.pack()

    def show_file_ui(self) -> None:
        """ Open the file dialog and start sending the file. """
        self.frame.children['ip-frame'].destroy()
        self.frame.children['conn-label'].destroy()

        if 'error-label' in self.root.children:
            self.root.children['error-label'].destroy()

        file = filedialog.askopenfile('rb')

        if file:
            self.connection_handler.send_file(self.socket, file)

        done_label = Label(self.frame, text='File transfered succesfully',
                           fg=FONT_COLOR, bg=BACKGROUND_COLOR, font=10)
        done_label.pack(expand=True, fill='x')

    def show_transfer_ui(self) -> None:
        """ Show the file transfer status on the UI and start receiving the file. """
        self.frame.children['ip-frame'].destroy()
        self.frame.children['conn-label'].destroy()

        waiting_label = Label(self.frame, text='Waiting for file...',
                              fg=FONT_COLOR, bg=BACKGROUND_COLOR, font=10)
        waiting_label.pack(expand=True, fill='x')

        self.connection_handler.recv_file(self.socket)

        waiting_label.configure(text='File received')

    def show_error(self, error) -> None:
        """ Show the error message on the UI. """
        if 'error-label' in self.root.children:
            self.root.children['error-label'].destroy()

        error_label = Label(self.root.children['main-frame'], text=error,
                            name='error-label', foreground='red', wraplength=200)
        error_label.pack(pady=9)

        error_label.after(8500, error_label.destroy)
