
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loracap.LoRaMode import *

def payload():
    return 'Hello World!'

def coder(data):
    pass

class demo(LoRaMode):
    def __init__(self):
        super(LoRaMode, self).__init__()
    
    def handle_line(self, line):
        if line.startswith('+TEST: RX'): # Only parse the data from this response event.
            self.events.put(line)
        else:
            self.responses.put(line)
    
    def handle_event(self, event):
        """Handle events and command responses starting with '+...'"""
        if event.startswith('+TEST: RX'):
            self.event_responses.put(event)
            print(f"event >>> {event}")
        else:
            logging.warning('unhandled event: {!r}'.format(event))

    def decoder(self, data):
        return data
    
    def coder(self, data):
        return data

# if __name__ == '__main__':
ser = serial.serial_for_url('/dev/ttyS0', baudrate=9600, timeout=1)
read_thread = serial.threaded.ReaderThread(ser, demo)
read_thread.start()
_thread, lorae5 = read_thread.connect()
# ser = serial.serial_for_url('/dev/ttyS0', baudrate=9600, timeout=1)
# with serial.threaded.ReaderThread(ser, demo) as lorae5:
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(message)s')
# lorae5.mode = 'TEST'
print(f"lorae5 Current Mode: {lorae5.mode}")
