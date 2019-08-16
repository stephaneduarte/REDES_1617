'''--------------------------------------------------------------------------------------'''
'''                                       TRS                                            '''
'''                                    Group 33                                          '''
'''     [81186] Stephane Duarte | [81728] Madalena Assembleia | [81858] Joao Oliveira    '''
'''--------------------------------------------------------------------------------------'''

import socket
import sys
import time
import os

#read flags information
def readTRSInfo():
    if len(sys.argv) == 1:
        print "You should indentify yourself. Please do './TRS.py [yournamehere]'."
        exit()
    else:
        try:
            LanguageName = sys.argv[1]
            TRSport = 59000
            TCSname = 'localhost'
            TCSport = 58033
            for i in range(2, len(sys.argv)):
                if sys.argv[i] == "-p":
                    TRSport = int(sys.argv[i+1])
                elif sys.argv[i] == "-n":
                    TCSname = sys.argv[i+1]
                elif sys.argv[i] == "-e":
                    TCSport = int(sys.argv[i+1])
                elif sys.argv[i][0] == "-" and (sys.argv[i] != "-p" or sys.argv[i] != "-n" or sys.argv[i] != "-e"):
                	print sys.argv[i] + " argument is not valid.\nPlease type 'python TRS.py LanguageName [-p TRSport] [-n TCSname] [-e TCSport]'.\n"
                	exit()
            return (LanguageName, TRSport, TCSname, TCSport)
        except:
            print "Arguments are not valid.\nPlease type 'python TRS.py LanguageName [-p TRSport] [-n TCSname] [-e TCSport]'.\n"
            exit()

#function that sends a message to the TCS
def sendmessageUDP(message):
    try:
        udp.sendto(message, (TCSname, TCSport))
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

#function that receives a message by TCP (from the user)
def recvmessageTCP(size):
    try:
        return connection.recv(size)
    except:
        print "Error while waiting/receiving a message.\n"
        raise SystemExit

#ask for connection with the TCS
def connectTCS():
    sendmessageUDP("SRG " + LanguageName + " " + IPSTRS + " " + str(TRSport) + "\n")
    msgreceived = recvmessageUDP().split( )
    if msgreceived[1] == 'OK\n': #connection accepted
        print(msgreceived[1])
        return 1
    if msgreceived[1] == 'NOK\n': #connection denied
        print("CONNECT: Your request has been denied by the Translation Central Server.\n")
        return 0
    if msgreceived[1] == 'ERR\n': #error
        print("CONNECT: Your request has been denied by the Translation Central Server. Please check your information.\n")
        return 0

#ask for disconnection with the TCS
def disconnect():
  sendmessageUDP("SUN " + LanguageName + " " + IPSTRS + " " + str(TRSport) + "\n")
  msgreceived = recvmessageUDP().split()
  if msgreceived[1] == 'OK\n': #disconnected
    print(msgreceived[1] + "\n")
    return 1
  if msgreceived[1] == 'NOK\n': #not disconnected
      print("DISCONNECT: Your request has been denied by the Translation Central Server.\n")
      return 0
  if msgreceived[1] == 'ERR\n': #error
      print("DISCONNECT: Your request has been denied by the Translation Central Server. Please check your information.\n")
      return 0

#translate words/sentences
def translate_text(data): #data = "N W1 W2 ... WN\n"
	try:
		temp_size = BUFFER_SIZE - 6
		#receive data
		while len(data) == (temp_size): 
			message = recvmessageTCP(BUFFER_SIZE)
			data = data + message
			temp_size = temp_size + len(message)
			if (len(data) == temp_size and data[temp_size-1] == "\n"):
				break
		words_nr = int(data[0])
		words_nr_flag = 0
		data = data[1:].split( ) #data = [W1, W2, ..., WN]
		translated_text = "TRR t" + " " + str(words_nr)
		for i in range(0,words_nr):
			text_doc = open('text_translation.txt', 'r')
			for string in text_doc:
				line = string.split()
				if line[0] == data[i]:
					translated_text += " " + line[1]
					words_nr_flag = words_nr_flag + 1
			text_doc.close()
		if words_nr_flag == words_nr: #all the words have been translated
			connection.send(translated_text + "\n")
		else: #there's no available translation
			connection.send("TRR NTA\n")
	except:
		connection.send("TRR ERR\n")
		print "Error while translating text.\n"

#translate files
def translate_file(): #data = "filename size data\n"
    try:
        #RECEIVING
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
        #SENDING
        #search a translation
        file_translation = ''
        file_doc = open('file_translation.txt', 'r')
        for string in file_doc:
            line = string.split()
            if line[0] == filename:
                file_translation = line[1]
        file_doc.close()
        if file_translation != '': #found a translation
            size = os.stat(file_translation).st_size #get size
            connection.send("TRR f " + file_translation + " " + str(size) + " ") #inform the user
            image = open(file_translation, 'rb') #mode: read bytes
            image_data = image.read(BUFFER_SIZE)
            while (image_data):
                connection.send(image_data)
                image_data = image.read(BUFFER_SIZE)
            connection.send("\n") #end of the message
            image.close()
        else: #no translation available
            connection.send("TRR NTA")
        time.sleep(1)
    except:
    	connection.send("TRR ERR")
        print "Error while translating files.\n"

#MAIN
BUFFER_SIZE = 256

TRSdetails = readTRSInfo()
LanguageName = TRSdetails[0]
TRSport = TRSdetails[1]
TCSname = TRSdetails[2]
TCSport = TRSdetails[3]

try:
    ip = socket.gethostname()
    IPSTRS = socket.gethostbyname(ip)

    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if connectTCS() == 0: #Connect TCS
        disconnect()
        udp.close()
        exit()

    print('Listening...')

    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind((IPSTRS, TRSport))

    while(1):
        tcp.listen(5)
        connection, client_address = tcp.accept() #Connect with a user
        print "Translating to: " + client_address[0] + ":" + str(client_address[1]) + "...\n" #print user info
        client_request = recvmessageTCP(6)
        if client_request == "TRQ t ":
            translate_text(recvmessageTCP(BUFFER_SIZE))
        if client_request == "TRQ f ":
            translate_file()
        connection.close()

except (KeyboardInterrupt, SystemExit):
    disconnect()
    tcp.close()
    udp.close()
    exit()
