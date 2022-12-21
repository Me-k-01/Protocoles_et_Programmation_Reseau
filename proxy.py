#!/usr/bin/python3
#Auteur: Auberval Florian, Behuiet Timothée, Siaudeau Romain
import socket, re

############### Paramètre constants ###############
IP_PROXY = '' 
PORT_PROXY = 8000
CONFIG_DOC_PATH = './configurator.html'
BLACKLIST_PATH = './wordsBlackList.txt'
CONFIG_LINK = 'config-proxy'

############### Fonctions ###############
def substr_from(str, start_str, end_str='\r\n'):
    # Trouve une chaines de caractères entre deux chaine de caractères 
    i = str.index(start_str) + len(start_str)
    str_from = str[i:]
    # L'indice de la seconde chaine en partant de la première chaîne
    j = str_from.index(end_str)
    sub_str = str_from[:j] 
    return sub_str

def rcv_all(socket) :
    res_data = b''
    size = 512

    while True:  
        reponse = socket.recv(size)
        if not reponse:  
            break
        res_data += reponse
        # Si la réponse est plus petite que la taille maximal, c'est que l'on a tout reçu
        if len(reponse) < size:  
            break

    return res_data

def parse_config(post_request):
    # Fonction qui recupère les valeurs 
    filter_status = substr_from(post_request, 'filter-status=', '&') # Est ce que le filtre doit etre actif sur les pages

    blacklist = post_request[post_request.index('blacklist=') + len('blacklist='):] 
    print(filter_status, blacklist)
    return filter_status, blacklist

def update_blacklist(filter_status, blacklist):
    # Fonction qui édite le fichier blacklist
    f = open(BLACKLIST_PATH, 'w')
    f.write(filter_status)
    f.write('\n')
    f.write(blacklist)
    f.close()

def from_url_to_chemin(request):
    lignes = request.split('\r\n') 
    G=re.compile(r"GET")
    P=re.compile(r"POST")
    
    msg_modifier=[]
    res = ""
    for line in lignes :
        if G.search(line) :#or hpps.search(line) :
            
            res = line[0:4]
            i = 13
            while True :
                if line[i] == '/' :
                    break
                i += 1
            res += line[i:]
            msg_modifier.append(res)

        elif P.search(line):

            res = line[0:5]
            i = 14
            while True :
                if(line[i] == "/") :
                    break
                i+=1
            res+=line[i:]
            msg_modifier.append(res)
        else :
            msg_modifier.append(line)

    return "\r\n".join(msg_modifier)

def faut_filtrer() :
    try :
        fichier = open(BLACKLIST_PATH,"r")
        
        ligne = fichier.readline() # ligne du booleen

        if re.search('on', ligne) :
            return True
        else :
            return False


    except Exception :
        print("erreur, pas de fichier de blacklist")
        return False


  
def filtre(request):
    doc=request.split(b"\r\n")
   
    html= doc[len(doc)-1].decode("utf-8",errors='ignore')
    try :
        fichier = open(BLACKLIST_PATH, "r")
        
        ligne = fichier.readline() # ligne du booleen
        while True :
            ligne = fichier.readline()

            if not ligne:
                break
            
            mot=re.compile(re.escape(ligne))
            html=re.sub(mot,"###",html)
    except Exception :
        print("erreur")
    
    doc[len(doc)-1] = html.encode("utf-8")
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
                if line[i]=="/" and line[i+1] != " ":
                    return False
                elif line[i]=="/" and line[i+1] == " ":
                    return True

                i += 1



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
    host_line = substr_from(request, "Host: ")

    host = host_line.split(':') 
    #TODO: ces valeurs sont là pour les test à rendre dynamique plus tard
    if request.startswith("GET"): # HTTP 
        return host[0].strip(), 80
    if request.startswith("CONNECT"): #TLS
        return host[0].strip(), int(host[1].strip()) #443
    if request.startswith("POST"):  
        return host[0].strip(), 80


def get_config_doc(): # Renvoie le document configurator.html
    #header = 'HTTP/1.1 200 OK\nContent-Type: text/html<strong>\n\n</strong>'
    header = b'HTTP/1.1 200 OK\n\n'
    file = open(CONFIG_DOC_PATH,'rb') 
    response = file.read()
    file.close()

    file = open(BLACKLIST_PATH,'rb')

    #inclusions des mots a bannir dans le textarea
    switch = file.readline()
    blacklist = b''
    while 1 :
        l = file.readline()
        if not l : break
        blacklist += l
    
    file.close()
    s = re.compile(b'<!-- BLACKLIST -->')
    c = re.compile(b'id="filter-status"')

    rep = re.sub(s, blacklist, response)
    # valeur de base que la checkbox aura suivant si on filtre ou non
    checked_value = b'checked' if re.search(b'on', switch) else b''
 
    rep = re.sub(c, b'id="filter-status"' + checked_value, rep)
    return header + rep

def read_blacklist():
    file = open(BLACKLIST_PATH, 'r')
    # On skip le premier mot
    file.readline()  

    liste_mot=[]
    while 1:
        ligne = file.readline()
        if not ligne:
            break
        ligne = ligne.replace('\n', '')
        liste_mot.append(ligne)

    file.close()
     
    return liste_mot

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
    
    #request_type = get_type(request)
    ##### NE PAS RETIRER AVANT D'AVOIR RESOLUE LE PROBLEME SVP #####
    # TODO: le client tente parfois d'actualiser la page avec une requete vide, 
    # Faut-il l'envoyer quelque pars?
    # Pour le moment on ignore ce cas. 
    if request == "":
        #print("Requête vide")
        socket_client.close()
        continue

    #print("Requête reçu: \n", request)
    print("Requête à faire: \n", msg_to_send)

    # On récupère l'ip et le port de destination 
    destination = get_host(msg_to_send) 
    print("Addresse du serveur à joindre:", destination)
    
    # Dans le cas d'un connection à config-proxy
    if destination[0] == CONFIG_LINK: 
        # Si la demande est un GET, on envoie la page web
        if request.startswith('GET'):
            # On retourne le document de parametrage du proxy 
            reponse = get_config_doc()
            socket_client.sendall(reponse)
            socket_client.close() 
            continue 
        # Si la demande est un POST, on update le filtrage
        if request.startswith('POST'):
            # TODO: traiter les updates du fichier configuration 
            print('post: ', request)
            filter_status, blacklist = parse_config(request)
            update_blacklist(filter_status, blacklist)
            socket_client.sendall(b'HTTP/1.0 200 OK\n\n')
            socket_client.close()
            continue
        # Ne reconnais pas la méthode utilisé        
        #socket_client.sendall('HTTP/1.0 200 OK\n\n')
        socket_client.close()
        continue

    # TODO: Éditions du document html, pour filtrer certains mots.
    ##### À coder içi #####
    read_blacklist()
    

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

    print(faut_filtrer())
    if html and faut_filtrer():
        reponse_filtre=filtre(reponse)
    else :
        reponse_filtre = reponse
    #print(reponse_filtre.decode("utf-8"))
    ############### Envoie au client de la réponse du serveur ###############
    socket_client.sendall(reponse_filtre)
    # Fin de la connection
    socket_client.close() 


    
ma_socket.close()
