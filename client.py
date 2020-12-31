import socket
import time
from struct import *
import sys
import keyboard
from colors import bcolors as b


class Client:

    def __init__(self, team_name):
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # to get servers offer
        self.host = socket.gethostbyname(socket.gethostname())
        self.udp_port = 13117  # The same port as used by the servers
        self.team_name = team_name
        self.game_mode = False

    def start(self):  # connect UDP to get offers
        print(f"{b.OKGREEN}Client started, listening for offer requests...{b.ENDC}")
        self.udp_sock.bind((self.host, self.udp_port))

        while True:
            data, address = self.udp_sock.recvfrom(10)  # received offer
            magic_cookie, msg_type, tcp_port = unpack('Ibh', data)
            if is_valid(magic_cookie, msg_type):
                print(f"{b.HEADER}Received offer from {address[0]}, attempting to connect...{b.ENDC}")
                self.connect(address[0], tcp_port)

    def connect(self, address, tcp_port):  # connect TCP to send name and play
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # to send team name and play the game
        self.tcp_sock.connect((address, tcp_port))

        try:
            self.tcp_sock.sendall(str.encode(self.team_name + '\n'))  # send team_name
            end_time=time.time()+5
            while time.time()<end_time or self.game_mode:
                # wait for a game started message
                try:
                    start_game_msg = self.tcp_sock.recv(4096).decode('utf-8')
                except:
                    # break
                    # self.game_mode = False
                    pass
                # end_time = time.time() + 5
                if start_game_msg:
                    self.game_mode = True
                    print(f"{b.BOLD}{start_game_msg}{b.ENDC}")
                    # start_game
                    # while self.game_mode:
                    #     end_time = time.time()+5
                    while time.time() < end_time or self.game_mode:
                        c = keyboard.read_key()
                        print(f"{b.OKBLUE}read key {c}{b.ENDC}")
                        try:
                            self.tcp_sock.sendall(str.encode(c))
                            print(f"{b.OKBLUE}send {c} to the server{b.ENDC}")
                        except:
                            # break
                            # self.game_mode = False
                            # pass
                            # if self.game_mode:
                            try:
                                to_stop = self.tcp_sock.recv(1024).decode('utf-8')  # check if get stop msg from server
                                if to_stop:
                                    self.game_mode = False
                            except:
                                self.game_mode = False
                    try:
                        if self.game_mode:
                            to_stop = self.tcp_sock.recv(1024).decode('utf-8')  # check if get stop msg from server
                            if to_stop:
                                self.game_mode = False
                    except:
                        self.game_mode = False

                        print(f"{b.FAIL}connection lost{b.ENDC}")
                        #     pass

        finally:
            self.tcp_sock.close()
            print(f"{b.WARNING}Server disconnected, listening for offer requests...{b.ENDC}")


def is_valid(magic_cookie, msg_type):
    return magic_cookie == 0xfeedbeef and msg_type == 0x2


if __name__ == "__main__":
    client = Client("spam")
    client.start()
