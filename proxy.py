#!/usr/bin/python3
import socket

IP_PROXY = '' 
PORT_PROXY = 8000

############### Fonctions ###############
"""
def recv_and_send(socket_src, socket_dest):
    size = 1024
    reponse = b'' 

    while len(reponse) < size :  
        reponse = socket_src.recv(size)  
 
        if not reponse: 
            return
        socket_dest.send(reponse) 
"""
     
def rcv_all(socket) :
    res_data = b''
    size = 4096 

    while True:  
        reponse = socket.recv(size) #.decode('utf-8') 
        if not reponse: 
            break
        res_data += reponse
        # Si la réponse est plus petite que la taille maximal, c'est que l'on a tout reçu
        if len(reponse) < size: 
            break 
 
    #print("Resultat :", res_data.decode('utf-8'))
    return res_data


def format_request(request):
    # Isolement de chaque partie de la reponse séparé par \r\n ,
    lignes = request.split('\r\n') 
    res = []
    for line in lignes:
        # pour retirer les lignes commençant par Connection:keep-alive et Proxy-connection:keep_alive .  
        if (line.startswith("Connection: keep-alive") or 
            line.startswith("Proxy-Connection: keep-alive") or
            line.startswith("Accept-Encoding: gzip")) :
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

def get_type(s):
    reg="[a-zA-Z]+ "
    type_co=re.search(reg, s)
    return type_co[0].rsplit()

def page_config():
    reponse="HTTP/1.1 200\n\n<html><head><title>Configuration</title><style>textarea{resize:none;}</style></head>\n<h1 style=\"text-align=center\">Changer votre liste de mot a filtrer</h1><br/><form method=\"post\"><textarea rows=\"4\" cols=\"50\"></textarea><br/><button type=\"submit\">Valider</button></form></html>"
    return reponse.encode()

############### Set up et démarage du proxy ###############
ma_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
ma_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ma_socket.bind((IP_PROXY, PORT_PROXY))
ma_socket.listen(socket.SOMAXCONN)
print("Lancement du proxy:", IP_PROXY, ":", PORT_PROXY)

while True:
    ############### Attente d'une nouvelle connexion. ###############
    socket_client, addr = ma_socket.accept() # renvoie le socket du client vers le proxy
    print ("Nouvelle connexion depuis: ", addr)

    ############### Formatage de la requête ###############
    request = socket_client.recv(10000).decode('utf-8')  
    # On recompose le message à envoyer au serveur
    msg_to_send = format_request(request)
    # On extrait l'adresse du serveur et le port pour se connecter dessus. 
    
    #On recupère le type de la requête entre GET, POST et CONNECT pour pouvoir effectuer les traitements adéquats dessus
    lignes = request.split('\r\n')
    '''x=get_type(lignes[0])
    print(x)'''
    # TODO: le client tente parfois d'actualiser la page avec une requete vide, 
    # Faut-il l'envoyer quelque pars?
    # Pour le moment on ignore ce cas.
    if request == "":
        print("Requête vide")
        socket_client.close()
        continue

    # print("Requête reçu: ", request)
    # print("Requête à faire: ", msg_to_send)

    # On récupère l'ip et le port de destination
    destination = get_host(msg_to_send) 
    print("Addresse du serveur à joindre:", destination)
    
    if(destination[0]=='config-proxy'):
        # TODO: Éditions du document html, pour filtrer certains mots.
        ##### À coder içi #####
        reponse=page_config()
    else:
    ############### Transmition de la requête au serveur ###############
    # Socket du proxy vers le serveur
        socket_proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        socket_proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_proxy.connect(destination)
    # Envoie de la requête au serveur
        socket_proxy.sendall(msg_to_send.encode('utf-8'))  

    ############### Réception de la réponse du serveur ###############
    # reponse = rcv_all(socket_proxy)
    # TODO: Ce n'est pas une bonne pratique d'utiliser un trop gros nombre, trouver une meilleur implémentation.
        reponse = socket_proxy.recv(1000000000) # Le nombre est tres grands pour des grosses pages comme p-fb.net
        print("Taille de la réponse du serveur: ", len(reponse))

    ############### Envoie au client de la réponse du serveur ###############
    socket_client.sendall(reponse)
    
    # Fin de la connection
    socket_client.close()
    


    
ma_socket.close()
