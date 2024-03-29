"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""

import threading
from chat_utils import *
import json
import tkinter

#ash
# from encryption import Encryption as ec
# from encryption import Cipher as cp
from RSA import Cipher as cp
from RSA import RSA
import random as rd
# from random import randint as rd
#end

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.previous_state = S_OFFLINE     # In order to return to chatting state or logged in state
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s

        #ash
        self.RSA = RSA()
        self.d = self.RSA.get_d()
        self.user_type = ""
        self.peer_ppn = 0
        self.cipher = cp()
        self.server_ppns = {}
        self.shift = 0
        #end

    def get_n_e(self):
        return self.RSA.get_n_e()

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action": "connect", "target": peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with ' + self.peer + '\n'
            self.get_shift()
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = json.dumps({"action": "disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''
    
    def get_shift(self):
        try:
            mysend(self.s, json.dumps({"action": "server ppns"}))
            self.server_ppns = json.loads(myrecv(self.s))["results"]
            self.peer_n, self.peer_e = self.server_ppns[self.peer]["n"], self.server_ppns[self.peer]["e"]
            # m is private number
            self.m = rd.randint(0, self.peer_n-1)
            # c is ciphertext, public, sent to server
            self.c = (self.m ** self.peer_e) % self.peer_n
            mysend(self.s, json.dumps({"action": "send c", "c": self.c}))
            # print("shift: " + str(self.shift))
        except:
            print("something went wrong")

    def proc(self, my_msg: str, peer_msg):
        self.out_msg = ''
# ==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
# ==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            
            if len(my_msg) > 0:
                
                # All the commands
                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.previous_state = self.state
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action": "time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action": "list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.previous_state = self.state
                        self.peer = peer
                        self.state = S_CHATTING
                        self.user_type = "sender"
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'

                        # self.get_shift()
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps(
                        {"action": "search", "target": term}))
                    search_rslt = json.loads(myrecv(self.s))["results"].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps(
                        {"action": "poem", "target": poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"]
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'
                
                

                else:
                    self.out_msg += menu

            if len(peer_msg) > 0:
                try:
                    peer_msg = json.loads(peer_msg)
                except Exception as err:
                    self.out_msg += " json.loads failed " + str(err)
                    return self.out_msg

                if peer_msg["action"] == "connect":

                    # ----------your code here------(good)#
                    # print(peer_msg)
                    peer = peer_msg["from"]
                    self.peer = peer
                    self.previous_state = self.state
                    self.state = S_CHATTING
                    self.user_type = "receiver"
                    self.out_msg += 'Connect to ' + peer_msg['from'] + '. Chat away!\n\n'
                    self.out_msg += '-----------------------------------\n'
                    # self.get_shift()
                    # ----------end of your code----#

# ==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
# ==============================================================================
        elif self.state == S_CHATTING:
            # print(self.me, self.user_type)
            if self.user_type == "receiver" and self.previous_state == S_LOGGEDIN:
                # get key
                mysend(self.s, json.dumps({"action": "server ppns"}))
                self.server_ppns = json.loads(myrecv(self.s))["results"]
                self.peer_c = self.server_ppns[self.peer]["c"]
                self.n = self.get_n_e()[0]
                self.m = self.peer_c ** self.d % self.n

            if len(my_msg) > 0:     # my stuff going out (and hiding commands)
                # encrypt message
                if self.user_type == "sender":
                    self.shift = self.c
                elif self.user_type == "receiver":
                    self.shift = self.m
                ec_msg = self.cipher.encode(my_msg, self.shift)
                mysend(self.s, json.dumps(
                    {"action": "exchange", "from": "[" + self.me + "] ", "message": ec_msg}))
                
                # LEAVE THE CHAT
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
                

            if len(peer_msg) > 0:    # peer's stuff, coming in

                # ----------your code here------#
                # print(f"{type(peer_msg)} -> {peer_msg=}")
                peer_msg = json.loads(peer_msg)
                # print(peer_msg)
                if self.user_type == "sender":
                    self.shift = self.c
                elif self.user_type == "receiver":
                    self.shift = self.m
                
                if peer_msg['action'] == 'connect':
                    self.previous_state = self.state
                    self.state = S_CHATTING
                    self.out_msg += 'Connect to ' + peer_msg['from'] + '. Chat away!\n\n'
                    self.out_msg += '-----------------------------------\n'
                if peer_msg['action'] == 'exchange':
                    # get key
                    # decrypt message
                    dc_msg = self.cipher.decode(peer_msg["message"], self.shift)
                    self.out_msg += "[" + peer_msg['from'] + "] " + dc_msg
                
                elif peer_msg['action'] == 'disconnect':
                    self.disconnect()
                    # self.previous_state = self.state
                    self.state = S_LOGGEDIN
                    self.peer = ''

            self.previous_state = self.state
                # ----------end of your code----#

            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
                self.out_msg += f"Your state: {self.state}"

# ==============================================================================
# invalid state
# ==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'

        return self.out_msg

