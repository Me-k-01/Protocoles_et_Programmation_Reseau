#!/usr/bin/python3
import socket, subprocess, base64, sys


ma_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM,socket.IPPROTO_TCP)
ma_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

ma_socket.bind(('0.0.0.0',80))
ma_socket.listen(socket.SOMAXCONN)


while True:
    client_co,addres = ma_socket.accept()
    print ("Nouvelle connexion depuis ",addres)
    
    request=client_co.recv(1000).decode()
    print(request)
    
    
    response='HTTP/1.1 200 OK\n'
    client_co.sendall(response.encode())
    
    
    client_co.close()
    
    
    '''
    socket_co=socket.socket(socket.AF_INET,socket.SOCK_STREAM,socket.IPPROTO_TCP)
    socket_co.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    
    socket_co.bind(addres)
    #socket_co.connect(addres)
    response=nouvelle_connexion.recv(1000)
    
    socket_co.send(response)

    socket_co.close()
    '''
ma_socket.close()
