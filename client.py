import socket
from struct import *
import sys


class Client:

    def __init__(self, team_name):
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # to get servers offer
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # to send team name and play the game
        self.host = socket.gethostname()
        self.udp_port = 13117  # The same port as used by the servers
        self.team_name = team_name
        self.game_mode = False

    def start(self):  # connect UDP to get offers
        print("Client started, listening for offer requests...")
        self.udp_sock.bind((self.host, self.udp_port))

        while True:
            data, address = self.udp_sock.recvfrom(7)  # received offer
            magic_cookie, msg_type, tcp_port = unpack('Ibh', data)
            if is_valid(magic_cookie, msg_type):
                print(f"Received offer from {address}, attempting to connect...")
                self.connect(address, tcp_port)

    def connect(self, address, tcp_port):  # connect TCP to send name and play
        self.tcp_sock.connect((address, tcp_port))
        try:
            self.tcp_sock.sendall(str.encode(self.team_name + '\n'))  # send team_name
            while True:
                # wait for a game started message
                start_game_msg = self.tcp_sock.recv(1024).decode('utf-8')
                if start_game_msg:
                    self.game_mode = True
                    print(start_game_msg)
                    # start_game
                    while self.game_mode:
                        c = sys.stdin.read(1)  # reads one byte at a time, similar to getchar()
                        self.tcp_sock.sendall(str.encode(c))
                        to_stop = self.tcp_sock.recv(16).decode('utf-8')  # check if get stop msg from server
                        if to_stop:
                            self.game_mode = False

        finally:
            print("Server disconnected, listening for offer requests...")


def is_valid(magic_cookie, msg_type):
    return magic_cookie == 0xfeedbeef and msg_type == 0x2


if __name__ == "__main__":
    client = Client("Cats")
    client.start()
