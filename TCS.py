'''--------------------------------------------------------------------------------------'''
'''                                       TCS                                            '''
'''                                    Group 33                                          '''
'''     [81186] Stephane Duarte | [81728] Madalena Assembleia | [81858] Joao Oliveira    '''
'''--------------------------------------------------------------------------------------'''

import sys
import socket

#read flags information
def readTCSInfo():
    TCSport = 58033
    if len(sys.argv) == 1:
        return TCSport
    else:
        for i in range(1, len(sys.argv)):
            if sys.argv[i] == "-p":
                try:
                    TCSport = int(sys.argv[i+1])
                except:
                    print sys.argv[i+1] + " is not a valid port.\n"
                    exit()
            elif sys.argv[i][0] == "-" and (sys.argv[i] != "-p"):
              print sys.argv[i] + " argument is not valid.\n"
              exit()
        return TCSport

#function that receives a message and the address of the sender
def recvmessage():
    try:
        msgreceived, address = server_socket.recvfrom(BUFFER_SIZE)
        return msgreceived, address
    except:
        print "Error while waiting/receiving a message.\n"
        raise SystemExit

#function that sends a message to an address
def sendmessage(message):
    try:
        server_socket.sendto(message, address)
    except:
        print "Error while sending a message.\n"
        raise SystemExit

#function that create a string with the available languages
def langs_available():
  string = ""
  i = 0
  for i in range(0, len(servers_list)):
    string = string + " " + servers_list[i][0]
  return string

#function that searches the index of a server in the list of servers by language
def search_lang(lang):
    i = 0
    for i in range(0, len(servers_list)):
        if servers_list[i][0] == lang:
            return i
    raise LangError

#function that searches if a server with that language(lang) already exists
def accept_lang(lang):
  i = 0
  for i in range(0, len(servers_list)):
      if servers_list[i][0] == lang:
          raise LangError
  return 1

#GLOBAL VARIABLES
BUFFER_SIZE = 256
servers_list = []
TCSport = readTCSInfo()

#SOCKET E SERVER CREATION
try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #bind the socket to a public host
    server_address = ('', TCSport)
    server_socket.bind(server_address) #become a server socket
except:
    "INICIATING: Error while creating the socket.\n"
    exit()

while(1):

    try:
        message, address = recvmessage() #wait for a message
        message = message.split()

        #TRS COMMUNICATION

        if message[0] == "SRG": #server wants to connect
            if len(message) == 4:
                try:
                    accept_lang(message[1]) #Language verification
                    socket.inet_aton(message[2]) #IP verification
                    int(message[3]) #Port verification
                    print "Server: " + str(message[2]) + ":" + str(message[3]) + " connected.  Language: " + message[1] + "\n"
                    servers_list.extend([message[1:]]) #add server to the list
                    sendmessage("SRR OK\n")
                except:
                    sendmessage("SRR NOK\n")
            else:
                sendmessage("SRR ERR\n")

        elif message[0] == "SUN": #server wants to disconnect
            if len(message) == 4:
                try:
                    i = search_lang(message[1]) #search server by language
                    socket.inet_aton(message[2]) #IP verification
                    int(message[3]) #Port verification
                    del servers_list[i] #remove server from the list
                    sendmessage("SUR OK\n")
                    print "Server: " + message[2] + ":" + message[3] + " disconnected.  Language: " + message[1] + "\n"
                except:
                    sendmessage("SUR NOK\n")
            else:
                sendmessage("SUR ERR\n")

        #USER COMMUNICATION

        elif message[0] == "ULQ": #client asks for languages available
            if len(message) == 1:
                try:
                    langs = langs_available()
                    print "Client asked for languages available: " + langs
                    sendmessage("ULR " + str(len(servers_list)) + langs + "\n")
                except:
                    sendmessage("ULR EOF\n")
            else:
                sendmessage("ULR ERR\n")

        elif message[0] == "UNQ": #client requests a server for tranlating a language
            if len(message) == 2:
                try:
                    print "Client request: " + message[1]
                    i = search_lang(message[1]) #search server by language
                    sendmessage("UNR " + servers_list[i][1] + " " + servers_list[i][2] + "\n") #send server IP and PORT
                except:
                    sendmessage("UNR EOF\n")
            else:
                sendmessage("UNR ERR\n")

        else:
            print "Message received not known.\n"

    except (KeyboardInterrupt, SystemExit):
        server_socket.close()
        exit()
