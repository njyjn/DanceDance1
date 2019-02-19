import socket

import sys

from Crypto import Random

from Crypto.Cipher import AES

import base64

import arduino as my_Ard
def Main_Run():

    #init conn to Arduino, blocking
    my_Ard.init()

    #init server
    my_pi = RaspberryPi(ip_addr, port_num)

    #poll data from arduino and send it to ML.
    for x in range(0,5):
        packet = my_Ard.listen()
    my_ML = ML()
    #obtain dance move and other relevant information from ML and send it to server
    data = Data(my_pi.sock, my_ML)
    data.sendData()

class ML():
    #dummy class for ML module
    def get(self):
        return "cowboy"


class Data():
    def __init__(self, socket, ML):
        self.sock = socket    
        self.ML = ML    
    def sendData(self):
        self.move = self.ML.get() #ML module that determines the dance move.
        self.current = 20
        self.voltage = 20
        self.power = 20
        self.cumpower = 20
        dataToSend = ("#" + self.move + "|" + str(self.voltage) + "|" + str(self.current) + "|" + str(self.power) + "|" + str(self.cumpower))
        paddedMsg = self.pad(dataToSend) #apply padding to pad message to multiple of 16
        encryptedData = self.encrypt(paddedMsg)
        self.sock.send(encryptedData)

    def pad(self,msg):
        extraChar = len(msg) % 16
        if extraChar > 0: #if msg size is under or over 16 char size
            padsize = 16 - extraChar
            paddedMsg = msg + (' ' * padsize)
        return paddedMsg

    def encrypt(self, msg):
        secret_key = "1234512345123451"
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(secret_key,AES.MODE_CBC,iv)
        return base64.b64encode(iv + cipher.encrypt(msg))
        
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
        #self.send()
    
    def send(self): #dummy msg for testing
        msg = "#fsdfoy|20|20|20|20|"
        paddedMsg = self.pad(msg) #apply padding to pad message to multiple of 16
        secret_key = "1234512345123451" #secret key for testing only
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(secret_key,AES.MODE_CBC,iv)
        encodedMsg = base64.b64encode(iv + cipher.encrypt(paddedMsg))
        self.sock.send(encodedMsg)
    def pad(self,msg):
        extraChar = len(msg) % 16
        if extraChar > 0: #if msg size is under or over 16 char size
            padsize = 16 - extraChar
            paddedMsg = msg + (' ' * padsize)
        return paddedMsg

if __name__ == '__main__':

    print("input server address: ")

    ip_addr = sys.argv[1]

    port_num = sys.argv[2]

    Main_Run()
    #my_pi = RaspberryPi(ip_addr, port_num)