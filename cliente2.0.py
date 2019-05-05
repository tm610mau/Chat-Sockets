# -*- coding: utf-8 -*-
"""
Created on Sun May  5 01:31:46 2019

@author: Kevin Racso
"""

############################ Llamar a este archivo cliente.py ################################################

# -*- coding: utf-8 -*-

#!/usr/bin/env python3
"""Script for Tkinter GUI chat client."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter

#----Now comes the sockets part----
#HOST = input('Enter host: ')
HOST = '127.0.0.1'
PORT = 33000
#PORT = input('Enter port: ')
#if not PORT:
#    PORT = 33000
#else:
#    PORT = int(PORT)

BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode('UTF-8')
            if msg == ":q": #terminar la sesion si el cliente recibe un :q del servidor
                client_socket.close()
                #print("You have left the quantum chat")
                top.quit()
                print("You have left the quantum chat")
                #top.destroy()
            else:
                msg_list.insert(tkinter.END, msg)
        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    client_socket.send(bytes(msg, 'UTF-8'))
#    if msg == ":q":
#        client_socket.close()
#        top.quit()
#        print("You have left the quantum chat")


def on_closing(event=None):
    """This function is to be called when the window is closed."""
    my_msg.set(":q")
    send()

top = tkinter.Tk()
top.title("Quantum Chat")

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent.
#my_msg.set("Type your nickname here")
my_msg.set("Type your message here")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
#xbar = tkinter.Scrollbar(messages_frame) # scrollbar horizontal
# Following will contain the messages.
msg_list = tkinter.Listbox(messages_frame, height=20, width=90, yscrollcommand=scrollbar.set) #, xscrollcommand=xbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
#xbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
#xbar.config(command=msg_list.xview)
scrollbar.config(command=msg_list.yview)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Talk like a normal human being", command=send)
send_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)



receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop() # Starts GUI execution.