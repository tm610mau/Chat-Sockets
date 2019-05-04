# -*- coding: utf-8 -*-
"""
Created on Wed May  1 22:45:10 2019

@author: Kevin Racso
"""

############################ Llamar a este archivo server.py ################################################
# -*- coding: utf-8 -*- 


#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread, Lock


def welcome():
    """Dar bienvenida, a menos que se haya superado el limite de clientes."""
    while True:
        client, address = SERVER.accept()
        CONNECTIONS[client] = client
        if len(CONNECTIONS) > CLIENTLIMIT: # si se llega al limite, no darle la bienvenida
            client.send(bytes("This chat is full, begone  (type :q)", "utf8"))
        
        else:
            print("<%s:%s> has connected." % address)
            client.send(bytes("Greetings fellow humans to this totally legit human chat!", "utf8"))
            ADDRESSES [client] = address
        
        Thread(target=enter_chat, args=(client,address,)).start()
        

def enter_chat(client, address):
    """Permitir que el cliente interactue en el chat, a menos que se haya superado el limite de clientes."""

    if len(CONNECTIONS) > CLIENTLIMIT: # esperar que cierre su chat, pero no dejarlo interactuar con los demas

            CONNECTIONS.pop(client) #remover cliente de lista de conecciones
            
            while True:
                messages = client.recv(BUFFERSIZE)
                if messages == bytes(":q", 'UTF-8'):
                    client.send(bytes(":q", 'UTF-8'))
                    client.close()
                    break
    else:
        name = client.recv(BUFFERSIZE).decode('UTF-8')
        while not_unique_name(name): # chequear que el nombre no este ya en la lista
            client.send(bytes('The name %s is already taken, try again' % name , 'UTF-8'))
        
            name = client.recv(BUFFERSIZE).decode('UTF-8')
            
        NAMES[client] = name; # si es unico, agregar nombre a la lista 
        
        #saludar y preguntar al cliente por su saldo
        client.send(bytes('Welcome %s! What is your balance?' % name, 'UTF-8'))
        
        
        while True:
            
            #saludar y preguntar al cliente por su saldo
            # client.send(bytes('Welcome %s! What is your balance?' % name, 'UTF-8'))
            saldo = client.recv(BUFFERSIZE).decode('UTF-8') # K: Definir saldo
            
            try: 
                saldo_num = float(saldo)
                
                if saldo_num<0:
                
                    client.send(bytes('The balance you entered is not valid. Please enter your balance', 'UTF-8'))
                
                elif not saldo_num.is_integer():
                
                    client.send(bytes('The balance you entered is not valid. Please enter your balance', 'UTF-8'))
                
                else:
                    break
            
            except ValueError:
                
                client.send(bytes('The balance you entered is not valid. Please enter your balance', 'UTF-8'))
    

        #saldo = client.recv(BUFFERSIZE).decode('UTF-8') # K: Definir saldo
        #print(saldo)
        BALANCES[client] = int(saldo)
        client.send(bytes('The balance of %s has been set to your account' % saldo, 'UTF-8'))
        # informar a todos que llego un nuevo usuario
        broadcast(bytes("User <%s> has graced this chat with their presence" % name,'UTF-8'),client)
        
        
        while True:
            messages = client.recv(BUFFERSIZE)
            msgstring = str(messages, 'UTF-8') 
            if messages == bytes(":q", 'UTF-8'):
                
                client.send(bytes(":q", 'UTF-8'))
                client.close()
                broadcast(bytes("%s has disconnected." % name, 'UTF-8'),client)
                print("<%s:%s> has disconnected." % address)
                CONNECTIONS.pop(client)
                ADDRESSES.pop(client)
                NAMES.pop(client)
                break
            
            elif messages == bytes(":funds", 'UTF-8'):   
                client.send(bytes("You have %s dollars" % saldo, 'UTF-8'))
                
            
            #elif bytes(":t", 'UTF-8') in messages:
            elif msgstring.startswith(":t"):  
                client.send(bytes("you've done it", 'UTF-8'))
            
            #elif msgstring.startswith(":p"):
                #target = ...
                
            elif msgstring.startswith(":p - <"):       
                l = len(msgstring)
                ind = 0
                
                for i in range(6, l):
                    if msgstring[(i-1):i] == '>':
                        ind = i
                        break
                    else:
                        pass
                    
                if ind ==0:
                    client.send(bytes('Your private message does not have the format ":p - <name> - message". Please try again.', 'UTF-8'))
                    
                elif msgstring[6:(i-1)] in NAMES:
                    client.send(bytes('Weena', 'UTF-8'))
                     
                else: 
                    client.send(bytes('The nickname you entered is incorrect. Please try again.' + msgstring[6:(i-1)], 'UTF-8'))
                    print(NAMES)
                    

            
                
                
            else:
                client.send(bytes("Me :",'UTF-8') + messages)
                broadcast(messages, client, "<%s> : " % name)   
                


def broadcast(message, client, prefix=""):  # prefix is for name identification.
    """Mandar mensaje a todos los clientes"""
        
    for i in NAMES:
        if i != client:
            i.send(bytes(prefix, 'UTF-8')+message)
        
def not_unique_name(name):
    
    for i in NAMES:   
        if NAMES[i] == name: # si nombre esta en la lista, retornar False
            
            return True
        
    return False # si no esta, retornar True

mutex = Lock()

CLIENTLIMIT = 2 # limite de clientes
CONNECTIONS = {} # conecciones activas
#CLIENTS = {} #clientes
ADDRESSES = {} # dirreciones de losclientes
NAMES = {} #nombres de los clientes
BALANCES = {}

HOST = '127.0.0.1' #asumir que solo se conectara el mismo computador con si mismo
#HOST = ''
PORT = 33000
BUFFERSIZE = 1024 #numero de B maximos
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(6)
    print("Waiting connection...")
    ACCEPT_THREAD = Thread(target=welcome)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
SERVER.close()