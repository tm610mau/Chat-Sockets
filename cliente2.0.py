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

def receive_message():
    """Recibir mensajes"""
    while True:
        try:
            message = client_socket.recv(BUFSIZ).decode('UTF-8')
            if message == ":q": #terminar la sesion si el cliente recibe un :q del servidor
                client_socket.close()
                top.quit()
                print("You have left the quantum chat")
                #top.destroy()
            else:
                message_history.insert(tkinter.END, message)
        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):  # event is passed by binders.
    """Enviar mensaje al server"""
    message = client_message.get()
    client_message.set("")  # Clears input field.
    client_socket.send(bytes(message, 'UTF-8'))


def quit_chat(event=None):
    """Mandar mensaje de termino de sesion cuando se cierra la ventana"""
    client_message.set(":q")
    send() #al enviar :q, el server envia un :q de vuelta que cierra la sesion por completo

top = tkinter.Tk()
top.title("Quantum Chat")

messages_frame = tkinter.Frame(top)
client_message = tkinter.StringVar()  # For the messages to be sent.
client_message.set("Type your Username here")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
xbar = tkinter.Scrollbar(messages_frame, orient='horizontal')
#xbar = tkinter.Scrollbar(messages_frame) # scrollbar horizontal
# Following will contain the messages.
message_history = tkinter.Listbox(messages_frame, height=20, width=80, yscrollcommand=scrollbar.set, xscrollcommand=xbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
xbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
xbar.config(command=message_history.xview)
scrollbar.config(command=message_history.yview)
message_history.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
message_history.pack()
messages_frame.pack()

entry = tkinter.Entry(top, textvariable=client_message)
entry.bind("<Return>", send)
entry.pack()
button = tkinter.Button(top, text="Talk like a normal human being", command=send)
button.pack()

top.protocol("WM_DELETE_WINDOW", quit_chat)



receive_thread = Thread(target=receive_message)
receive_thread.start()
tkinter.mainloop() # Starts GUI execution.
