import serial
import time

# Constants
SOH = 0x01
EOT = 0x04
ACK = 0x06
NAK = 0x15

EOT_SIZE = 1
MAX_RETRIES = 4
TIMEOUT = 5
DATA_SIZE = 128
PACKET_SIZE = 132

def calculate_checksum(data):
    # sum all bytes and return lowest 8 bits
    sum = 0
    for byte in data:
        sum += byte
    return sum & 0xFF

def send_one_packet(serial_obj,packet_num=0,data=0,is_EOT=False):
    if(is_EOT):
        serial_obj.write(bytes([EOT]))
        bytes_written = EOT_SIZE
    else:                     
        packet_num = packet_num
        packet = bytearray([SOH, packet_num, (~packet_num) & 0xFF])
        checksum = 0

        data = data.ljust(128, b'\x1A')  # 0x1A is standard XMODEM padding
        packet.extend(data)
        checksum = calculate_checksum(data)
        packet.append(checksum)

        bytes_written = serial_obj.write(packet)

    return bytes_written
    
def wait_for_response(serial_obj,value=ACK,timeout=None):
    if value == ACK:
        other_value = NAK
    else:
        other_value = ACK

    listening = 1
    time_start = time.time()
    while (listening):
        if timeout != None:
            if time.time() - time_start > timeout:
                listening = 2
                break

        if serial_obj.in_waiting > 0:
            data = serial_obj.read(1)
            if data and data[0] == value:
                listening = 0
            elif data and data[0] == other_value:
                break
            else:
                pass

    return listening


def send_file(port, filename):
    # open serial port
    # open firmware file
    # wait for initial NAK from STM32
    # send packets one by one
    # send EOT when done

    ser = serial.Serial(port=port,baudrate=115200,timeout=None)
    time.sleep(0.5)
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    packet_num = 1
    total_data_bytes_sent = 0
    abort = False
    is_EOT_sent_yet = False
    eot = False
    packet_size = PACKET_SIZE

    print("Listening for Start")

    while True:
        status = wait_for_response(ser, NAK, 5*TIMEOUT)
        if status == 0:
            break # Stop looping if status is 0    
        if status == 2:
            print("Timeout, no receiver initiating: Exiting...")
            return total_data_bytes_sent # Exit the function since since we are aborting

    print("Starting Communication") 

    try:
        with open(filename,"rb") as f:
            while True:
                if is_EOT_sent_yet:
                    break

                data = f.read(DATA_SIZE)

                if not data and not is_EOT_sent_yet: # No data left, just need to send EOT
                    packet_size = EOT_SIZE
                    packet_num = "EOT"
                    eot = True
                    is_EOT_sent_yet = True

                if(send_one_packet(ser,packet_num,data,eot) == packet_size):
                    max_retries = MAX_RETRIES
                    while(True): # While I am not getting an ACK, I keep resending packets
                        status = wait_for_response(ser,ACK,TIMEOUT) 
                        if(status == 2): # If response is neither ACK or NAK, just garbage -> assume communication is lost
                            print(f"Packet {packet_num} timed out, receiver not responding: Aborting communication")
                            abort = True
                            break 
                        elif(status == 1 and max_retries > 0): # Received the opposite value (in this case a NAK)
                            send_one_packet(ser,packet_num,data)
                            print(f"Packet {packet_num} sent & not received: Resending...{max_retries-1} Attempts Remaining")
                            max_retries -= 1
                        elif(status == 1 and max_retries == 0):
                            print(f"Max retries used: Aborting communication")
                            abort = True
                            break
                        else:
                            break

                    if abort:
                        break
                    else:
                        # I have received an ACK for the current packet
                        print(f"Packet {packet_num} sent & received")
                        if not is_EOT_sent_yet:
                            packet_num = (packet_num + 1) & 0xFF # Becareful it cannot be more than one byte
                            total_data_bytes_sent += DATA_SIZE
                else:
                    print(f"Packet {packet_num} failed to be sent")

        if (abort):
            print("Communication was not successful")
        else:
            print("Communication was successful: File fully sent")
            
    except FileNotFoundError:
        print("Error: The file 'app.bin' does not exist.")

    except PermissionError:
        print("Error: You do not have permission to read this file.")
        
    ser.close()

    return total_data_bytes_sent


def main():
    # Note to get the actual length of the file do:

    # Get-Item app.bin | Select-Object Length

    # This returned 9328, very close to 9344 (due to the padding on the last packet)
    bytes_sent = send_file("COM6","app.bin")
    print(f"Total number of data bytes sent from app.bin: {bytes_sent}")

main()