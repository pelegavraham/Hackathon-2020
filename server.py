import socket
from socket import *
from struct import *
import sys, time
import _thread
from random import randint


class Server:
    def __init__(self):
        self.udp_sock = socket(AF_INET, SOCK_DGRAM)
        self.tcp_sock = socket(AF_INET, SOCK_STREAM)
        self.host = gethostname()
        self.clients_socket = {}
        self.clients_counter = {}
        self.port = 13117  # the same port as used by the clients
        self.group1 = []
        self.group2 = []

    def start(self):
        print("Server started, listening on IP address ", self.host)
        self.udp_sock.bind((self.host, self.port))  # bind the socket to the port
        self.send_offers()

    def send_offers(self):
        # send UDP broadcast packets
        self.udp_sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        data = pack('Ibh', 0xfeedbeef, 0x2, 22)  # what is the port for the TCP connection ?
        start_time = time.time()
        t_end = time.time() + 10  # during 10 seconds send broadcasts
        while time.time() < t_end:
            self.udp_sock.sendto(data, ('<broadcast>', self.port))
            self.tcp_sock.bind((self.host, 22))
            self.tcp_sock.listen(5)  # Listen for incoming connections
            while True:  # TODO - define timeout
                # wait for a connection
                client_socket, client_address = self.tcp_sock.accept()
                _thread.start_new_thread(self.get_team_name_and_enter_to_group, (client_socket, client_address))
                break
            left_time = (time.time() - start_time)
            if left_time < 1:   # every second
                time.sleep(1 - left_time)

        for cs in self.clients_socket:
            self.send_start_game_msg(cs)

        start_game_time = time.time()
        while time.time()-start_game_time < 10:
            for team_name, client_socket in self.clients_socket: # do multithreading
                while True:  # TODO - define timeout
                    data = client_socket.recv(1)  # can extend to do manipulate on the data
                    self.clients_counter[team_name] += 1

        end_msg = self.calc_groups_counter()
        print(end_msg)
        for team_name, client_socket in self.clients_socket:
            client_socket.close()

    def get_team_name_and_enter_to_group(self, client_socket, address):
        while True:  # TODO - define timeout
            team_name = client_socket.recv(1024)
            self.clients_socket[team_name] = client_socket
            self.clients_counter[team_name] = 0
            if team_name:
                k = randint(0, 1)
                if k == 0:
                    self.group1.append(team_name)
                else:
                    self.group2.append(team_name)
            else:
                break

    def send_start_game_msg(self, client_socket):
        start_game_msg = f"Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n====\n{arr_to_str(self.group1)}\nGroup 2:\n====\n{arr_to_str(self.group2)}\nStart pressing keys on your keyboard as fast as you can!!"
        client_socket.sendall(str.encode(start_game_msg))

    def calc_groups_counter(self):
        group1_count = 0
        group2_count = 0
        for team_name, count in self.clients_counter:
            if team_name in self.group1:
                group1_count += count
            else:
                group2_count += count
        winner_group = "Group 1" if group1_count >= group2_count else "Group 2"
        winner_teams = arr_to_str(self.group1) if group1_count >= group2_count else arr_to_str(self.group2)
        return f"Game over!\nGroup 1 typed in {group1_count} characters. Group 2 typed in {group2_count} characters.\n{winner_group} wins!\nCongratulations to the winners:\n==\n{winner_teams}"


def arr_to_str(arr):
    s = ""
    for x in arr:
        s = s + x + "\n"
    return s


if __name__ == "__main__":
    server = Server()
    server.start()
