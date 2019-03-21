import serial
import struct

NUM_DATA_POINTS = 6

MESSAGE_START = 55

PACKET_CODE_NACK = 0
PACKET_CODE_ACK = 1
PACKET_CODE_HELLO = 2
PACKET_CODE_READ = 3
PACKET_CODE_WRITE = 4
PACKET_CODE_DATA_RESPONSE = 5

port = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=10)

def process_data(len):
    packet = {}
    packet['packet_code'] = PACKET_CODE_DATA_RESPONSE
    rawsum = 0 # used to compute checksum
    # get voltage and current values
    raw_voltage = port.read(2)
    rawsum = calculate_rawsum(rawsum, raw_voltage)
    raw_current = port.read(2)
    rawsum = calculate_rawsum(rawsum, raw_current)
    raw_power = port.read(2)
    rawsum = calculate_rawsum(rawsum, raw_power)
    raw_cumpower = port.read(2)
    rawsum = calculate_rawsum(rawsum, raw_cumpower)    
    packet["voltage"] = struct.unpack("<H", raw_voltage)[0] #in mV
    packet["current"] = struct.unpack("<H", raw_current)[0] #in mA
    packet["power"] = struct.unpack("<H", raw_power)[0] #in mW
    packet["cumpower"] = struct.unpack("<H", raw_cumpower)[0] #in mJ
    # get rest of data
    for i in range(len):
        sensor_id = port.read().hex()
        data = []
        rawsum ^= int(sensor_id,16)
        for j in range(NUM_DATA_POINTS):
            raw_data_reading = port.read(2)
            reading = struct.unpack("<h", raw_data_reading)[0]
            data.append(reading)
            rawsum = calculate_rawsum(rawsum, raw_data_reading)
        packet[str(sensor_id)] = data
    checksum = int(port.read().hex(),16)
    return packet, (checksum == rawsum)


def calculate_rawsum(rawsum, raw_reading):
    top, bottom = divmod(int(raw_reading.hex(),16),0x100)
    rawsum ^= top
    rawsum ^= bottom
    return rawsum

def read_packet():
    packet = {}
    is_valid = True
    start=port.read().hex()
    try:
        if int(start,16) == MESSAGE_START:
            packet_code = int(port.read().hex(),16)
            len = int(port.read().hex(),16)
            if packet_code == PACKET_CODE_DATA_RESPONSE and len>0: # Sensor data
                packet, is_valid = process_data(len)
            elif packet_code == PACKET_CODE_ACK:
                packet['packet_code'] = PACKET_CODE_ACK
            elif packet_code == PACKET_CODE_NACK:
                packet['packet_code'] = PACKET_CODE_NACK
            elif packet_code == PACKET_CODE_HELLO:
                packet['packet_code'] = PACKET_CODE_HELLO
            elif packet_code == PACKET_CODE_READ:
                packet['packet_code'] = PACKET_CODE_READ
            elif packet_code == PACKET_CODE_WRITE:
                packet['packet_code'] = PACKET_CODE_WRITE
            else:
                is_valid = False
    except Exception as e:
        reset()
    return packet, is_valid


def send_packet(packet_code):
    port.write(struct.pack("B", MESSAGE_START)) # start
    port.write(struct.pack("B", packet_code))
    port.write(struct.pack("B", 0)) # len


def handshake_init():
    handshake_status = 0
    while handshake_status > -1:
        try:
            response,checksum = read_packet()
            # Hello from Arduino
            if handshake_status == 0 and response.get('packet_code') == PACKET_CODE_HELLO:
                print("Arduino says HELLO...")
                # Ack to Arduino
                send_packet(PACKET_CODE_ACK)
                print("Sent HELLO ACK to RPi")
                handshake_status = 1
            # First Ack from Arduino
            elif handshake_status == 1 and response.get('packet_code') == PACKET_CODE_ACK:
                print("Arduino says ACK")
                # Hello to Arduino
                send_packet(PACKET_CODE_HELLO)
                print("Sent HELLO to RPi")
                handshake_status = 2
            # Last Ack from Arduino
            elif handshake_status == 2 and response.get('packet_code') == PACKET_CODE_ACK:
                print("Arduino says ACK")
                # Ack to Arduino
                send_packet(PACKET_CODE_ACK)
                print("Sent ACK to RPi. Handshake complete!")
                handshake_status = -1
            elif response.get('packet_code') == PACKET_CODE_DATA_RESPONSE:
                print("Arduino was in the midst of transmission. Reconnecting...")
                # Ack to Arduino
                send_packet(PACKET_CODE_ACK)
                print("Sent ACK to RPi. Connection reestablished!")
                handshake_status = -1
        except Exception as e:
            reset()
    return True


def init():
    # Initial setup message to console
    print("Hello world! Awaiting initial handshake from Arduino...")
    port.flushInput()
    # Initial handshake with RPi
    handshake_init()


def reset():
    print("Resetting connection...")
    port.close()
    port.open()
    init()


def listen():
    # Process the packets
    packet, is_valid = read_packet()
    if packet.get('packet_code') == 5:
        if is_valid:
            send_packet(PACKET_CODE_ACK) # Acknowledge data received
        else:
            send_packet(PACKET_CODE_NACK) # Reject data and ask to resend
        return packet
    elif packet.get('packet_code') == 2:
        handshake_init()
