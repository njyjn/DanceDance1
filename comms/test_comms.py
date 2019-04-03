from arduino import listen, init


print("Welcome to debug mode!")
init()
while True:
    packet = listen()
    print(packet)
