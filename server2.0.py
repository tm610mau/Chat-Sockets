# -*- coding: utf-8 -*- 

#!/usr/bin/env python3

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread, Lock

def welcome():
# Dar bienvenida, a menos que se haya superado el limite de clientes.
    while True:
        client, address = SERVER.accept() #aceptar al cliente
        CONNECTIONS[client] = client #agregar cliente a la lista de clientes
        if len(CONNECTIONS) > CLIENTLIMIT: # si se llega al limite, no darle la bienvenida
            client.send(bytes("This chat is full, begone  (type :q)", "utf8"))
        
        else:
            print("<%s:%s> has connected." % address) #imprimir la direccion del cliente en la consola
            client.send(bytes("Greetings fellow humans to this totally legit human chat!", "utf8"))
            ADDRESSES [client] = address #agregar la dirreccion del cliente a la lista de dirrecciones
        
        Thread(target=enter_chat, args=(client,address,)).start() # darle un thread a los procesos del cliente
        

def enter_chat(client, address):
# Permitir que el cliente interactue en el chat, a menos que se haya superado el limite de clientes.

    if len(CONNECTIONS) > CLIENTLIMIT: #  no hacerle mas pregunta ni dejarlo interactuar con los demas en el chat

            CONNECTIONS.pop(client) # remover cliente de lista de conecciones
            
            while True: #esperar que cierre su ventana
                messages = client.recv(BUFFERSIZE) # recibir mensajes del cliente
                if messages == bytes(":q", 'UTF-8'): # mensaje del cliente para cerrar la ventana
                    client.send(bytes(":q", 'UTF-8')) # mandar la orden que el cliente cierre su ventana
                    client.close() # cerrar el socket del cliente
                    break
    else:
        name = client.recv(BUFFERSIZE).decode('UTF-8') # recibir mensajes del cliente
        while check_name(name): # chequear que el nombre no este ya en la lista
            client.send(bytes('The name %s is already taken, try again' % name , 'UTF-8'))
        
            name = client.recv(BUFFERSIZE).decode('UTF-8') # pedirle que introduzca otro nombre
            
        NAMES[client] = name; # si es unico, agregar nombre de usuario a la lista 

        #saludar y preguntar al cliente por su saldo
        client.send(bytes('Welcome %s! What is your balance?' % name, 'UTF-8'))
        
        saldo = ask_saldo(client) # Preguntar y recibir el balance del usuario

        BALANCES[client] = saldo # agregar saldo a la lista de blanaces
        client.send(bytes('The balance of %s has been set to your account' % saldo, 'UTF-8'))
        
        # informar a todos que llego un nuevo usuario
        broadcast(bytes("User <%s> has graced this chat with their presence" % name,'UTF-8'),client)
        
        while True:
            messages = client.recv(BUFFERSIZE) # recibir mensajes del cliente
            msgstring = str(messages, 'UTF-8')  # version string del mensaje del usuario
            saldo = BALANCES[client] # refrescar el saldo en cada iteracion
            
            client.send(bytes("Me: ",'UTF-8') + messages) # devolver el mensaje al usuario sin importar contenido
            
            if messages == bytes(":q", 'UTF-8'): # cerrar sesion
                
                # quitar al cliente y sus atributos de las listas respectivas
                remove_client(client, name, address) # quitar al cliente de la lista
                
                break # ir al termino del programa
            
            elif messages == bytes(":funds", 'UTF-8'):   # ver fondos
                
                client.send(bytes("You have %s dollars" % saldo, 'UTF-8')) #mostrar saldo al usuario
            
            elif messages == bytes(":u", 'UTF-8'): # mandar mensaje privado
                
                usernames_list(client) #entregar lista de usuarios
                
            elif msgstring.startswith(":p"): # enviar mensajes privados
                
                private_message(client, msgstring, name)

            elif msgstring.startswith(":t - <"): #transferencia
                
                # revisar sintaxis de msgstring, si check es falso, no esta el usuario
                check, identifier, string_amount = check_transfer(msgstring, client) #
                
                if check and try_check_balance(check, client, identifier):
                
                    try: 
                        int(string_amount) # probar que el amonto sea un entero
                        
                        if int(string_amount)>0:
                            transfer(client, name, string_amount, identifier) #realizar transferencia
                       
                        else:
                            client.send(bytes('The amount is not a valid number for transfering', 'UTF-8'))
                            
                    except ValueError:
                        
                        client.send(bytes('The amount is not a valid number for transfering', 'UTF-8'))

            else: 
            
                msgstring =  replace_emojis(msgstring)  # Reemplazar emojis (si existen)       
                messages = bytes(msgstring, 'UTF-8') # retransformar string a bytes
                broadcast(messages, client, "<%s> : " % name)  # desplegar el mensaje a todos los demas

def check_name(name):
# Revisar si name esta en la lista de nombres
    
    for i in NAMES:   
        if NAMES[i] == name: # si nombre esta en la lista, retornar True
            
            return True
        
    return False # si no esta, retornar False

