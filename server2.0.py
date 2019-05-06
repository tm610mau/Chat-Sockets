# -*- coding: utf-8 -*-
"""
Created on Sun May  5 01:31:24 2019
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
        while check_name(name): # chequear que el nombre no este ya en la lista
            client.send(bytes('The name %s is already taken, try again' % name , 'UTF-8'))
        
            name = client.recv(BUFFERSIZE).decode('UTF-8')
            
        NAMES[client] = name; # si es unico, agregar nombre a la lista 
        
        #saludar y preguntar al cliente por su saldo
        client.send(bytes('Welcome %s! What is your balance?' % name, 'UTF-8'))
        
        saldo = ask_saldo(client)
        
        saldo = int(saldo)
        BALANCES[client] = saldo
        client.send(bytes('The balance of %s has been set to your account' % saldo, 'UTF-8'))
        
        # informar a todos que llego un nuevo usuario
        broadcast(bytes("User <%s> has graced this chat with their presence" % name,'UTF-8'),client)
        
        while True:
            messages = client.recv(BUFFERSIZE)
            msgstring = str(messages, 'UTF-8') 
            BALANCES.update()
            saldo = BALANCES[client] # reinicializae el saldo en cada iteracion
            
            client.send(bytes("Me: ",'UTF-8') + messages)
            
            if messages == bytes(":q", 'UTF-8'): # quit
                
                # quitar al cliente y sus atributos de las listas respectivos
                remove_client(client, name, address)
                break
            
            elif messages == bytes(":funds", 'UTF-8'):   # ver fondos
                
                client.send(bytes("You have %s dollars" % saldo, 'UTF-8')) #mostrar saldo al usuario
            
            elif messages == bytes(":u", 'UTF-8'):
                
                client.send(bytes("Currently active users:", 'UTF-8'))
                
                usernames_list(client) #entregar lista de usuarios
                
            elif msgstring.startswith(":p - <"): # enviar mensajes privados
                l = len(msgstring)
                ind = 0
                
                for i in range(6, l):
                    if msgstring[i:i+1] == '>': # revisar formato
                        ind = i
                        break
                    else:
                        pass
                    
                if ind == 0: # formato incorrecto
                    client.send(bytes('Your private message does not have the format ":p - <name> - message". Please try again.', 'UTF-8'))
                    
                elif names_client(msgstring[6:ind]) == -1: # destinatario no existe
                    #client.send(bytes('Weena', 'UTF-8'))
                    client.send(bytes('The nickname you entered is incorrect. Please try again.', 'UTF-8'))
                     
                elif msgstring[ind+1:ind+4] != ' - ': # formato incorrecto
                    client.send(bytes('Your private message does not have the format ":p - <name> - message". Please try again.', 'UTF-8'))
                
                else: # enviar mensaje privado a destinatario
                    dest = names_client(msgstring[6:ind]) # direccion destinatario
                    #dest_name = NAMES[dest]
                    pmsg = msgstring[ind+4:] # mensaje
                    pmsg = pmsg.replace(':sad', ':(')
                    pmsg = pmsg.replace(':smile', ':)')
                    pmsg = pmsg.replace(':confused', ':S')
                    pmsg = pmsg.replace(':angry', '>:(')
                    dest.send(bytes('<'+str(name)+'> (private): '+str(pmsg), 'UTF-8'))
                    #print(NAMES)
                    #dest = names_client(msgstring[6:(i-1)])
                    #dest.send(bytes(msgstring[6:(i-1)], 'UTF-8'))
                
            #elif msgstring.startswith(":p"): # una solicidud mensaje privado incompleto
             #   client.send(bytes('''Your private message does not have the format ":p - <name> - message". Please try again.''', 'UTF-8'))

            elif msgstring.startswith(":t - <"): #transferencia
                
                #chequear sintaxis de msgstring
                check, identifier, string_amount = check_transfer(msgstring, client) 
                if check:
                    try: 
                        int(string_amount) # probar que el amonto sea un entero
                        
                        if int(string_amount)>0:
                            transfer(client, name, string_amount, identifier) #realizar transferencia
                       
                        else:
                            client.send(bytes('The amount is not a valid number for transfering', 'UTF-8'))
                            
                    except ValueError:
                        
                        client.send(bytes('The amount is not a valid number for transfering', 'UTF-8'))

            elif msgstring.startswith(":t"): # una solicidud de transferencia incompleta
                client.send(bytes('''The transference does not have the format ":t - <name> - message". Please try again.''', 'UTF-8'))
            
            else: 
                # desplegar el mensaje a todos los demas
                msgstring = msgstring.replace(':sad', ':(')
                msgstring = msgstring.replace(':smile', ':)')
                msgstring = msgstring.replace(':confused', ':S')
                msgstring = msgstring.replace(':angry', '>:(')
                messages = bytes(msgstring, 'UTF-8')
                broadcast(messages, client, "<%s> : " % name)  

def broadcast(message, client, prefix=""):  # prefix is for name identification.
    """Mandar mensaje a todos los clientes"""
        
    for i in NAMES:
        if i != client:
            i.send(bytes(prefix, 'UTF-8')+message)
        
def check_name(name):
    """Revisar si name esta en la lista de nombres"""
    
    for i in NAMES:   
        if NAMES[i] == name: # si nombre esta en la lista, retornar True
            
            return True
        
    return False # si no esta, retornar False

def ask_saldo(client):
    
    while True:
        saldo = client.recv(BUFFERSIZE).decode('UTF-8') # K: Definir saldo
        
        try: 
            saldo_num = float(saldo)
                
            if saldo_num<0 or not saldo_num.is_integer():
                
                client.send(bytes('''The balance you entered is not valid, it must be a positive Integer. Please try again''', 'UTF-8'))
                
            else:
                break
            
        except ValueError:
                
            client.send(bytes('The balance you entered is not valid. Please enter your balance', 'UTF-8'))
            
    return saldo

def usernames_list(client):
    """Entregar lista de usuarios por linea""" 
    
    for i in NAMES:   
        client.send(bytes('<' + NAMES[i] + '>', 'UTF-8')) #sumar el nombre de usuario a la lista
        
def check_transfer(msgstring, client):
    """Revisar la sintaxis del mensaje de transferencia"""
    
    check = False #salida por deafult
    identifier = '' #salida por deafult
    string_amount = ''  #salida por deafult
    
    ident_start = 6 #indice del inicio del identificador
    ident_end = msgstring.find('>',ident_start ) #buscar final del identificador
                
    if ident_start < -1 or ident_end <= ident_start: # si no se encontro '<' o si '>' esta antes de '<'
        client.send(bytes('''The transference does not have the format ":t - <name> - amount". Please try again.''', 'UTF-8'))
                
    else:
        identifier = msgstring[ident_start:ident_end] # identificación del usuario al que se quiere transferir
                    
        if not check_name(identifier): # si no esta en el chat
            client.send(bytes('The user: %s is not on the chat' %identifier, 'UTF-8'))
            
        else:
            amount_start = msgstring.find('-',ident_end)+2 # indice inicial del monto
                    
            if amount_start < 1: # si el indice encontrad es menor a (-1 +2) 
                client.send(bytes('The transference you requested is incorrect. Please try again', 'UTF-8'))
                
            else: 
                string_amount = msgstring[amount_start:] # string de monto a transferir
                check = True
                
    return check, identifier, string_amount 

def transfer(client, name, string_amount, identifier): 
    """Realizar transferencia """
    
    amount = int(string_amount)
    mutex.acquire() # poner mutex (candado)
    
    saldo = BALANCES[client] #revisar el balance dentro del mutex (por si alguien le entrego dinero justo antes)
        
    if saldo < amount:
        client.send(bytes('You do not have enough money for the transaction', 'UTF-8'))
                                
    else:    
        target = names_client(identifier) # ver el cliente destino de la transaccion
                                    
        BALANCES[target] += amount # dar dinero al target
        target.send(bytes('%s has transferred you ' %name + string_amount, 'UTF-8'))
                                    
        BALANCES[client] -= amount # quitar el dinero al cliente
        client.send(bytes('You have succesfully transferred %s to ' %amount + identifier, 'UTF-8'))
            
    mutex.release() # liberar el candado
    
        
def names_client(identifier):
    """Buscar indice correspondiente al cliente que tiene como nombre identifier """
    
    for client in NAMES:   
        if NAMES[client] == identifier: # retorna el cliente que tiene el identificador
            
            return client
        
    return -1 # si no esta, retornar -1
        
def remove_client(client, name, address):
    
    client.send(bytes(":q", 'UTF-8'))
    client.close()
    broadcast(bytes("%s has disconnected." % name, 'UTF-8'),client)
    print("<%s:%s> has disconnected." % address)
    CONNECTIONS.pop(client)
    ADDRESSES.pop(client)
    NAMES.pop(client)
    BALANCES.pop(client)

mutex = Lock()

CLIENTLIMIT = 6 # limite de clientes
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
