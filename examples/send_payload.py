
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loracap.LoRaMode import *

data_to_send = {
    "temperature": 22.5,
    "humidity": 48, 
}

class uploader(LoRaMode):
    def __init__(self):
        super(LoRaMode, self).__init__()
    
    def handle_line(self, line):
        self.responses.put(line)

if __name__ == '__main__':
    class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKCYAN = '\033[96m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')
    
    ser = serial.serial_for_url('/dev/ttyS0', baudrate=9600, timeout=1)
    with serial.threaded.ReaderThread(ser, uploader) as lorae5:
        lorae5.mode = 'TEST'
        encoded_data = json.dumps(data_to_send)
        
        print(f"{bcolors.OKBLUE}Encoded data: {encoded_data}{bcolors.ENDC}")
        
        status = lorae5.send_str(encoded_data)
        info_color = bcolors.OKGREEN if status else bcolors.FAIL
        ret = "Success" if status else "Fail"
        print(f"{info_color}Send String {ret}{bcolors.ENDC}")
        
        status = lorae5.send_hex(encoded_data)
        info_color = bcolors.OKGREEN if status else bcolors.FAIL
        ret = "Success" if status else "Fail"
        print(f"{info_color}Send Hex {ret}{bcolors.ENDC}") # Would be Failed
        
        status = lorae5.send_hex(encoded_data.encode().hex())
        info_color = bcolors.OKGREEN if status else bcolors.FAIL
        ret = "Success" if status else "Fail"
        print(f"{info_color}Send Hex {ret}{bcolors.ENDC}")