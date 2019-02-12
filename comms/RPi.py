import socket

import sys

from Crypto import Random

from Crypto.Cipher import AES

import base64

class Data():
    def __init__(self, socket):
        self.sock = socket        
    def sendData(self, move):
        self.move = move
        self.current = 20
        self.voltage = 20
        self.power = 20
        self.cumpower = 20
        dataToSend = ("#" + self.move + "|" + self.voltage + "|" + self.current + "|" + self.power + "|" + self.cumpower)
        encryptedData = self.encrypt(dataToSend)
        self.sock.send(encryptedData)

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
        self.send()
    
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

    my_pi = RaspberryPi(ip_addr, port_num)