import socket
import time
from struct import *
import sys

import keyboard


class Client:

    def __init__(self, team_name):
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # to get servers offer
        self.host = socket.gethostbyname(socket.gethostname())
        self.udp_port = 13117  # The same port as used by the servers
        self.team_name = team_name
        self.game_mode = False

    def start(self):  # connect UDP to get offers
        print("Client started, listening for offer requests...")
        self.udp_sock.bind((self.host, self.udp_port))

        while True:
            data, address = self.udp_sock.recvfrom(10)  # received offer
            print("recieve....")
            magic_cookie, msg_type, tcp_port = unpack('Ibh', data)
            if is_valid(magic_cookie, msg_type):
                print(f"Received offer from {address[0]}, attempting to connect...")
                self.connect(address[0], 5050)

    def connect(self, address, tcp_port):  # connect TCP to send name and play
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # to send team name and play the game
        self.tcp_sock.connect((address, tcp_port))

        try:
            self.tcp_sock.sendall(str.encode(self.team_name + '\n'))  # send team_name
            end_time=time.time()+10
            while time.time() < end_time:
                # wait for a game started message
                print("want start msg..")
                start_game_msg = self.tcp_sock.recv(4096).decode('utf-8')
                print(start_game_msg)
                if start_game_msg:
                    self.game_mode = True
                    print(start_game_msg)
                    # start_game
                    # while self.game_mode:
                    end_time = time.time()+10
                    while time.time() < end_time:
                        c = keyboard.read_key()
                        # c = sys.stdin.read(1)  # reads one byte at a time, similar to getchar()
                        self.tcp_sock.sendall(str.encode(c))
                        to_stop = self.tcp_sock.recv(16).decode('utf-8')  # check if get stop msg from server
                        if to_stop:
                            self.game_mode = False

        finally:
            self.tcp_sock.close()
            print("Server disconnected, listening for offer requests...")


def is_valid(magic_cookie, msg_type):
    return magic_cookie == 0xfeedbeef and msg_type == 0x2


if __name__ == "__main__":
    client = Client("Cats")
    client.start()
