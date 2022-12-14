#!/usr/bin/python3
import socket

IP_PROXY = 'localhost' 
PORT_PROXY = 8000

############### Fonctions ###############
'''def rcvall(socket) :
    rep = []

    while True :
        # socket.recv(1000) est une sortie bloquante, donc ce n'est pas une bonne solutions
        reponse = socket.recv(1000)  # TODO: trouver un moyen d'extraire l'entiereté des données d'une page web
        if not reponse : break
        rep.append(reponse)
        
    return  b''.join(rep)
'''

def format_request(request):
    # Isolement de chaque partie de la reponse séparé par \r\n ,
    lignes = request.split('\r\n') 
    res = []
    for line in lignes:
        # pour retirer les lignes commençant par Connection:keep-alive et Proxy-connection:keep_alive .  
        if line.startswith("Connection: keep-alive"): 
            continue
        if line.startswith("Proxy-Connection: keep-alive") :
            continue
        if line.startswith("Accept-Encoding: gzip") :
            continue
        res.append(line)
    return '\r\n'.join(res)

def get_host(request):
    #firstLine = request.partition('\n')[0]
    #host = re.search('(?<=: )[^\]]+', firstLine) 
    # trouver la ligne "Host: ip:port"
    i = request.index("Host: ") + 5 
    host_line = request[i:]
    host_line = host_line[:host_line.index("\r\n")]

    host = host_line.split(':') 
    #TODO: ces valeurs sont là pour les test à rendre dynamique plus tard
    if request.startswith("GET"): # HTTP 
        return (host[0].strip(), 80)
    if request.startswith("CONNECT"): #TLS
        return (host[0].strip(), int(host[1].strip())) #443

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

    request = socket_client.recv(10000).decode('utf-8')  
    # On recompose le message à envoyer au serveur
    msg_to_send = format_request(request)
    # On extrait l'adresse du serveur et le port pour se connecter dessus. 

    # TODO: le client tente parfois d'actualiser la page avec une requete vide, 
    # il faut donc trouver un moyen de garder la destination.
    # Pour le moment on ignore ce cas.
    if (request == ""):
        print("Requête vide")
        socket_client.close()
        continue

    print("Requête reçu: ", request)  
    print("Requête à faire: ", msg_to_send)  
    destination = get_host(msg_to_send) 
    print("Addresse du serveur à joindre:", destination)
    
    # Socket du proxy vers le serveur
    socket_proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    socket_proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_proxy.connect(destination)  
    
    socket_proxy.sendall(msg_to_send.encode('utf-8'))
    reponse = socket_proxy.recv(1000000000) # Le nombre est tres grands pour des grosses pages comme p-fb.net
    #print("Réponse du serveur: ", reponse.decode('utf-8'))
    socket_client.sendall(reponse)
    # Fin de la connection
    socket_client.close()
    


    
ma_socket.close()
