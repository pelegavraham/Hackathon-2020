import socket
import time
from struct import *
import keyboard
from colors import bcolors as b


class Client:

    def __init__(self, team_name):
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # to get servers offer
        self.host = socket.gethostbyname(socket.gethostname())
        self.udp_port = 13117  # The same port as used by the servers
        self.team_name = team_name
        self.game_mode = False
        self.port = 0

    def start(self):  # connect UDP to get offers
        print(f"{b.OKGREEN}Client started, listening for offer requests...{b.ENDC}")
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_sock.bind((self.host, self.udp_port))

        while True:

            try:
                data, address = self.udp_sock.recvfrom(10)  # received offer
                magic_cookie, msg_type, tcp_port = unpack('Ibh', data)
                if is_valid(magic_cookie, msg_type) and address[1] != self.port:
                    print(f"{b.HEADER}Received offer from {address[0]}, attempting to connect...{b.ENDC}")
                    self.port = address[1]
                    self.connect(address[0], tcp_port)
            except:
                print(f"{b.FAIL}failed to connect..{b.ENDC}")

    def connect(self, address, tcp_port):  # connect TCP to send name and play
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # to send team name and play the game
        self.tcp_sock.connect((address, tcp_port))

        try:
            self.tcp_sock.sendall(str.encode(self.team_name + '\n'))  # send team_name
            try:
                start_game_msg = self.tcp_sock.recv(4096).decode('utf-8')
            except:
                pass

            self.tcp_sock.setblocking(False)
            if start_game_msg:
                self.game_mode = True
                print(f"{b.BOLD}{start_game_msg}{b.ENDC}")

                first = True
                while self.game_mode:
                    try:
                        c = keyboard.read_key()
                        if first:
                            print(f"\n{b.OKBLUE}read key {c}{b.ENDC}")
                            try:
                                self.tcp_sock.sendall(str.encode(c))
                                print(f"{b.OKBLUE}send {c} to the server{b.ENDC}")
                            except:
                                print(f"{b.FAIL}Connection problems{b.ENDC}")
                                self.game_mode=False
                            first=False
                        else:
                            first=True

                    except:
                        pass
                    try:
                        to_stop = self.tcp_sock.recv(1024).decode('utf-8')  # check if get stop msg from server
                        if to_stop:
                            print(to_stop)
                            self.game_mode = False
                            self.port = 0
                    except:
                        pass

        finally:
            self.tcp_sock.close()
            self.game_mode = False
            print(f"{b.WARNING}Server disconnected, listening for offer requests...{b.ENDC}")


def is_valid(magic_cookie, msg_type):
    return magic_cookie == 0xfeedbeef and msg_type == 0x2


if __name__ == "__main__":
    client = Client("spam")
    client.start()
