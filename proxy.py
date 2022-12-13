#!/usr/bin/python3
import socket, re

IP_PROXY = '0.0.0.0' 
PORT_PROXY = 80

############### Fonctions ###############
def rcvall(socket) :
    rep = []

    while True :
        reponse = socket.recv(1000)
        if not reponse : break
        
        rep.append(reponse)
    
    reponse = b''.join(rep)
    return reponse


############### Set up et démarage du proxy ###############
ma_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
ma_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ma_socket.bind((IP_PROXY, PORT_PROXY))
ma_socket.listen(socket.SOMAXCONN)
print("Lancement du proxy:", IP_PROXY, ":", PORT_PROXY)

# Attente d'une nouvelle connexion
while True:
    socket_client, addr = ma_socket.accept()
    print ("Nouvelle connexion depuis: ", addr)
    
    # request = client_co.recv(1000).decode()
    request = socket_client.recv(1000).decode('utf-8')
    
    # Isolement de chaque partie de la reponse séparé par \r\n pour retirer les lignes commençant par Connection:keep-alive et Proxy-connection:keep_alive    
    elements = request.split('\r\n')
    elements.remove(elements[3]) #elements.remove("Connection: Keep-Alive") 
    elements.remove(elements[2]) #elements.remove("Proxy-Connection: Keep-Alive")  

    # On extrait l'adresse du serveur pour se connecter dessus
    host = re.search('(?<=: )[^\]]+', elements[2])
    # On recompose le message à envoyer au serveur
    msg_to_send = '\r\n'.join(elements).encode('utf-8') 

    
    
    print("Requête reçu: ", request)  
    print("Requête à faire: ", elements) 
    #print(host[0])
    
    socket_proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    socket_proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    #TODO: ces valeurs sont là pour les test à rendre dynamique plus tard
    socket_proxy.connect(('p-fb.net', 443))
    
    socket_proxy.sendall(msg_to_send)
    reponse = rcvall(socket_proxy)
    
    #print("Réponse du serveur: ", reponse.decode())
    socket_client.sendall(reponse)
    socket_client.close()
    


    
ma_socket.close()
