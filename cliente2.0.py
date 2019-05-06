############################ Llamar a este archivo cliente.py ################################################

# -*- coding: utf-8 -*-

#!/usr/bin/env python3

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter


def receive_message():
# Recibir mensajes
    while True:
        try:
            message = client.recv(BUFFERSIZE).decode('UTF-8')
            if message == "{good night}": # orden de termino de sesion
                client_message.set("You have left the chat")
                client.close()  # terminar sesion
                root.quit() #salir del tkinter
                print("You have left the quantum chat")
            
            elif message.startswith("Welcome"):
                # pedirle al cliente que escriba su balance
                client_message.set("Type your balance") 
                chat.insert(tkinter.END, message) # mantener mensajes pasados
                
            elif message == 'The balance you entered is not valid, it must be a positive integer. Please try again':
                # si se equivoca al poner el balance, poner un valor por default que sea valido
                client_message.set("0") 
                chat.insert(tkinter.END, message) # agregar a historial de mensajes
            
            else:
                chat.insert(tkinter.END, message) # agregar a historial de mensajes
                
        except OSError:  # A menos que el cliente ya haya dejado el chat
            break

def server_send(envio=None):
# Enviar mensaje al servidor
    message = client_message.get() #obtener mensaje del cliente
    client_message.set("")  # poner el textbox en blanco
    client.send(bytes(message, 'UTF-8')) # enviar al servidor


def quit_chat():
# Mandar mensaje de termino de sesion cuando se cierra la ventana
    client_message.set(":You have left the quantum chat") # mostrar mensaje que se ha ido del chat
    client_message.set(":q")
    server_send() #al enviar :q, el server envia un :q de vuelta que cierra la sesion por completo
    
    
HOST = input('Enter host: ') # Pedir al usuario que introduzca dirrecion IP del servidor

PORT = 25500 # Puerto del servidor

if not HOST:
    HOST = '127.0.0.1' #por default, asumir que se esta conectando al mismo computador


BUFFERSIZE = 1024 #numero de Bytes maximos
ADDRESS = (HOST, PORT) #Tupla de host y puerto

client = socket(AF_INET, SOCK_STREAM) # socket correspondiente al cliente
client.connect(ADDRESS) # conectar el cliente al servidor

root = tkinter.Tk() # comenzar el tkinter
root.title("Quantum Chat") #titulo del tkinter

messages_frame = tkinter.Frame(root) # marco de tkinter
client_message = tkinter.StringVar()
client_message.set("Type your Username") # pedirle al usuario que ponga su username

# barra de dezplazamiento
scrollbar = tkinter.Scrollbar(messages_frame)  # barra vertical
xbar = tkinter.Scrollbar(messages_frame, orient='horizontal') # barra horizontal
# configuraciones de las barras
chat = tkinter.Listbox(messages_frame, height=20, width=80, yscrollcommand=scrollbar.set, xscrollcommand=xbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
xbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
xbar.config(command=chat.xview)
scrollbar.config(command=chat.yview)
chat.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
chat.pack()
messages_frame.pack()

#la entrada del usuario
entry = tkinter.Entry(root, textvariable=client_message)
entry.bind("<Return>", server_send)
entry.pack()

# el boton
button = tkinter.Button(root, text="Talk like a normal human being", command=server_send)
button.pack()

root.protocol("WM_DELETE_WINDOW", quit_chat) # protocolo de termino si se cierra la ventana de forma manual

receive_thread = Thread(target=receive_message) # tomar al cliente y darle bienvenida en un thread
receive_thread.start() # comenzar el thread
tkinter.mainloop() # loop del tkinter
