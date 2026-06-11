import serial
import time

# Constants
SOH = 0x01
EOT = 0x04
ACK = 0x06
NAK = 0x15

def calculate_checksum(data):
    # sum all bytes and return lowest 8 bits
    sum = 0
    for byte in data:
        sum += byte
    return sum & 0xFF

def send_file(port, filename):
    # open serial port
    # open firmware file
    # wait for initial NAK from STM32
    # send packets one by one
    # send EOT when done

    # So far I am only sending packet

    ser = serial.Serial(port=port,baudrate=115200,timeout=None)
    time.sleep(0.5)
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    print("Listening for Start")
    # Waiting for initial NAK from STM32
    listening = True
    while (listening):
        if ser.in_waiting > 0:
            data = ser.read(1)
            if data and data[0] == NAK:
                print("Starting Communication")
                listening = False

    packet_num = 1
    packet = bytearray([SOH, packet_num, (~packet_num) & 0xFF])
    checksum = 0

    with open(filename, "rb") as f:
        data = f.read(16)
        data = data.ljust(128, b'\x1A')  # 0x1A is standard XMODEM padding
        # byte_data = bytes([int(data,2)])
        packet.extend(data)
        checksum = calculate_checksum(data)
        packet.append(checksum)

    f.close()

    print(f"Sending Packet...{time.time()}")
    ser.write(packet)
    print("Succesfully Sent Packet")

    listening = True
    while (listening):
        if ser.in_waiting > 0:
            data = ser.read(1)
            if data and data[0] == ACK:
                print(f"STM32 Successfully Recieved Packet: {packet_num}")
                listening = False
                packet_num += 1

    ser.write(bytes([EOT]))

    listening = True
    while (listening):
        if ser.in_waiting > 0:
            data = ser.read(1)
            if data and data[0] == ACK:
                print("Successfully Ended Communication")
                listening = False
                packet_num += 1

    ser.close()


def main():
    send_file("COM6","app.bin")

main()