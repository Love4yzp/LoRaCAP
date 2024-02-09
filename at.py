from serial import Serial
import threading
import time
from LoRaE5_Macro import *
import re

def hex_value(line):
    """
    extract hex value
    """
    pattern = r'\+\w+:\s*\w+,\s*([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){2,7})'
    match = re.search(pattern, line)
    if match:
        return match.group(1)  # 返回匹配的十六进制字符串
    else:
        return None

def validate_and_format_hex(value, expected_length):
    """
    验证和格式化十六进制字符串。
    :param value: 原始字符串值。
    :param expected_length: 期望的十六进制字符长度。
    :return: 格式化后的十六进制字符串。
    """
    # 移除非十六进制字符
    cleaned_value = ''.join(filter(str.isalnum, value)).upper()
    # 验证长度
    if len(cleaned_value) != expected_length:
        raise ValueError(f"Expected hex string of length {expected_length}, got {len(cleaned_value)}")
    return cleaned_value
    
# LORA_MODE = {
#     0: "LoRa",
#     1: "Fsk",
#     2: "p2p"
# }

class atc:
    def __init__(self, port='/dev/ttyS0', baud_rate=LORA_BAUDRATE_DEFAULT, timeout=DEFAULT_TIMEWAIT):
        self.running = True  # 新增线程运行控制标志
        self.open(port, baud_rate, timeout)        
        
        self.received_data = ""
        self.data_ready = threading.Event()
        self.read_thread = threading.Thread(target=self.read_from_port)
        self.read_thread.daemon = True
        self.read_thread.start()
        
        # LoRa
        self.lowpower_auto = False
        self.adpative_DR = True
        self.freq_band = 0

        # self.mode = LoRa_mode
    
    def set_mode(self,mode):
        self.mode = mode
    
    @property
    def serial(self) -> Serial:
        if not self._ser.is_open:
            raise ValueError("Serial port is not open.")
        return self._ser

    def close(self):
        self.running = False  # 设置运行标志为False，使得read_from_port线程可以优雅地停止
        self.read_thread.join()  # 等待线程真正结束
        self._ser.close()
        print("Closed serial port.")

    def open(self, serial_port='/dev/ttyS0', baud_rate=LORA_BAUDRATE_DEFAULT, timeout=DEFAULT_TIMEWAIT):
        if hasattr(self, '_ser') and self._ser.is_open:
            print(f"Closed {self._ser.port}")
            self.close()
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self._ser = Serial(serial_port, baud_rate, timeout=timeout)
        print(f"Opened {serial_port}.")

    def _send_command(self, command: str):
        """Send AT command"""
        self._ser.write(command.encode())
        self._ser.flush()

    def read_from_port(self):
        """Continuously read serial data in a background thread"""
        while self.running:
            try:
                if self._ser.in_waiting > 0:
                    received_char = self._ser.read(self._ser.in_waiting).decode()  # Read all available data
                    self.received_data += received_char
                    self.data_ready.set()
                else:
                    time.sleep(0.01)
            except self.serial.SerialException:
                break  # Exit the loop if the serial port is closed during reading

    def _wait_for_ack(self, ack, timeout_ms = DEFAULT_TIMEOUT_ReTx) -> bool:
        """Wait for a specific response, ensuring a complete message is received"""
        start_time = time.time() * 1000
        while (time.time() * 1000 - start_time) < timeout_ms:
            if self.data_ready.is_set():
                # Check if a complete response is received (e.g., response ending with a newline)
                if self.received_data.endswith('\r\n') and (ack is None or ack in self.received_data):
                    # print("Received expected ack")
                    return True
                self.data_ready.clear()  # Reset the event, waiting for the next data
            time.sleep(0.01)  # Avoid intensive polling
        # print("Timeout or no ack received")
        return False

    def fetch(self, command: str, timeout_ms: int = DEFAULT_TIMEOUT_ReTx) -> str:
        return self.fetch_ack(command, AT_NO_ACK, timeout_ms)

    def fetch_ack(self, command: str, ack:str, timeout_ms: int = DEFAULT_TIMEOUT_ReTx) -> str:
        # If the command is None or any other condition that should return an empty string
        # if not command:
        #     return ""
        # self.received_data = ''  # Reset received data
        # command += '\n'
        # self._send_command(command)  # Send command
        # # if self.lowpower_auto:
        # #     self.__send_command('AT+LPOFF\n')
        # if self._wait_for_ack(ack, timeout_ms):
        #     # Strip leading and trailing whitespace/newlines for cleaner response
        #     return self.received_data.strip()
        # return ""
        pass
        print(f"<<< {command}")  # 日志记录发送的命令
        self.received_data = ''  # 重置接收数据
        command += '\n'
        self._send_command(command)  # 发送命令
        if self._wait_for_ack(None, timeout_ms):
            response = self.received_data.strip()  # 清理响应数据
            print(f">>> {response}")  # 日志记录接收到的响应
            return response
        return ""
    # Debug
    @property
    def LogLevel(self):
        raise AttributeError("""
              You can only set the log level
              DEBUG/INFO/WARN/ERROR/FATAL/PANIC/QUIET
              LogLevel = QUIET
              LogLevel = quiet
              """)
    
    @LogLevel.setter
    def LogLevel(self, level:str):
        level = level.upper()
        level_list = [x.name for x in DebugLevel]
        print("LogLevel = ", level)
        if level in level_list:
            return self.fetch(f"AT+LOG={level}\n")
        raise ValueError("Invalid Debug Level")
    
    # Device Identification

    @property
    def DevAddr(self):
        """'+ID: DevAddr, 32:30:C9:A3"""
        response = self.fetch('AT+ID=DevAddr')
        return hex_value(response)

    @DevAddr.setter
    def DevAddr(self, value):
        formatted_value = validate_and_format_hex(value, 8)  # DevAddr should be 8 hexadecimal characters
        return self.fetch(f'AT+ID=DevAddr,\"{formatted_value}\"\n', DEFAULT_TIMEWAIT * 2)

    @property
    def DevEui(self):
        response =  self.fetch('AT+ID=DevEui')
        return hex_value(response)

    @DevEui.setter
    def DevEui(self, value):
        formatted_value = validate_and_format_hex(value, 16)  # DevEui should be 16 hexadecimal characters
        return self.fetch(f'AT+ID=DevEui,\"{formatted_value}\"\n', DEFAULT_TIMEWAIT * 2)
        
    @property
    def AppEui(self):
        response =  self.fetch('AT+ID=AppEui')
        return hex_value(response)
    
    @AppEui.setter
    def AppEui(self, value):
        formatted_value = validate_and_format_hex(value, 16)  # AppEui should be 16 hexadecimal characters
        return self.fetch(f'AT+ID=AppEui,\"{formatted_value}\"\n', DEFAULT_TIMEWAIT * 2)

    #End of Device Identification

    # The keys used for communication
    @property
    def NwkSKey(self):
        raise AttributeError('NwkSKey is write only')
    
    @NwkSKey.setter
    def NwkSKey(self, value):
        formatted_value = validate_and_format_hex(value, 32)  # AppEui should be 16 hexadecimal characters
        return self.fetch(f'AT+KEY=NWKSKEY,\"{formatted_value}\"\n', DEFAULT_TIMEWAIT * 2)

    
    @property
    def AppSKey(self):
        raise AttributeError('AppSKey is write only')

    
    @AppSKey.setter
    def AppSKey(self, value):
        formatted_value = validate_and_format_hex(value, 32)  # AppEui should be 16 hexadecimal characters
        return self.fetch(f'AT+KEY=AppSKey,\"{formatted_value}\"\n', DEFAULT_TIMEWAIT * 2)


    @property
    def AppKey(self):
        raise AttributeError('AppKey is write only')
    
    @AppKey.setter
    def AppKey(self, value):
        formatted_value = validate_and_format_hex(value, 32)  # AppEui should be 16 hexadecimal characters
        return self.fetch(f'AT+KEY=AppKey,\"{formatted_value}\"\n', DEFAULT_TIMEWAIT * 2)

    
if __name__ == '__main__':
    # 使用示例
    at_serial = atc()
    # at_serial = atc('/dev/ttyS0')
    # at_serial.fetch('AT')
    # at_serial.fetch('AT+VER?')
    print( "DevEui: ", at_serial.DevEui, "AppEui: ", at_serial.AppEui,"DevAddr: ", at_serial.DevAddr)
    # at_serial.LogLevel = 'QUIET'