def ask_saldo(client):
# Entregar el saldo del cliente, solo si el input del cliente es un saldo valido
    
    while True:
        saldo = client.recv(BUFFERSIZE).decode('UTF-8') # recibir el input del cliente como saldo
        
        try: 
            saldo = float(saldo) # transformar a float
                
            if saldo<0 or not saldo.is_integer(): # dar error si es un entero negativo
                
                client.send(bytes('The balance you entered is not valid, it must be a positive integer. Please try again', 'UTF-8'))
                
            else:
                break
            
        except ValueError:
                
            client.send(bytes('The balance you entered is not valid, it must be a positive integer. Please try again', 'UTF-8'))
            
    return int(saldo)

def usernames_list(client):
# Entregar lista de usuarios por linea
    
    client.send(bytes("Currently active users:", 'UTF-8')) 
    
    for i in NAMES:   
        client.send(bytes('<' + NAMES[i] + '>', 'UTF-8')) #sumar el nombre de usuario a la lista
        
def private_message(client, msgstring, name):
# revisar sintaxis y enviar el mensaje privado si lo cumple
    
    if msgstring.startswith(":p - <"):
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
            client.send(bytes('The username you entered is incorrect. Please try again.', 'UTF-8'))
                     
        elif msgstring[ind+1:ind+4] != ' - ': # formato incorrecto
            client.send(bytes('Your private message does not have the format ":p - <name> - message". Please try again.', 'UTF-8'))
                
        else: # enviar mensaje privado a destinatario
            dest = names_client(msgstring[6:ind]) # direccion destinatario
            pmsg = msgstring[ind+4:] # mensaje
            pmsg = replace_emojis(pmsg) # reemplazar emojis
            dest.send(bytes('<'+str(name)+'> (private): '+str(pmsg), 'UTF-8'))
            client.send(bytes('Private message: "' +str(pmsg) +'" has been sent to : '+'<'+str(name)+'> ', 'UTF-8'))
            

    else:
        client.send(bytes('Your private message does not have the format ":p - <name> - message". Please try again.', 'UTF-8'))

def replace_emojis(msgstring):
# Reemplazar los emojis dentro de msgstring
    
    msgstring = msgstring.replace(':sad', ':(')
    msgstring = msgstring.replace(':smile', ':)')
    msgstring = msgstring.replace(':confused', ':S')
    msgstring = msgstring.replace(':angry', '>:(')
 
    return msgstring

def check_transfer(msgstring, client):
# Revisar la sintaxis del mensaje de transferencia
    
    check = False #salida por deafult
    identifier = '' #salida por deafult
    string_amount = ''  #salida por deafult
    
    if not msgstring.startswith(":t - <"): # revisar que comience con :t - < 
        client.send(bytes('The transference does not have the format ":t - <name> - amount". Please try again.', 'UTF-8'))
    else:  
    
        ident_start = 6 #indice del inicio del identificador
        ident_end = msgstring.find('>',ident_start ) #buscar final del identificador
                
        if ident_start < -1 or ident_end <= ident_start: # si no se encontro '<' o si '>' esta antes de '<'
            client.send(bytes('The transference does not have the format ":t - <name> - amount". Please try again.', 'UTF-8'))
                
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
                    check = True # permitir que siga la transferencia
                    
    return check, identifier, string_amount 

def try_check_balance(check, client, identifier):
# Ver si el cliente identifier tiene un balance asociado
    if not check:
        return False
    
    dest = names_client(identifier) # ver el cliente destino de la transaccion
  
    if str(BALANCES.get(dest)) == 'None': # si el diccionario de balances no tiene el indice de la persona buscada
        client.send(bytes('The user: %s does not have a balance yet' %identifier, 'UTF-8'))
        return False

    return True # si funciona bien
    
def transfer(client, name, string_amount, identifier): 
# Realizar transferencia
    
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
# Buscar indice correspondiente al cliente que tiene como nombre identifier    
    
    for client in NAMES:   
        if NAMES[client] == identifier: # retorna el cliente que tiene el identificador
            
            return client
        
    return -1 # si no esta, retornar -1


def broadcast(message, client, prefix=""):  
# Mandar mensaje a todos los clientes
        
    for i in NAMES:
        if i != client:
            i.send(bytes(prefix, 'UTF-8')+message)
        
def remove_client(client, name, address):
# cerrar sesion del cliente y quitar sus atributos de las listas
    
    client.send(bytes("{good night}", 'UTF-8')) # mandar la orden que el cliente cierre su ventana
    client.close()
    broadcast(bytes("%s has disconnected." % name, 'UTF-8'),client)
    print("<%s:%s> has disconnected." % address)
    # quitar todos los atributos asociados al clientes en los diccionarios respectivos
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
PORT = 25500 #Puerto del servidor
BUFFERSIZE = 1024 #numero de Bytes maximos
ADDR = (HOST, PORT) #Tupla de host y puerto

SERVER = socket(AF_INET, SOCK_STREAM) # crear el socket del servidor
SERVER.bind(ADDR) # enlazar el servidor con el address

if __name__ == "__main__":
    SERVER.listen(6) # estar atento a solicitudes de conexion
    print("Waiting connection...")
    ACCEPT_THREAD = Thread(target=welcome) # tomar al cliente y darle bienvenida en un thread
    ACCEPT_THREAD.start() # comenzar el thread
    ACCEPT_THREAD.join() # esperar a que termine el thread y enterrarlo
SERVER.close()
