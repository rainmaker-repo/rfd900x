import serial
import time
import sys
from rfd900x import RFDConfig
from serial.tools import list_ports

def enter_command_mode(radio):
    time.sleep(1)  
    radio.port.write("+++".encode())
    time.sleep(1)  
    response = radio.port.read(100).decode().strip()
    if "OK" not in response:
        print("Failed to enter command mode. Response:", response)
        sys.exit(1)

def read_netid(radio):
    radio.port.write("ATS3?\r".encode())
    time.sleep(0.1)
    response = radio.port.read(100).decode().strip()
    # Clean up response to get just the number
    netid = response.replace('ATS3?', '').strip()
    print(f"Current NetID: {netid}")
    return netid

def write_netid(radio, netid):
    # Get current ID first
    print(f"Changing NetID to {netid}...")
    
    # Write new ID
    command = f"ATS3={netid}\r"
    radio.port.write(command.encode())
    time.sleep(0.1)
    radio.port.read(100)
    
    # Verify write
    current_id = read_netid(radio).strip()
    if current_id == netid:
        print(f"Verified!")
    else:
        print(f"Failed to verify -- NetID failed to change to {netid} -- current is {current_id}")

    # Save settings
    radio.port.write("AT&W\r".encode())
    time.sleep(0.1)
    radio.port.read(100)

def flash_params(radio):
    print("Flashing radio parameters...")
    
    params = {
        'EncryptionKey': '12B71897A45F07B0C69595787C3CB99498D3BA732D7C94E610709B5CA2F55DC1',
        'AIR_SPEED': 125,
        'ANT_MODE': 0,
        'DUTY_CYCLE': 100,
        'ECC': 0,
        'ENCRYPTION_LEVEL': 2,
        'FORMAT': 63,
        'LBT_RSSI': 0,
        'MAVLINK': 1,
        'MAX_FREQ': 915000,
        'MAX_WINDOW': 131,
        'MIN_FREQ': 902000,
        'NETID': 111,
        'NUM_CHANNELS': 51,
        'OPPRESEND': 0,
        'RATE/FREQBAND': 0,
        'RTSCTS': 1,
        'SERIAL_SPEED': 57,
        'TXPOWER': 30,
    }

    # Set desired values
    for param, value in params.items():
        if param in radio.params:
            radio.params[param]['desVal'] = value
        else:
            print(f"Warning: Parameter {param} not found in radio configuration")

    # Write parameters
    radio.writeOutAll()
    
    # Save to EEPROM
    print("Saving parameters to EEPROM...")
    radio.save()
    print("Flash complete!")

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ['r', 'w', 'f']:
        print("Usage: python test_net_id.py [r|w|f] [netid]")
        print("  r: read current NetID")
        print("  w: write new NetID (requires netid parameter)")
        print("  f: flash all parameters")
        sys.exit(1)

    if sys.argv[1] == 'w' and len(sys.argv) != 3:
        print("Error: NetID value required for write operation")
        sys.exit(1)

    serial_port = '/dev/tty.usbserial-ABSCDOXC'
    baud_rate = 57600

    # # Check if port exists
    # if serial_port not in [p for p in serial.tools.list_ports.comports()]:
    #     print(f"Error: Port {serial_port} not found")
    #     sys.exit(1)

    radio = RFDConfig()
    radio.port.port = serial_port
    radio.port.baudrate = baud_rate
    radio.port.timeout = 2
    
    try:
        radio.port.open()
    except serial.SerialException as e:
        print(f"Error: Could not open port {serial_port}")
        print("Make sure no other program is using the port")
        print(f"Details: {e}")
        sys.exit(1)

    try:
        enter_command_mode(radio)
        
        if sys.argv[1] == 'r':
            read_netid(radio)
        elif sys.argv[1] == 'w':
            write_netid(radio, sys.argv[2])
        else:  # flash
            flash_params(radio)

        # Exit command mode
        radio.port.write("ATO\r".encode())
        time.sleep(0.1)
    finally:
        radio.port.close()

if __name__ == "__main__":
    main()
