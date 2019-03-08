from arduino import listen


print("Welcome to debug mode!")
while true:
    packet = listen()
    print(packet)
