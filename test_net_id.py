import serial
import time
from rfd900x import RFDConfig

serial_port = '/dev/tty.usbserial-ABSCDK0I'
baud_rate = 57600

radio = RFDConfig()
radio.port.port = serial_port
radio.port.baudrate = baud_rate
radio.port.timeout = 2
radio.port.open()

try:
    time.sleep(1)  
    radio.port.write("+++".encode())
    time.sleep(1)  
    response = radio.port.read(100).decode().strip()
    if "OK" in response:
        print("Entered command mode.")
    else:
        print("Failed to enter command mode. Response:", response)
    
    ############## Set the NetID HERE ##########
    command = "ATS3=222\r"
    radio.port.write(command.encode())
    time.sleep(0.1)
    response = radio.port.read(100).decode().strip()
    print("Set NetID Response:", response)
    
    # Verify the NetID
    radio.port.write("ATS3?\r".encode())
    time.sleep(0.1)
    response = radio.port.read(100).decode().strip()
    print("Verify NetID Response:", response)

    if "222" in response:
        print("NetID successfully set and verified.")
    else:
        print("NetID verification failed.")

    radio.port.write("AT&W\r".encode())
    time.sleep(0.1)
    response = radio.port.read(100).decode().strip()
    print("Save Settings Response:", response)
    
    radio.port.write("ATO\r".encode())
    time.sleep(0.1)
    print("Exited command mode.")
finally:
    radio.port.close()
