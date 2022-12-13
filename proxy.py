#!/usr/bin/python3
import socket, re

IP_PROXY = 'localhost' 
PORT_PROXY = 8000

############### Fonctions ###############
def rcvall(socket) :
    rep = []

    while True :
        # socket.recv(1000) est une sortie bloquante, donc ce n'est pas une bonne solutions
        reponse = socket.recv(1000)  # TODO: trouver un moyen d'extraire l'entiereté des données d'une page web
        if not reponse : break
        rep.append(reponse)
        
    return  b''.join(rep)


def formatRequest(request):
    lignes = request.decode('utf-8').split('\r\n') 
    res = []
    for line in lignes:
        if line.startswith("Connection: keep-alive"): 
            continue
        if line.startswith("Proxy-Connection: keep-alive") :
            continue
        res.append(line)
    return '\r\n'.join(res).encode('utf-8') 

############### Set up et démarage du proxy ###############
ma_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
ma_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ma_socket.bind((IP_PROXY, PORT_PROXY))
ma_socket.listen(socket.SOMAXCONN)
print("Lancement du proxy:", IP_PROXY, ":", PORT_PROXY)

while True:
    # Attente d'une nouvelle connexion.
    socket_client, addr = ma_socket.accept() # renvoie le socket du client vers le proxy
    print ("Nouvelle connexion depuis: ", addr)

    request = socket_client.recv(1000)
    print(request)
    # Isolement de chaque partie de la reponse séparé par \r\n ,
    # pour retirer les lignes commençant par Connection:keep-alive et Proxy-connection:keep_alive .  
    #elements.remove(elements[3]) 
    #elements.remove(elements[2])  
    # On extrait l'adresse du serveur pour se connecter dessus.
    #host = re.search('(?<=: )[^\]]+', request)
    # On recompose le message à envoyer au serveur
    msg_to_send = formatRequest(request)

    print("Requête reçu: ", request.decode('utf-8'))  
    print("Requête à faire: ", msg_to_send.decode('utf-8')) 
    #print("Addresse du serveur à joindre:", host[0])
    
    # Socket du proxy vers le serveur
    socket_proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    socket_proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    #TODO: ces valeurs sont là pour les test à rendre dynamique plus tard
    socket_proxy.connect(('p-fb.net', 80)) # pour du https on utilise port: 443
    
    socket_proxy.sendall(msg_to_send)
    reponse = socket_proxy.recv(100000)
    print(reponse)
    #print("Réponse du serveur: ", reponse.decode('utf-8'))
    socket_client.sendall(reponse)
    # Fin de la connection
    socket_client.close()
    


    
ma_socket.close()
