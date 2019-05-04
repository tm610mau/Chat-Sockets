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
        while check_name(name): # chequear que el nombre no este ya en la lista
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
                
                if saldo_num<0 or not saldo_num.is_integer():
                
                    client.send(bytes('The balance you entered is not valid. Please enter your balance', 'UTF-8'))
                
                else:
                    break
            
            except ValueError:
                
                client.send(bytes('The balance you entered is not valid. Please enter your balance', 'UTF-8'))
    

        #saldo = client.recv(BUFFERSIZE).decode('UTF-8') # K: Definir saldo
        saldo = int(saldo)
        BALANCES[client] = saldo
        client.send(bytes('The balance of %s has been set to your account' % saldo, 'UTF-8'))
        # informar a todos que llego un nuevo usuario
        broadcast(bytes("User <%s> has graced this chat with their presence" % name,'UTF-8'),client)
        
        
        while True:
            messages = client.recv(BUFFERSIZE)
            msgstring = str(messages, 'UTF-8') 
            BALANCES[client] = saldo # reinicializae el saldo en cada iteracion
            
            if messages == bytes(":q", 'UTF-8'):
                
                client.send(bytes(":q", 'UTF-8'))
                client.close()
                broadcast(bytes("%s has disconnected." % name, 'UTF-8'),client)
                print("<%s:%s> has disconnected." % address)
                CONNECTIONS.pop(client)
                ADDRESSES.pop(client)
                NAMES.pop(client)
                BALANCES.pop(client)
                break
            
            elif messages == bytes(":funds", 'UTF-8'):   
                client.send(bytes("You have %s dollars" % saldo, 'UTF-8'))
                
            
            elif msgstring.startswith(":t"):#transferencia
                
                client.send(bytes("Me: ",'UTF-8') + messages)
                ident_start = msgstring.find('<') + 1 #buscar inicio del identificador
                ident_end = msgstring.find('>') #buscar final del identificador
                if ident_start < -1 or ident_end <= ident_start: # si no se encontro '<' o si '>' esta antes
                    client.send(bytes('The transference you requested is not valid', 'UTF-8'))
                else:
                    identifier = msgstring[ident_start:ident_end] # identificación del usuario al que se quiere transferir
                    
                    if not check_name(identifier):
                        client.send(bytes('The user: %s is not on the chat' %identifier, 'UTF-8'))
                    else:
                        amount_start = msgstring.find('-',ident_end)+2 # indice inicial del monto
                    
                        if amount_start < 1: # si el indice encontrad es menor a (-1 +2) 
                            client.send(bytes('The transference you requested is not valid', 'UTF-8'))
                        else: 
                            string_amount = msgstring[amount_start:] # string de monto a transferir
                            #transfer(client, name, string_amount, identifier)
                            try: 
                                amount = int(string_amount)
                                
                                if saldo < amount:
                                    client.send(bytes('You do not have enough money for the transaction', 'UTF-8'))
                                else:    
                                    mutex.acquire()
                                    target = names_client(identifier)
                                    saldo_ident = BALANCES[target]
                                    saldo_ident += amount
                                    BALANCES[target] = saldo_ident
                                    target.send(bytes('%s has transferred you ' %name + string_amount, 'UTF-8'))
                                    saldo -= amount
                                    client.send(bytes('You have succesfully transferred %s to ' %amount + identifier, 'UTF-8'))
                                    mutex.release()
                                    
                            except ValueError:
                                client.send(bytes('The balance  is not valid for transfering', 'UTF-8'))

                                                
            #elif msgstring.startswith(":p"):
                #target = ...
                
            #elif msgstring.startswith(":p - <Identifier> - "):
                
            elif msgstring.startswith(":x"):
                mutex.acquire()
                target = names_client('a')
                saldo_ident = BALANCES[target]
                saldo_ident += 1000
                BALANCES[target] = saldo_ident
                client.send(bytes("%s" % saldo_ident,'UTF-8'))
                mutex.release()
            
            else:
                client.send(bytes("Me: ",'UTF-8') + messages)
                broadcast(messages, client, "<%s> : " % name)   
                


def broadcast(message, client, prefix=""):  # prefix is for name identification.
    """Mandar mensaje a todos los clientes"""
        
    for i in NAMES:
        if i != client:
            i.send(bytes(prefix, 'UTF-8')+message)
        
def check_name(name):
    
    for i in NAMES:   
        if NAMES[i] == name: # si nombre esta en la lista, retornar True
            
            return True
        
    return False # si no esta, retornar False

#def transfer(client, name, string_amount, identifier):
#    try: 
#        amount = int(string_amount)
#        saldo = BALANCES[client]
#        if saldo < amount:
#            client.send(bytes('You do not have enough money for the transaction', 'UTF-8'))
#        else:    
#            target = name_index(identifier)
#            saldo_ident = BALANCES[target]
#            saldo_ident += amount
#            target.send(bytes('%s has transferred you ' %name + string_amount, 'UTF-8'))
#            saldo -= amount
#            client.send(bytes('You have succesfully transferred %s to ' %amount + identifier, 'UTF-8'))

#    except ValueError:
#        client.send(bytes('The balance  is not valid for transfering', 'UTF-8'))
        
def names_client(identifier):
    
    for client in NAMES:   
        if NAMES[client] == identifier: # retorna el cliente que tiene el identificador
            
            return client
        
    return -1 # si no esta, retornar -1
        

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
