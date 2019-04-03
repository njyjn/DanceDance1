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
from keras.models import load_model
import numpy as np
import tensorflow as tf


#global variables
dataQueue = queue.Queue(100)
queueLock = threading.Lock()
labels_dict = {
    0: 'hunchback', 1: 'cowboy', 2: 'crab', 3: 'chicken', 4: 'raffles'
}

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

model_path = os.path.join(PROJECT_DIR, 'models', 'onesecondCVmodel.h5')
model = load_model(model_path)
graph = tf.get_default_graph()
n_features = 18
# reshape data into time steps of sub-sequences
n_steps, n_length = 4, 5
# for i in range(len(test_samples)):
#     test_samples[i] = test_samples[i].reshape((1, n_steps, n_length, n_features))


def normalise(x, minx, maxx):
    new_x = 2*(x-minx)/(maxx-minx) - 1
    return new_x


def Main_Run():
    
    myThread1 = listen()
    myThread2 = toMLtoServer()
    input("Press ENTER when server is ready...")
    print("Started!")
    myThread1.start()
    myThread2.start()

class toMLtoServer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.my_pi = RaspberryPi(ip_addr, port_num)

    def run(self):
        danceMove = ""
        power = ""
        voltage = ""
        current = ""
        cumpower = ""
        ml_data = []
        predictions = ["0","1","2"]
        j=0
        while True:
            queueLock.acquire()
            if not dataQueue.empty(): #check if queue is empty or not. If empty, dont try to take from queue
                packet_data = dataQueue.get()
                #print("data from queue: " + str(packet_data)) #check for multithreading using this line
                if packet_data is None:
                    print("None received")
                    continue 
                power = packet_data["power"]
                voltage = packet_data["voltage"]
                current = packet_data["current"]
                cumpower = int(packet_data["cumpower"] / 1000)
                ml_data.append(packet_data["01"] + packet_data["02"] + packet_data["03"])
            queueLock.release()
            #ML prediction
            if len(ml_data) == 20:
                for arr in ml_data:
                    for i in range(len(arr)):
                        if i < 3:
                            arr[i] = normalise(arr[i], -2000, 2000)
                        elif i in range(3, 6):
                            arr[i] = normalise(arr[i], -250000, 250000)
                        elif i in range(6, 9):
                            arr[i] = normalise(arr[i], -2000, 2000)
                        elif i in range(9, 12):
                            arr[i] = normalise(arr[i], -250000, 250000)
                        elif i in range(12, 15):
                            arr[i] = normalise(arr[i], -2000, 2000)
                        elif i in range(15, 18):
                            arr[i] = normalise(arr[i], -250000, 250000)
                arr_data = []
                for array in ml_data:
                    arr_raw = []
                    arr_raw += [
                        array[0], array[1], array[2], array[6], array[7], array[8], array[12], array[13], array[14],
                        array[3],
                        array[4], array[5], array[9], array[10], array[11], array[15], array[16], array[17]
                    ]
                    arr_data.append(arr_raw)

                test_sample = arr_data
                test_sample = np.array(test_sample)
                test_sample = test_sample.reshape(1, n_steps, n_length, n_features)
                with graph.as_default():
                       result = model.predict(test_sample, batch_size=96, verbose=0)
                       
                model.reset_states()
                result_int = int(np.argmax(result[0]))
                danceMove = labels_dict[result_int]
                index = j % 3
                predictions[index] = danceMove
                j = j + 1
                print(predictions)
                if all(prediction==predictions[0] for prediction in predictions):
                    predictions = ["0","1","2"]
                    data = Data(self.my_pi.sock)
                    data.sendData(danceMove, power, voltage, current, cumpower)
                    #queueLock.acquire()
                    #dataQueue.queue.clear()
                    time.sleep(1.5)
                    my_Ard.clear_buffer()
                    #if dataQueue.empty(): 
                        #print("queue has been emptied for new window")
                    #queueLock.release()
                ml_data = []
                dataQueue.queue.clear()
                print("data queue has been cleared")

class listen(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        my_Ard.init()

    def run(self):
        my_Ard.clear_buffer()
        while True:
            packet = my_Ard.listen() #packet is in dict format
            queueLock.acquire()
            if not dataQueue.full(): #check if queue is full. If full, dont put it inside queue
                #print("data into queue: " + str(packet))
                dataQueue.put(packet)
            queueLock.release()



class ML():
    #dummy class for ML module
    def give(self, data):
        return "cowboy"


class Data():
    def __init__(self, sock):
        self.sock = sock

    def sendData(self, move, power, voltage, current, cumpower):
        self.move = move
        self.current = current
        self.voltage = voltage
        self.power = power
        self.cumpower = cumpower
        dataToSend = ("#" + self.move + "|" + str(self.voltage) + "|" + str(self.current) + "|" + str(self.power) + "|" + str(self.cumpower) + "|")
        print("sending over data: " + str(dataToSend))
        paddedMsg = self.pad(dataToSend) #apply padding to pad message to multiple of 16
        encryptedData =self.encrypt(paddedMsg) #encrypt and encode in base64
        #print('encrypted + encoded data is : ' + str(encryptedData))
        self.sock.sendall(encryptedData)

    def pad(self,msg):
        paddedMsg = ""
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
