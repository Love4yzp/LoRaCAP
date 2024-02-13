# LoRaE5 Python Code for P2P Communication

This Python code is designed to facilitate P2P communication using a LoRaE5 module on a Raspberry Pi OS (Linux), leveraging the UART functionality for serial communication. The code provides a framework for sending and receiving data over LoRa, including setup, message formatting, and handling.

## Prerequisites

- A Raspberry Pi with Raspberry Pi OS installed.
- A LoRaE5 module connected to the Raspberry Pi via UART.
- Python 3.x installed on the Raspberry Pi.

## Key Components of the Code

- **Serial Communication Setup**: Establishes communication with the LoRaE5 module using the `serial` library.
- **Threading for Asynchronous Reading**: Utilizes the `threading` library to continuously read data from the LoRaE5 module without blocking the main program.
- **Regular Expressions for Data Parsing**: Uses the `re` library to parse and extract hexadecimal values from received messages.
- **LoRaE5 Macro Definitions**: Includes specific settings such as baud rate and timeout values for the LoRaE5 module, defined in `LoRaE5_Macro`.

### Steps to Implement P2P Communication

1. **Hardware Setup**:
   - Connect the LoRaE5 module to the Raspberry Pi via the UART pins.
   - Ensure the module is powered and correctly wired to the Pi's GPIO pins for serial communication.

2. **Software Setup**:
   - Install necessary Python libraries: `pySerial` for serial communication and `threading` for concurrent operations.
   - Define the communication parameters, such as the baud rate and serial port, matching your hardware setup.

3. **Send a Message**:
   - Use the `fetch` or `command` method to send a message.

## Example Use Case

### Switch Mode
```Python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from LoRaTESTMode import *
 
ser = serial.serial_for_url('/dev/ttyS0', baudrate=9600, timeout=1)
with serial.threaded.ReaderThread(ser, LoRaTESTMode) as lorae5:
   print(f"Current Mode: {lorae5.mode}")
   
   print("Change to TEST Mode")
   lorae5.mode = 'TEST'
   
   print("Change to LWOTAA Mode")
   lorae5.mode = 'LWOTAA'
   
   print("Change to LWABP Mode")
   lorae5.mode = 'LWABP'
```

### Update Credential of LoRa-E5
```Python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from LoRaTESTMode import *

ser = serial.serial_for_url('/dev/ttyS0', baudrate=9600, timeout=1)
read_thread = serial.threaded.ReaderThread(ser, LoRaTESTMode)
read_thread.start()
_thread, lorae5 = read_thread.connect()

print("Credentials: \n{}".format(lorae5)) 

print("Updating credentials...")
# lorae5.DevEui = '2CF7F12053700006'
lorae5.DevEui = '2C:F7:F1:20:53:70:00:06'
# lorae5.DevAddr = '3230C9A3'
lorae5.DevAddr = '32:30:C9:A3'
# lorae5.AppEui = '8000000000000009'
lorae5.AppEui = '80:00:00:00:00:00:00:09'

print("Credentials updated!\n{}".format(lorae5))
```