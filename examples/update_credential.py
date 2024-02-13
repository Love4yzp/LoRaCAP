import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loracap.LoRaMode import *

class credentials(LoRaMode):
    def __init__(self):
        super(LoRaMode, self).__init__()
    def handle_line(self, line):
        """
        We don't need any events for this example.
        """
        self.responses.put(line)

if __name__ == "__main__":
    ser = serial.serial_for_url('/dev/ttyS0', baudrate=9600, timeout=1)
    read_thread = serial.threaded.ReaderThread(ser, credentials)
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