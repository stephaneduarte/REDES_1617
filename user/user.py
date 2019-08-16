'''--------------------------------------------------------------------------------------'''
'''                                      USER                                            '''
'''                                    Group 33                                          '''
'''     [81186] Stephane Duarte | [81728] Madalena Assembleia | [81858] Joao Oliveira    '''
'''--------------------------------------------------------------------------------------'''

import socket
import sys
import os
import time

#read flags information
def readServerInfo():
    TCSname = 'localhost'
    TCSport = 58033
    if len(sys.argv) == 1:
        return (TCSname, TCSport)
    else:
        try:
            for i in range(1, len(sys.argv)):
                if sys.argv[i] == "-n":
                    TCSname = sys.argv[i+1]
                elif sys.argv[i] == "-p":
                    TCSport = int(sys.argv[i+1])
                elif sys.argv[i][0] == "-" and (sys.argv[i] != "-p" or sys.argv[i] != "-n"):
                    print sys.argv[i] + " argument is not valid."
                    exit()
            return (TCSname, TCSport)
        except:
            print "Arguments are not valid.\nPlease type 'python user.py [-n TCSname] [-p TCSport]'.\n"
            exit()

#function that sends a message to an address
def sendmessageUDP(message):
    try:
        udp.sendto(message, server_address)
    except:
        print "Error while sending a message.\n"
        raise SystemExit

#function that receives a message and the address of the sender
def recvmessageUDP():
    try:
        msgreceived, server = udp.recvfrom(BUFFER_SIZE)
        return msgreceived
    except:
        print "Error while waiting/receiving a message.\n"
        raise SystemExit

#fuction that sends a message (TCP)
def sendmessageTCP(message):
    try:
        tcp.send(message)
    except:
        print "Error while sending a message.\n"
        raise SystemExit

#function that receives a message by TCP (from the TRS)
def recvmessageTCP(size):
    try:
        return tcp.recv(size)
    except:
        print "Error while waiting/receiving a message.\n"
        raise SystemExit

#print languages available
def list_languages():
    sendmessageUDP("ULQ\n") #ask TCS
    msgreceived = recvmessageUDP() #receives the answer
    try:
        languages_nr = int(msgreceived[4])
        languages_available = msgreceived[6:].split( ) #save the languages
        for i in range(0,languages_nr):
          print i+1,"- ",languages_available[i]
        if languages_nr == 0:
            print "No languages available.\n"
        return languages_available
    except:
        print "Error while listing the languages. TCS message is not valid.\n"

#send request
def request(languages_available, order):
    try:
        if int(order[0]) > len(languages_available) or int(order[0]) <= 0: #confirms the language
            print "REQUEST: Language not available."
        else:
            if order[1] == "t" or order[1] == "f":
                sendmessageUDP("UNQ " + languages_available[int(order[0])-1] + "\n") #ask TCS for TRS info
                msgreceived = recvmessageUDP().split( ) #receives TRS info
                IPTRS = msgreceived[1]
                portTRS = msgreceived[2]
                tcp.connect((IPTRS, int(portTRS))) #connect with the TRS
                print "Translating from " + IPTRS + ":" + str(portTRS) + "...\n"
                translate(order[1:])
            else:
                raise RequestError
    except:
        print "REQUEST: Invalid syntax or language not available.\n"
        print "To request list languages: 'list'.\n"
        print "To request text translation: 'request [Language Number] t [Words separated by spaces]'.\n"
        print "To request image translation: 'request [Language Number] f [Filename]'.\n"

#function that translate words/sentences or files
def translate(order):
    try:
        if order[0] == "t": #words/sentences request
          words_nr = len(order[1:])
          if words_nr > 10:
            print "REQUEST: We can't translate more than 10 words at the same time. Please try once again.\n"
            return
          else:
            message = "TRQ t " + str(words_nr) + " " + " ".join(order[1:]) + "\n"
            sendmessageTCP(message) #send request
            data = ''
            temp_size = 0
            #receive answer
            while len(data) == (temp_size):
                message = recvmessageTCP(BUFFER_SIZE)
                data = data + message
                temp_size = temp_size + len(message)
                if (len(data) == temp_size and data[temp_size-1] == "\n"):
                    break
            if data[0:6] == "TRR t ": #translation well succeded
                print data[8:]
            elif data[0:7] == "TRR NTA":
                print "There's no translation for your input.\n"
            else:
                print "REQUEST: Invalid syntax.\n"
                print "To request text translation: 'request [Language Number] t [Words separated by spaces]'.\n"
        if order[0] == "f": #file request
            #SENDING
            size = os.stat(order[1]).st_size
            message = "TRQ f " + order[1] + " " + str(size) + " "
            sendmessageTCP(message)
            image = open(order[1], 'rb') #mode: read bytes
            image_data = image.read(BUFFER_SIZE)
            while (image_data):
                sendmessageTCP(image_data)
                image_data = image.read(BUFFER_SIZE)
            sendmessageTCP("\n") #end of the message
            image.close()
            #RECEIVING
            #receives header
            data = recvmessageTCP(6) #data = "TRR f "
            if data == "TRR f ":
                #reads the message byte-by-byte
                temp_byte = recvmessageTCP(1)
                filename = ''
                size = ''
                while temp_byte != " ": #receiving filename
                    filename = filename + temp_byte
                    temp_byte = recvmessageTCP(1)
                temp_byte = recvmessageTCP(1)
                while temp_byte != " ": #receiving size
                    size = size + temp_byte
                    temp_byte = recvmessageTCP(1)
                print "RECEIVING:\nFILENAME: " + filename + " SIZE: " + size + "\n"
                size = int(size)
                #saves the file
                image = open(filename, 'wb+') #mode: write bytes
                while size > 0:
                    message = recvmessageTCP(BUFFER_SIZE)
                    image.write(message)
                    size = size - len(message) #len(message) could be < than the BUFFER_SIZE
                image.close()
                print "You received " + filename +".\n"
            elif data == "TRR NT":
                A = recvmessageTCP(1)
                if A == 'A':
                    print "There's no translation for your input.\n"
            else:
                print "REQUEST: Invalid syntax.\n"
                print "To request image translation: 'request [Language Number] f [Filename]'.\n"
    except:
        print "Request: Error while translating your text/file.\n"


# USER PROGRAM

BUFFER_SIZE = 256
ask_lang = 0 #flag to remind if the client knows what languages are available

server_address = readServerInfo()

try:
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while(1):
        client_request = raw_input().split( ) #reads input

        if client_request[0] == "list":
            ask_lang = 1
            languages_available = list_languages()

        elif client_request[0] == "request":
            if ask_lang == 0:
                print "REQUEST: Languages are not known yet. Please enter the command 'list'.\n"
            else:
                tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                request(languages_available, client_request[1:])
                tcp.close()

        elif client_request[0] == "exit":
            udp.close()
            exit()

        else:
            print client_request[0] + ": command not known.\n"

except (KeyboardInterrupt, SystemExit):
    udp.close()
    exit()
