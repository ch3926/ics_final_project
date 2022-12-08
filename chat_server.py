"""
Created on Tue Jul 22 00:47:05 2014

@author: alina, zzhang
"""

import time
import socket
import select
import sys
import string
from tkinter.messagebox import showerror
import indexer
import json
import pickle as pkl
from chat_utils import *
import chat_group as grp
import ast
import tkinter

#ash
from encryption import Encryption as ec
import random as rd
#end

class Server:
    def __init__(self):
        self.new_clients = []  # list of new sockets of which the user id is not known
        self.logged_name2sock = {}  # dictionary mapping username to socket
        self.logged_sock2name = {}  # dict mapping socket to user name
        self.all_sockets = []
        self.group = grp.Group()
        # start server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER)
        self.server.listen(5)
        self.all_sockets.append(self.server)
        # initialize past chat indices
        self.indices = {} # {person1:indexer object, person2:indexer object,...}
        # sonnet
        self.sonnet = indexer.PIndex("AllSonnets.txt")

        #ash - generate public nums
        self.base = rd.choice([2, 6])
        self.mod = 11
        self.ppns = {}
        #end

    def new_client(self, sock):
        # add to all sockets and to new clients
        print('new client...')
        sock.setblocking(0)
        self.new_clients.append(sock)
        self.all_sockets.append(sock)

    def login(self, sock):
        # read the msg that should have login code plus username
        try:
            msg = json.loads(myrecv(sock))
            if len(msg) > 0:

                if msg["action"] == "login":
                    name = msg["name"]
                    password = msg["password"]
                    
                    with open("userPasswordBank.txt") as file:
                        passBank = ast.literal_eval(file.read())
                        #print(passBank)
                    if name not in passBank or passBank[name] != password:
                        mysend(sock, json.dumps({"action": "login", "status": "failed"}))

                    elif self.group.is_member(name) != True:
                        # move socket from new clients list to logged clients
                        self.new_clients.remove(sock)

                        # add into the name to sock mapping
                        self.logged_name2sock[name] = sock
                        self.logged_sock2name[sock] = name
                        
                        # load chat history of that user
                        if name not in self.indices.keys():
                            try:
                                self.indices[name] = pkl.load(
                                    open(name + '.idx', 'rb'))
                             # if chat index doesn't exist yet
                            except IOError: 

                                # create one
                                self.indices[name] = indexer.Index(name)
                        #print(name + ' logged in')

                        self.group.join(name)
                        mysend(sock, json.dumps(
                            {"action": "login", "status": "success"}))
                    else:  # a client under this name has already logged in
                        mysend(sock, json.dumps(
                            {"action": "login", "status": "duplicate"}))
                        showerror(title="Duplicate login attempt",message="Unsuccessful login")
                else:
                    print('something went wrong')
            
            else:  # client died unexpectedly
                self.logout(sock)
        except:
            self.all_sockets.remove(sock)

    def logout(self, sock):
        # remove sock from all lists
        name = self.logged_sock2name[sock]
        pkl.dump(self.indices[name], open(name + '.idx', 'wb'))
        del self.indices[name]
        del self.logged_name2sock[name]
        del self.logged_sock2name[sock]
        self.all_sockets.remove(sock)
        self.group.leave(name)
        sock.close()

# ==============================================================================
# main command switchboard
# ==============================================================================
    def handle_msg(self, from_sock):
        # read msg code
        msg = myrecv(from_sock)
        if len(msg) > 0:
            # ==============================================================================
            # handle connect request this is implemented for you
            # ==============================================================================
            msg = json.loads(msg)
            if msg["action"] == "connect":
                to_name = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = json.dumps({"action": "connect", "status": "self"})
                # connect to the peer
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.connect(from_name, to_name)
                    the_guys = self.group.list_me(from_name)
                    msg = json.dumps(
                        {"action": "connect", "status": "success"})
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps(
                            {"action": "connect", "status": "request", "from": from_name}))
                else:
                    msg = json.dumps(
                        {"action": "connect", "status": "no-user"})
                mysend(from_sock, msg)
