from arduino import listen, init
import time

print("Welcome to debug mode!")
init()
while True:
    packet = listen()
    if packet is not None:
        print(packet)
