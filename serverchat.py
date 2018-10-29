#!/usr/bin/python3

import socket
import sys
import select


s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 7777))
s.listen(1)

adrs = [] #stockage des pseudos
stocksock = [] #stockage des sockets
liste = '' #liste des pseudos
x = 0
#faire un tableau de tableau pour les sock associés aux pseudos

def envoi(message, sock):
    for i in stocksock:
        if ( i!=s and i!= sock):
            x = stocksock.index(sock)
            username = adrs[x]
            message = str(username) + ": " + message
            i.send(message.encode())

def supprsock(sock):
    x = stocksock.index(sock)
    sock.close()
    del adrs[x]
    del stocksock[x]

def whois(sock):
    x = stocksock.index(sock)
    pseudo = adrs[x]
    return pseudo

while True:
    l1,_,_ = select.select(stocksock + [s], [], [])
    for sock in l1:
        if sock == s:#JOIN
            (connexion, adresse_client) = sock.accept()
            stocksock.append(connexion)
            adrs.append(adresse_client[1])
            print ('Connection from ', adresse_client[1])
            message_connexion = "JOIN: " + str(adresse_client[1]) + " \n"
            for i in stocksock:
                if ( i!=s and i!= sock):
                    i.send(message_connexion.encode())

        else:
            message = sock.recv(1500).decode('UTF-8')
            if('NICK' in str(message)):#NICK
                nick_len = len(message)-1
                nick = message[5:nick_len]
                x = stocksock.index(sock)#Cherche à quel indice ce trouve sock
                old_pseudo = adrs[x]#ancien pseudo/adresse
                adrs[x] = nick#Associe sock/pseudo
                print('Changement de pseudo de ' + str(old_pseudo) + ' en ' + str(nick))

            elif('LIST' in str(message)):#LIST
                for i in adrs:
                    if not isinstance(i, int):
                        liste = i + " " + liste
                    else:
                        liste = str(i) + " " + liste
                liste = liste + "\n"
                sock.send(str.encode(liste))
                liste = ''

            elif('QUIT' in str(message)):#QUIT
                pseudo = whois(sock)
                message_deconnexion = str(pseudo) + " nous quitte\n"
                for i in stocksock:
                    if (i!=s and i!= sock):
                        i.send(message_deconnexion.encode())
                print("Au revoir", pseudo)
                supprsock(sock)

            elif('KILL' in str(message)):#Exclure un client
                kill_len = len(message)-1
                kill = message[5:kill_len]#kill contient le pseudo ou l'adresse_client
                x = adrs.index(kill)
                sock_kill = stocksock[x]
                message_kick = "Adieu " + str(kill) + "\n"
                sock_kill.send(message_kick.encode())
                print("Adieu", kill)
                supprsock(sock_kill)
                #sock_kill.close()
                #del adrs[x]
                #del stocksock[x]

            elif not message:#QUIT
                pseudo = whois(sock)
                print("Adieu", pseudo)
                message_deconnexion = "QUIT: " + str(pseudo) + " \n"
                for i in stocksock:
                    if (i!=s and i!= sock):
                        i.send(message_deconnexion.encode())
                supprsock(sock)

            else:
                envoi(message, sock)
                pseudo = whois(sock)
                print("Envoi de message de", pseudo)
s.close()