# ==============================================================================
# handle messeage exchange: IMPLEMENT THIS (To check: NEED TO INDEX (SENDING MESSAGES ARE FINE))
# ==============================================================================
            elif msg["action"] == "exchange":
                from_name = self.logged_sock2name[from_sock]
                """
                Finding the list of people to send to and !index message!
                """
                # IMPLEMENTATION (TEST THIS INDEXING)
                # ---- start your code ---- #
                "--> needs to use self.indices search to work"
                
                #ash
                ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
                msg_to_index = "[" + from_name + "] " + str(ctime) + " " + msg["message"]
                # self.indices[from_name].add_msg_and_index(time.strftime('%d.%m.%y,%H:%M', time.localtime()) + msg['from'] + msg['message'])
                #end

                # ---- end of your code --- #

                the_guys = self.group.list_me(from_name)[1:]
                for g in the_guys:
                    to_sock = self.logged_name2sock[g]
                    
                    # IMPLEMENTATION
                    # ---- start your code ---- #
                    # print(f"{msg=}")

                    #ash
                    g_index = self.indices[g]
                    g_index.add_msg_and_index(msg_to_index)
                    #end

                    # mysend(
                    #     to_sock, f"{msg['from']}{msg['message']}")
                    # print(f"{msg=}")

                    #ash
                    #mysend(
                    #    to_sock, json.dumps(msg))
                    mysend(to_sock, json.dumps(
                        {"action": "exchange", "from": from_name, "message": msg["message"]}))
                    #end

                    # ---- end of your code --- #

# ==============================================================================
# the "from" guy has had enough (talking to "to")!
# ==============================================================================
            elif msg["action"] == "disconnect":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                self.group.disconnect(from_name)
                the_guys.remove(from_name)
                if len(the_guys) == 1:  # only one left
                    g = the_guys.pop()
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps(
                        {"action": "disconnect", "msg": "everyone left, you are alone"}))
# ==============================================================================
#                 listing available peers: IMPLEMENT THIS (done)
# ==============================================================================
            elif msg["action"] == "list":

                # IMPLEMENTATION
                # ---- start your code ---- #
                msg = self.group.list_all()
                "...needs to use self.group functions to work"

                # ---- end of your code --- #
                mysend(from_sock, json.dumps(
                    {"action": "list", "results": msg}))
# ==============================================================================
#             retrieve a sonnet : IMPLEMENT THIS (done)
# ==============================================================================
            elif msg["action"] == "poem":

                # IMPLEMENTATION
                # ---- start your code ---- #
                sonnet_number = msg["target"]
                poem = self.sonnet.get_poem(int(sonnet_number))
                poem = "\n".join(poem)
                
                "...needs to use self.sonnet functions to work"
                print('here:\n', poem)

                # ---- end of your code --- #

                mysend(from_sock, json.dumps(
                    {"action": "poem", "results": poem}))
# ==============================================================================
#                 time
# ==============================================================================
            elif msg["action"] == "time":
                ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
                mysend(from_sock, json.dumps(
                    {"action": "time", "results": ctime}))
# ==============================================================================
#                 search: : IMPLEMENT THIS
# ==============================================================================
            elif msg["action"] == "search":

                # IMPLEMENTATION
                # ---- start your code ---- #
                "needs to use self.indices search to work"
                # print(f"{msg=}")
                
                
                search_rslt = ""
                # print(f"{self.indices=}")
                for x,y in self.indices.items():
                    # print(f"{y.msgs=}")
                    
                    add = list(set([x[1] for x in y.search(msg['target'])]))
                    if add:
                        for log in add:
                            search_rslt += log + '\n'
            
                
                print('server side search: ' + search_rslt)

                # ---- end of your code --- #
                mysend(from_sock, json.dumps(
                    {"action": "search", "results": search_rslt}))

# ==============================================================================
#                 #ash ---- num & ppn : FINAL project related
# ==============================================================================
            elif msg["action"] == "base, mod":
                mysend(from_sock, json.dumps({"action": "base, mod", "base": self.base, "mod": self.mod}))
            
            elif msg["action"] == "server ppns":
                # print(self.ppns)
                mysend(from_sock, json.dumps(
                    {"action": "server ppns", "results": self.ppns}))
            
            elif msg["action"] == "send ppn":
                name = self.logged_sock2name[from_sock]
                print(name, msg["ppn"])
                self.ppns[name] = msg["ppn"]
                # mysend(from_sock, json.dumps({"status": "success"}))
            #end
# ==============================================================================
#                 the "from" guy really, really has had enough
# ==============================================================================

        else:
            # client died unexpectedly
            self.logout(from_sock)

# ==============================================================================
# main loop, loops *forever*
# ==============================================================================
    def run(self):
        print('starting server...')
        while(1):
            read, write, error = select.select(self.all_sockets, [], [])
            print('checking logged clients..')
            for logc in list(self.logged_name2sock.values()):
                if logc in read:
                    self.handle_msg(logc)
            print('checking new clients..')
            for newc in self.new_clients[:]:
                if newc in read:
                    self.login(newc)
            print('checking for new connections..')
            if self.server in read:
                # new client request
                sock, address = self.server.accept()
                self.new_client(sock)


def main():
    server = Server()
    server.run()


if __name__ == '__main__':
    main()
