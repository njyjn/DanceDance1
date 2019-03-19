import queue
import socket
import sys
import base64
import time
import threading
import os
import arduino as my_Ard
import csv
from Crypto import Random
from Crypto.Cipher import AES


#global variables
dataQueue = queue.Queue(1000)
queueLock = threading.Lock()
workingCSV = ""

def Main_Run():
    global workingCSV
    workingCSV = createCSV()
    myThread1 = listen()
    myThread1.start()

    myThread2 = toMLtoServer()
    myThread2.start()

def createCSV():
    data_filename = time.strftime('%Y-%m-%dT%H%M%S', time.localtime()) + '.csv'
    open(os.path.join(os.pardir, 'data', 'transient', data_filename), 'w+')
    print('Created file %s in main dir' % (data_filename))
    return data_filename

def appendToCSV(packet_data, data_filename):
    ML_data = [
    #    [] ,
    #   [] ,
# []
    ]            
    
    with open(os.path.join(os.pardir, 'data', 'transient', data_filename), 'a', newline = '') as datafile:
        writer = csv.writer(datafile, delimiter = " ")
        writer.writerow(packet_data["01"]+packet_data["02"]+packet_data["03"])

class toMLtoServer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
#        my_pi = RaspberryPi(ip_addr, port_num)
 #       my_ML = ML()
  #      danceMove = ""
        #power = ""
        #voltage = ""
        #current = ""
        #cumpower = ""
        while True:
            queueLock.acquire()
            if not dataQueue.empty(): #check if queue is empty or not. If empty, dont try to take from queue
                packet_data = dataQueue.get()
                print("data from queue: " + str(packet_data)) #check for multithreading using this line
                #power = packet_data["power"]
                #voltage = packet_data["voltage"]
                #current = packet_data["current"]
                #cumpower = packet_data["cumpower"]
                #danceMove = my_ML.give(packet_data)
                appendToCSV(packet_data, workingCSV)
            queueLock.release()
   #         danceMove = my_ML.give(packet_data) #dummy class for sending
    #        data = Data(danceMove, my_pi.sock)
     #       data.sendData()
            #time.sleep(2)


class listen(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        my_Ard.init()
        while True:
            packet = my_Ard.listen() #packet is in dict format
            queueLock.acquire()
            if not dataQueue.full() and packet is not None: #check if queue is full. If full, dont put it inside queue
                print("data into queue: " + str(packet))
                dataQueue.put(packet)
                print("queue size: " + str(dataQueue.full()))
            queueLock.release()


class ML():
    #dummy class for ML module
    def give(self, data):
        return "cowboy"


class Data():
    def __init__(self, move, sock):
        self.move = move
        self.sock = sock

    def sendData(self):
        self.current = 20
        self.voltage = 20
        self.power = 20
        self.cumpower = 20
        dataToSend = ("#" + self.move + "|" + str(self.voltage) + "|" + str(self.current) + "|" + str(self.power) + "|" + str(self.cumpower) + "|")
        print("sending over data: " + dataToSend)
        paddedMsg = self.pad(dataToSend) #apply padding to pad message to multiple of 16
        encryptedData =self.encrypt(paddedMsg) #encrypt and encode in base64
        print('encrypted + encoded data is : ' + str(encryptedData))
        # encodedData = encryptedData.encode('utf8')
        self.sock.sendall(encryptedData)

    def pad(self,msg):
        extraChar = len(msg) % 16
        if extraChar > 0: #if msg size is under or over 16 char size
            padsize = 16 - extraChar
            paddedMsg = msg + (' ' * padsize)
        return paddedMsg

    def encrypt(self, msg):
        secret_key = "1234512345123451" #dummy key for testing
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(secret_key,AES.MODE_CBC,iv)
        return base64.b64encode(iv + cipher.encrypt(msg)) #encrypted msg in octets(bytes) is transformed into sets of sextets. sextet value is used to determine the letter in Base64 table


class RaspberryPi():

    def __init__(self, server_add, server_port):
        self.server_add = server_add #address of the server (PC acting as server)
        self.server_port = int(server_port) #port of the server(PC acting as server)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates the socket object
        self.connect()

    def connect(self):
        server_fullAdd = (self.server_add, self.server_port)
        self.sock.connect(server_fullAdd) #connect to server socket
        print("connected to server websocket!")


if __name__ == '__main__':
    Main_Run()
