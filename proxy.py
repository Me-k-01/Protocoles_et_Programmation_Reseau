#!/usr/bin/python3
import socket, subprocess, base64, sys, re


ma_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM,socket.IPPROTO_TCP)
ma_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

ma_socket.bind(('0.0.0.0',80))
ma_socket.listen(socket.SOMAXCONN)


while True:
    client_co,addres = ma_socket.accept()
    #print ("Nouvelle connexion depuis ",addres)
    
    #request=client_co.recv(1000).decode()
    request=client_co.recv(1000)
    
    #je vais isoler chaque partie de la reponse sepaere par \r\n pour retirer les lignes commençant par Connection:keep-alive et Proxy-					connection:keep_alive    
    r=request.decode('utf-8')
    element=r.split('\r\n')
    element.remove(element[3])
    element.remove(element[2])
    
    #on extrait l'adresse du serveur pour se connecter dessus
    host=re.search('(?<=: )[^\]]+',element[2])
    
    #on recompose le message à envoyer au serveur
    e='\r\n'.join(element)
    e=e.encode('utf-8')
    
    #print(request.decode())
    #print(element)
    #print(host[0])
    print(e)
    
    socket_client=socket.socket(socket.AF_INET,socket.SOCK_STREAM,socket.IPPROTO_TCP)
    socket_client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    
    #ces valeurs sont là pour les test à rendre dynamique plus tard
    socket_client.connect(('p-fb.net',443))
    
    socket_client.send(e)
    reponse=socket_client.recv(1000)
    
    socket_client.close()
    #print(reponse.decode())
   
    #response='HTTP/1.1 200 OK\n'
    client_co.sendall(reponse)
    
    
    
    client_co.close()
    
ma_socket.close()
