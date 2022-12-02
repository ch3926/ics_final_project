#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 13:36:58 2021

@author: bing
"""

# import all the required  modules
import threading
import select
from tkinter import *
from tkinter import font
from tkinter import ttk
from chat_utils import *
import json
from tkinter.messagebox import showerror, showinfo
import ast

# GUI class for the chat


class GUI:
    # constructor method
    def __init__(self, send, recv, sm, s):
        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()
        self.send = send
        self.recv = recv
        self.sm = sm
        self.socket = s
        self.my_msg = ""
        self.system_msg = ""

    def login(self):
        # login window
        self.login = Toplevel()

        # set the title
        self.login.title("Login")
        self.login.resizable(width=False,
                             height=False)
        self.login.configure(width=400,
                             height=300)

        # create a Label for log in prompt
        self.pls = Label(self.login,
                         text="Please login to continue",
                         justify=CENTER,
                         font="Helvetica 14 bold")

        self.pls.place(relheight=0.15,
                       relx=0.2,
                       rely=0.07)
        # create a Label for user name
        self.labelName = Label(self.login,
                               text="Name: ",
                               font="Helvetica 12")

        self.labelName.place(relheight=0.2,
                             relx=0.1,
                             rely=0.2)

        # create a entry box for typing the message
        self.entryName = Entry(self.login,
                               font="Helvetica 14")

        self.entryName.place(relwidth=0.4,
                             relheight=0.12,
                             relx=0.35,
                             rely=0.2)

        # set the focus of the curser
        self.entryName.focus()


#------------------------- our extension - password system ------------------------#

        # create a label for for password prompting
        self.labelPassword = Label(self.login,
                               text="Password: ",
                               font="Helvetica 12")

        # password label settings
        self.labelPassword.place(relheight=0.2,
                             relx=0.1,
                             rely=0.4)

        # create an entry box for password
        self.entryPass = Entry(self.login,
                               font="Helvetica 14")

        # Entry widget settings
        self.entryPass.place(relwidth=0.4,
                             relheight=0.12,
                             relx=0.35,
                             rely=0.4)

        # set cursor focus
        self.entryName.focus()


        # create a Log in button
        # along with action
        self.Login = Button(self.login,
                         text="LOG IN",
                         font="Helvetica 14 bold",
                         command=lambda: self.goAhead(self.entryName.get(), self.entryPass.get()))
        
        # create a sign up button
        self.signUp = Button(self.login,
                         text="SIGN UP",
                         font="Helvetica 14 bold",
                         
                         # instead of calling "self.goAhead", call our custom function "self.sign_up"
                         command=lambda: self.sign_up(self.entryName.get(), self.entryPass.get()))

        self.Login.place(relx=0.1,
                      rely=0.55)
        self.signUp.place(relx=0.7,
                      rely=0.55)
        self.Window.mainloop()

        

    def goAhead(self, name, password):

        # now time check for both name and password before proceeding
        if len(name) and len(password):

            # dump in name and password
            msg = json.dumps({"action": "login", "name": name, "password": password})
            self.send(msg)

            # grab the response
            response = json.loads(self.recv())

            # if status or response returns "success"
            if response["status"] == 'success':
                self.login.destroy()
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(name)
                self.layout(name)
                self.textCons.config(state=NORMAL)
                # self.textCons.insert(END, "hello" +"\n\n")
                self.textCons.insert(END, menu + "\n\n")
                self.textCons.config(state=DISABLED)
                self.textCons.see(END)
                # while True:
                #     self.proc()
            
            # if failed to login, show an error message
            elif response['status'] == 'failed':
                showerror(title="Login Failed", message="Incorrect username or password.")
                return

        # the thread to receive messages
            process = threading.Thread(target=self.proc)
            process.daemon = True
            process.start()

    #------------------------- custom function - "sign_up" ------------------------#

    def sign_up(self, name, password):
        """
        When "sign up" button/widget is pressed, this event 
        controls the process of signing up and keeping records of past sign ups
        """
        with open("userPasswordBank.txt") as f:

            # passBank dict
            passBank: dict = ast.literal_eval(f.read())
        
        # don't allow duplicate usernames or passwords (for simplicity)
        if name in passBank.keys() or password in passBank.values():
            showerror(title="Login failed", message="Username or Password is already in use.")
            return # don't execute next part

        # if not caught by above check, execute below
        with open("userPasswordBank.txt", "w") as f:
            
            # store name: password pair into password bank txt file for later use
            passBank[name] = password
            f.write(str(passBank))
        
        # disply a success message
        showinfo(title="You have successfully signed up", message="Click 'Log in' to enter the chat room!")

    # The main layout of the chat
    def layout(self, name):

        self.name = name
        # to show chat window
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width=True,
                              height=True)
        self.Window.configure(width=900,
                              height=800,
                              bg="#17202A")
        self.labelHead = Label(self.Window,
                               bg="#17202A",
                               fg="#EAECEE",
                               text=self.name,
                               font="Helvetica 13 bold",
                               pady=5)

        self.labelHead.place(relwidth=1)
        self.line = Label(self.Window,
                          width=450,
                          bg="#ABB2B9")

        self.line.place(relwidth=1,
                        rely=0.07,
                        relheight=0.012)

        self.textCons = Text(self.Window,
                             width=20,
                             height=2,
                             bg="#17202A",
                             fg="#EAECEE",
                             font="Helvetica 14",
                             padx=5,
                             pady=5)

        self.textCons.place(relheight=0.745,
                            relwidth=1,
                            rely=0.08)

        self.labelBottom = Label(self.Window,
                                 bg="#ABB2B9",
                                 height=80)

        self.labelBottom.place(relwidth=1,
                               rely=0.825)

        self.entryMsg = Entry(self.labelBottom,
                              bg="#2C3E50",
                              fg="#EAECEE",
                              font="Helvetica 13")

        # place the given widget
        # into the gui window
        self.entryMsg.place(relwidth=0.74,
                            relheight=0.06,
                            rely=0.008,
                            relx=0.011)

        self.entryMsg.focus()

        # create a Send Button
        self.buttonMsg = Button(self.labelBottom,
                                text="Send",
                                font="Helvetica 10 bold",
                                width=20,
                                bg="#ABB2B9",
                                command=lambda: self.sendButton(self.entryMsg.get()))

        self.buttonMsg.place(relx=0.77,
                             rely=0.008,
                             relheight=0.06,
                             relwidth=0.22)
        
        

        self.textCons.config(cursor="arrow")

        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)

        # place the scroll bar
        # into the gui window
        scrollbar.place(relheight=1,
                        relx=0.974)

        scrollbar.config(command=self.textCons.yview)

        self.textCons.config(state=DISABLED)

    # function to basically start the thread for sending messages

    def sendButton(self, msg):
        # self.textCons.config(state=DISABLED)
        self.my_msg = msg
        # print(msg)
        self.entryMsg.delete(0, END)
        self.textCons.config(state=NORMAL)
        self.textCons.insert(END, msg + "\n")
        self.textCons.config(state=DISABLED)
        self.textCons.see(END)

    def proc(self):
        # print(self.msg)
        while True:
            read, write, error = select.select([self.socket], [], [], 0)
            peer_msg = []
            # print(self.msg)
            if self.socket in read:
                peer_msg = self.recv()
            if len(self.my_msg) > 0 or len(peer_msg) > 0:
                # print(self.system_msg)
                self.system_msg = self.sm.proc(self.my_msg, peer_msg)
                self.my_msg = ""
                self.textCons.config(state=NORMAL)
                self.textCons.insert(END, self.system_msg + "\n\n")
                self.textCons.config(state=DISABLED)
                self.textCons.see(END)

    def run(self):
        self.login()


# create a GUI class object
if __name__ == "__main__":
    g = GUI()
