#!/usr/bin/python3
#Auteur: Auberval Florian, Behuiet Timothée, Siaudeau Romain
import socket, re

IP_PROXY = '' 
PORT_PROXY = 8000
CONFIG_DOC_PATH = './configurator.html'

############### Fonctions ###############
def rcv_all(socket) :
    res_data = b''
    size = 512

    while True:  
        reponse = socket.recv(size) #.decode('utf-8') 
        #socket.sendall(b'')
        if not reponse:  
            break
        res_data += reponse
        # Si la réponse est plus petite que la taille maximal, c'est que l'on a tout reçu
        if len(reponse) < size:  
            break

    return res_data




def from_url_to_chemin(request):
    lignes = request.split('\r\n') 
    G=re.compile(r"GET")
    P=re.compile(r"POST")
    
    msg_modifier=[]
    res=""
    for line in lignes :
        if G.search(line) :#or hpps.search(line) :
            
            res=line[0:4]
            i=13
            while True :
                if(line[i] == "/") :
                    break
                i+=1
            res+=line[i:]
            msg_modifier.append(res)

        elif P.search(line):

            res=line[0:5]
            i=14
            while True :
                if(line[i] == "/") :
                    break
                i+=1
            res+=line[i:]
            msg_modifier.append(res)
        else :
            msg_modifier.append(line)

    return "\r\n".join(msg_modifier)


  
def filtre(request) :


    doc=request.split(b"\r\n")
   
    html= doc[len(doc)-1].decode("utf-8",errors='ignore')
    try :
        fichier=open("./wordsBlackList.txt","r")
        
      
        while True :

            ligne = fichier.readline()

            if not ligne:
                break
            
            mot=re.compile(re.escape(ligne))

            html=re.sub(mot,"###",html)
    except Exception :
        print("erreur")
    
    doc[len(doc)-1]=html.encode("utf-8")
    reponse = b"\r\n".join(doc)

    return reponse
        
        
def cible_html (request):
    lignes = request.split('\r\n') 
    G=re.compile(r"GET")
    P=re.compile(r"POST")
    
   
    for line in lignes :
        if G.search(line) or P.search(line):#or hpps.search(line) :
            i=0
            while 1 :
                if(line[i]=="/" and line[i+1]!=" " ):
                    return False
                elif(line[i]=="/" and line[i+1]==" " ):
                    return True
                i+=1

        
        

           
                



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
    #print("request: ", request)
    i = request.index("Host: ") + 5 
    host_line = request[i:]
    host_line = host_line[:host_line.index("\r\n")]

    host = host_line.split(':') 
    #TODO: ces valeurs sont là pour les test à rendre dynamique plus tard
    if request.startswith("GET"): # HTTP 
        return host[0].strip(), 80
    if request.startswith("CONNECT"): #TLS
        return host[0].strip(), int(host[1].strip()) #443
    if request.startswith("POST"):  
        return host[0].strip(), 80

def get_type(request):
    if(request.startswith("GET")):
        return "GET"
    if(request.startswith("POST")):
        return "POST"
    if(request.startswith("CONNECT")):
        return "CONNECT"

def get_config_doc(): # Renvoie le document configurator.html
    #header = 'HTTP/1.1 200 OK\nContent-Type: text/html<strong>\n\n</strong>'
    header = b'HTTP/1.1 200 OK\n\n'
    #response = "HTTP/1.1 200 OK\n\n<html><head><title>Configuration</title><style>textarea{resize:none;}</style></head>\n<h1 style=\"text-align=center\">Changer votre liste de mot a filtrer</h1><br/><form method=\"post\"><textarea rows=\"4\" cols=\"50\"></textarea><br/><button type=\"submit\">Valider</button></form></html>"
    file = open(CONFIG_DOC_PATH,'rb') 
    response = file.read()
    file.close()

    return header + response

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
    
    request_type = get_type(request)
    #On recupère le type de la requête entre GET, POST et CONNECT pour pouvoir effectuer les traitements adéquats dessus
    #print(request_type)
    #if (request_type):
    #    if(request_type[0] == 'GET'):
    #        print("c'est du get")
    ##### NE PAS RETIRER AVANT D'AVOIR RESOLUE LE PROBLEME SVP #####
    # TODO: le client tente parfois d'actualiser la page avec une requete vide, 
    # Faut-il l'envoyer quelque pars?
    # Pour le moment on ignore ce cas. 
    if request == "":
        #print("Requête vide")
        socket_client.close()
        continue

    #print("Requête reçu: ", request)
    #print("Requête à faire: ", msg_to_send)

    # On récupère l'ip et le port de destination 
    destination = get_host(msg_to_send) 
    #print("Addresse du serveur à joindre:", destination)
    
    # Dans le cas d'un connection à config-proxy
    if (destination[0] == 'config-proxy'): 
        # On retourne le document de parametrage du proxy 
        reponse = get_config_doc()
        socket_client.sendall(reponse)
        socket_client.close()
        # TODO: traiter les updates du fichier configuration
        continue 
    
    # TODO: Éditions du document html, pour filtrer certains mots.
    ##### À coder içi #####

    ############### Transmition de la requête au serveur ###############
    # Socket du proxy vers le serveur
    socket_proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    socket_proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_proxy.connect(destination)
    # Envoie de la requête au serveur 
    msg = from_url_to_chemin(msg_to_send)
    html = cible_html(msg)
    #print(msg)
   
    socket_proxy.sendall(msg.encode('utf-8'))  
 
    
    ############### Réception de la réponse du serveur ###############
    reponse = rcv_all(socket_proxy)  
    #reponse=socket_proxy.recv(36000)
    #print("Taille de la réponse du serveur: ",len(reponse))

    if html :
        reponse_filtre=filtre(reponse)
    else :
        reponse_filtre=reponse
    #print(reponse_filtre.decode("utf-8"))
    ############### Envoie au client de la réponse du serveur ###############
    socket_client.sendall(reponse_filtre)
    # Fin de la connection
    socket_client.close() 


    
ma_socket.close()
