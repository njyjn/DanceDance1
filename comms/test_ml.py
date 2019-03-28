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
dataQueue = queue.Queue(1000)
queueLock = threading.Lock()
labels_dict = {
    0: 'hunch', 1: 'cowboy', 2: 'crab', 3: 'chicken', 4: 'raffles'
}

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

model_path = os.path.join(PROJECT_DIR, 'models', 'firstmodel.h5')
model = load_model(model_path)
graph = tf.get_default_graph()
n_features = 18
# reshape data into time steps of sub-sequences
n_steps, n_length = 4, 15
# for i in range(len(test_samples)):
#     test_samples[i] = test_samples[i].reshape((1, n_steps, n_length, n_features))


def normalise(x, minx, maxx):
    new_x = 2*(x-minx)/(maxx-minx) - 1
    return new_x


def Main_Run():
    print("Ready to go!")
    myThread1 = listen()
    myThread1.start()

    myThread2 = toMLtoServer()
    myThread2.start()

class toMLtoServer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        #my_pi = RaspberryPi(ip_addr, port_num)
        #my_ML = ML()
        danceMove = ""
        power = ""
        voltage = ""
        current = ""
        cumpower = ""
        ml_data = []
        while True:
            queueLock.acquire()
            if not dataQueue.empty(): #check if queue is empty or not. If empty, dont try to take from queue
                packet_data = dataQueue.get()
                #print("data from queue: " + str(packet_data)) #check for multithreading using this line
                power = packet_data["power"]
                voltage = packet_data["voltage"]
                current = packet_data["current"]
                cumpower = packet_data["cumpower"]
                ml_data.append(packet_data["01"] + packet_data["02"] + packet_data["03"])
            queueLock.release()
            #ML prediction
            if len(ml_data) == 60:
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
                print(test_sample.shape)
                with graph.as_default():
                     result = model.predict(test_sample, batch_size=96, verbose=0)
                result_int = int(np.argmax(result[0]))
                danceMove = labels_dict[result_int]
                ml_data = []
                print("Dance move predicted : " + danceMove)
                dataQueue.queue.clear()
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
                #print("data into queue: " + str(packet))
                dataQueue.put(packet)
            queueLock.release()


if __name__ == '__main__':

    Main_Run()
