import socket
from socket import *
from struct import *
import sys, time
from random import randint
import threading
from colors import bcolors as b
start_game_time = 0


class Server:
    def __init__(self):
        self.udp_sock = socket(AF_INET, SOCK_DGRAM)
        self.tcp_sock = socket(AF_INET, SOCK_STREAM)
        self.udp_sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.udp_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        self.host = gethostbyname(gethostname())
        self.tcp_sock.bind((self.host, 2126))
        self.tcp_sock.listen(1)  # Listen for incoming connections

        self.clients_socket = {}
        self.clients_counter = {}
        self.chars={}
        self.port = 13117  # the same port as used by the clients
        self.group1 = []
        self.group2 = []

        self.best_score=0
        self.best_team=''
        self.most_common_letter=''

    def start(self):
        print(f"{b.OKGREEN}Server started, listening on IP address{b.ENDC}", self.host)
        while True:
            self.clients_socket = {}
            self.clients_counter = {}
            self.group1 = []
            self.group2 = []
            self.send_offers()

    def send_offers(self):
        # send UDP broadcast packets

        data = pack('Ibh', 0xfeedbeef, 0x2, 2126)  # what is the port for the TCP connection ?
        start_time = time.time()
        t_end = time.time() + 10  # during 10 seconds send broadcasts

        while time.time() < t_end:
            thread = threading.Thread(target=self.send_broadcast, args=(data, t_end))
            thread.start()

            self.tcp_sock.settimeout(10)
            try:
                client_socket, client_address = self.tcp_sock.accept()
                print(f"{b.HEADER}one connection is active {client_address}....{b.ENDC}")
                thread1 = threading.Thread(target=self.get_team_name_and_enter_to_group,
                                          args=(client_socket, client_address))
                thread1.start()
                left_time = (time.time() - start_time)
                if 0 < left_time < 1:  # every second
                    time.sleep(1 - left_time)

            except:
                pass

        for team_name in self.clients_socket:
            cs = self.clients_socket[team_name]
            self.send_start_game_msg(cs)

        global start_game_time
        start_game_time = time.time()
        while thread.is_alive():
            continue
        # while thread1.is_alive():
        #     continue
        i = len(self.clients_socket)-1
        end_time=time.time()+10
        for team_name in self.clients_socket:  # do multithreading
            # if t_end>time.time():

            client_socket = self.clients_socket[team_name]
            thread2 = threading.Thread(target=self.recieve_char, args=(client_socket, team_name, time.time()+10))
            thread2.start()
            if i==0:
                while thread2.is_alive() and end_time>time.time():
                    continue
            i-=1
            # else:
            # else:
            #     break


        end_msg = self.calc_groups_counter()
        print(f"{b.BOLD}{end_msg}{b.ENDC}")

        for team_name in self.clients_socket:
            client_socket = self.clients_socket[team_name]
            client_socket.sendall(str.encode(end_msg))
            print(f"send end msg to client {client_socket}")

    # =============================================================================================================== #

    def send_broadcast(self, data, t_end):
        while time.time() < t_end:
            self.udp_sock.sendto(data, ('<broadcast>', self.port))
            print(f"{b.OKBLUE}send broadcast...{b.ENDC}")
            time.sleep(1)

    def recieve_char(self, client_socket, team_name, end_time):
        while time.time() < end_time:
            client_socket.settimeout(10)
            try:
                data = client_socket.recv(1).decode('utf-8')
                print(f'{b.OKBLUE}got msg: ' + data + f'{b.ENDC}')

                if data:
                    if team_name in self.clients_socket:
                        self.clients_counter[team_name] += 1
                        self.chars[team_name]+=data
                    # else:
                    #     print("something went wrong on server.recieve_char")
            except:
                pass

    def get_team_name_and_enter_to_group(self, client_socket, address):
        team_name = client_socket.recv(1024).decode('utf-8')
        team_name = team_name[:-1]
        print(team_name)
        self.clients_socket[team_name] = client_socket
        self.clients_counter[team_name] = 0
        self.chars[team_name] = ''

        if team_name:
            k = randint(0, 1)
            if k == 0:
                self.group1.append(team_name)
            else:
                self.group2.append(team_name)

    def send_start_game_msg(self, client_socket):
        start_game_msg = f"Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n====\n{arr_to_str(self.group1)}\nGroup 2:\n====\n{arr_to_str(self.group2)}\nStart pressing keys on your keyboard as fast as you can!!"
        client_socket.sendall(str.encode(start_game_msg))

    def calc_groups_counter(self):
        group1_count = 0
        group2_count = 0
        for team_name in self.clients_counter:
            count = self.clients_counter[team_name]
            if team_name in self.group1:
                group1_count += count
            else:
                group2_count += count
        winner_group = "Group 1" if group1_count >= group2_count else "Group 2"
        winner_teams = arr_to_str(self.group1) if group1_count >= group2_count else arr_to_str(self.group2)
        if group1_count>self.best_score:
            self.best_score=group1_count
            self.best_team="Group 1"
        if group2_count>self.best_score:
            self.best_score = group2_count
            self.best_team = "Group 2"
        letters={}
        for team_name in self.chars:
            for c in self.chars[team_name]:
                if c not in letters:
                    letters[c]=0
                letters[c]+=1
        amount=0
        for c in letters:
            if letters[c]>amount:
                self.most_common_letter=c
                amount=letters[c]
        return f"Game over!\nGroup 1 typed in {group1_count} characters. Group 2 typed in {group2_count} characters.\n" \
               f"{winner_group} wins!\nCongratulations to the winners:\n==\n{winner_teams}\n ============= Some Statistics ============\n\n" \
               f"The best score ever is {self.best_score} by the team {self.best_team}\nThe most common letter that appears is {self.most_common_letter}, which shows {amount} times\n"


def arr_to_str(arr):
    s = ""
    for x in arr:
        s = s + x + "\n"
    return s


if __name__ == "__main__":
    server = Server()
    server.start()
