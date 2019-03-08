import queue
import socket
import sys
import base64
import time
import threading
import os
import arduino as my_Ard
from Crypto import Random
from Crypto.Cipher import AES


#global variables
dataQueue = queue.Queue(10)
queueLock = threading.Lock()


def Main_Run():

    data_filename = time.strftime('%Y-%m-%dT%H%M%S', time.localtime()) + '.csv'
    open(os.path.join(os.pardir, 'data', 'transient', data_filename), 'w+')
    print('Created file %s in main dir' % (data_filename))

    myThread1 = listen()
    myThread1.start()

    myThread2 = toMLtoServer()
    myThread2.start()


class toMLtoServer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        my_pi = RaspberryPi(ip_addr, port_num)
        my_ML = ML()
        danceMove = ""
        while True:
            queueLock.acquire()
            if not dataQueue.empty(): #check if queue is empty or not. If empty, dont try to take from queue
                ML_data = dataQueue.get()
                print("data from queue: " + str(ML_data)) #check for multithreading using this line
                danceMove = my_ML.give(ML_data)
            queueLock.release()
            data = Data(danceMove, my_pi.sock)
            data.sendData()
            time.sleep(2)


class listen(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        my_Ard.init()
        while True:
            packet = my_Ard.listen() #packet is in dict format
            queueLock.acquire()
            if not dataQueue.full(): #check if queue is full. If full, dont put it inside queue
                print("data into queue: " + str(packet))
                dataQueue.put(packet)
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

    ip_addr = sys.argv[1]

    port_num = sys.argv[2]

    Main_Run()
