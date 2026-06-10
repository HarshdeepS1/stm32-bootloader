import serial
import time

# Constants
SOH = 0x01
EOT = 0x04
ACK = 0x06
NAK = 0x15

def calculate_checksum(data):
    # sum all bytes and return lowest 8 bits
    pass

def send_file(port, filename):
    # open serial port
    # open firmware file
    # wait for initial NAK from STM32
    # send packets one by one
    # send EOT when done
    pass