import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loracap.LoRaMode import *

class Switch(LoRaMode):
    def __init__(self):
        super(LoRaMode, self).__init__()
    def handle_line(self, line):
        """
        We don't need any events for this example.
        """
        self.responses.put(line)

if __name__ == '__main__':
    ser = serial.serial_for_url('/dev/ttyS0', baudrate=9600, timeout=1)
    with serial.threaded.ReaderThread(ser, Switch) as lorae5:
        print(f"Current Mode: {lorae5.mode}")
        
        print("Change to LWOTAA Mode")
        lorae5.mode = 'LWOTAA'
        
        print("Change to LWABP Mode")
        lorae5.mode = 'LWABP'

        print("Change to TEST Mode")
        lorae5.mode = 'TEST'