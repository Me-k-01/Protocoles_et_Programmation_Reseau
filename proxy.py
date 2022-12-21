#!/usr/bin/python3
#Auteur: Auberval Florian, Behuiet Timothée, Siaudeau Romain

import socket, re
from urllib import parse # Pour décoder les requetes post de la pars du configurateur

############### Paramètre constants ###############
IP_PROXY = '' 
PORT_PROXY = 8000
CONFIG_DOC_PATH = './configurator.html'
BLACKLIST_PATH = './wordsBlackList.txt'
CONFIG_LINK = 'config-proxy'


############### Fonctions ###############
# Trouve une chaines de caractères entre deux chaine de caractères 
def substr_from(str, start_str, end_str='\r\n'): 
    i = str.index(start_str) + len(start_str) # début de chaine
    str_from = str[i:]
    # L'indice de la seconde chaine en partant de la première chaîne
    j = str_from.index(end_str) # fin de chaine

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
 

# Fonction qui recupère les valeurs d'une requete POST, dans le cadre du configurateur.
def parse_config(post_request): 
    filter_status = "filter-status=on" in post_request # Est ce que le filtre doit etre actif sur les pages ?
    blacklist = post_request[post_request.index('blacklist=') + len('blacklist='):] # Liste des mots a bannir
    # On doit convertir la valeur, qui est encodé sous un format spécial de HTML
    blacklist = parse.unquote(blacklist)

    return filter_status, blacklist

# Fonction qui édite le fichier blacklist
def update_blacklist(filter_status, blacklist): 
    f = open(BLACKLIST_PATH, 'w')
    # Ecriture
    f.write(str(filter_status))
    f.write('\n')
    f.write(blacklist)

    f.close()

# Convertir les url en en chemin sur le serveur (specificite des communiquation navigateur- proxy)
def from_url_to_chemin(request):
    lignes = request.split('\r\n')


    G = re.compile(r"GET")
    P = re.compile(r"POST")
    
    msg_modifier=[] # msg  apres la convertion
    res = ''
    for line in lignes :

        if G.search(line) :#si get
            
            res = line[0:4]# on coserve le GET 
            i = 13# on se place appres le http://
            while True :#tant que je ne croise pas de /
                if line[i] == '/' :
                    break
                i += 1  # je continue
            res += line[i:] 
            msg_modifier.append(res)

        elif P.search(line): # meme principe que pour get mais adapter a POST

            res = line[0:5]
            i = 14
            while True :
                if line[i] == '/' :
                    break
                i += 1
            res += line[i:]
            msg_modifier.append(res)



        else :
            msg_modifier.append(line) # si ce n'est pas la ligne post/get on la garde telle quelle

    return "\r\n".join(msg_modifier)

def faut_filtrer() : # finction qui revoie si on doit effectuer le filtrage
   
    try :
        fichier = open(BLACKLIST_PATH, 'r') # on ouvre la banList
        ligne = fichier.readline() # ligne du booleen

        return re.search('True', ligne) # retourne s'il faut trier

    except Exception :
        print("erreur, pas de fichier de blacklist")
        return False #si le fichier n'existe pas alors on n'a pas de mots à filtrés


  
def filtre(request): # la foncttions qui effectue le filtrage d'une reponse http
    doc = request.split(b"\r\n")
   
    # La derniere case du tableau contient le corps de la reponse
    html = doc[-1].decode('utf-8', errors='ignore')
    try :
        fichier = open(BLACKLIST_PATH, 'r')
        
        ligne = fichier.readline() # ligne du booleen
        while True : # pour chaque mot de la banlist
            ligne = fichier.readline()

            if not ligne:
                break
            
            mot=re.compile( re.escape(ligne))
            html=re.sub(mot,"###",html)#on filtre le corp de la reponse
    except Exception :
        print("erreur")
    
    doc[-1] = html.encode('utf-8')
    reponse = b"\r\n".join(doc)

    return reponse
        
        
def cible_html (request):#fonctions qui renvoie si la cible de la requete est le document html (index.html)
    #attention la requete doit demander la resssource sur le serveur avec un chemin d'acces et pas une URL

    lignes = request.split('\r\n') 
    G = re.compile(r"GET")
    P = re.compile(r"POST")
    htm = re.compile(r"\.html ")
   
    for line in lignes : 
        if G.search(line) or P.search(line): # si c'es la ligne GET/POST
            i = 0
            while 1 : # on boucle pour trouver le premeir / 
                if re.search(htm,line) : # si on cherche un doc ****.html
                    return True
                elif line[i] == '/' and line[i+1] != ' ' : 
                    return False
                elif line[i]=='/' and line[i+1] == ' ' :# ou si on a juste un / 
                    return True  # alors on cible un doc html

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
    host_line = substr_from(request, 'Host: ')

    host = host_line.split(':') 
    #TODO: ces valeurs sont là pour les test à rendre dynamique plus tard
    if request.startswith('GET'): # HTTP 
        return host[0].strip(), 80
    if request.startswith('CONNECT'): #TLS
        return host[0].strip(), int(host[1].strip()) #443
    if request.startswith('POST'):  
        return host[0].strip(), 80


def get_config_doc(): # Renvoie le document configurator.html
    #header = 'HTTP/1.1 200 OK\nContent-Type: text/html<strong>\n\n</strong>'
    header = b'HTTP/1.1 200 OK\n\n'
    file = open(CONFIG_DOC_PATH, 'rb') 
    response = file.read()
    file.close()

    file = open(BLACKLIST_PATH, 'rb')

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
    rep = re.sub(c, b'id="filter-status" ' + checked_value, rep)
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
print('Lancement du proxy:', IP_PROXY, ':', PORT_PROXY)

while True:
    ############### Attente d'une nouvelle connexion. ###############
    socket_client, addr = ma_socket.accept() # renvoie le socket du client vers le proxy
    print('Nouvelle connexion depuis:', addr)

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
    if request == '':
        #print("Requête vide")
        socket_client.close()
        continue

    #print("Requête reçu: \n", request)
    print('Requête à faire: \n', msg_to_send)

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
    
    print(html)
   
    socket_proxy.sendall(msg.encode('utf-8'))  
 
    
    ############### Réception de la réponse du serveur ###############
    reponse = rcv_all(socket_proxy)  
    #reponse=socket_proxy.recv(36000)
    #print("Taille de la réponse du serveur: ",len(reponse))

 
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
