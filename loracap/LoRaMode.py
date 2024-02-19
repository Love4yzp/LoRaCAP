import re
from loracap.ATProtocol import *
from loracap.utility import *
from loracap.macro import *
from typing import Optional

NO_RESPONSE = '_'

class LoRaMode(ATProtocol):

    def __init__(self):
        super(LoRaMode, self).__init__()
        self.__RF_CONFIG_PATTERN = r"F:(\d+), SF(\d+), BW(\d+K), TXPR:(\d+), RXPR:(\d+), POW:(\d+dBm), CRC:(ON|OFF), IQ:(ON|OFF), NET:(ON|OFF)"
        self.rx_mode = False
        self.__rx_pattern = re.compile(r'\+TEST: RX \"([A-Z0-9]+)\"')

    def handle_line(self, line):
        try:
            logging.debug("%r", line)
            match = self.__rx_pattern.search(line)
            if match: 
                extracted_value = match.group(1)
                self.events.put(extracted_value)
            else:
                self.responses.put(line)
        except Exception as e:
            # 记录异常，可能需要进一步的错误处理
            print(f"Error handling line: {e}")

    def handle_event(self, event) -> str:
        print(f"event received: {event}")

    def connection_made(self, transport):
        super(LoRaMode, self).connection_made(transport)
        self.transport.serial.reset_input_buffer()

    def fetch(self, command):
        """
        Directly command set without waiting for response.
        """
        return self.command(command, NO_RESPONSE)

    def command(self, command, response='OK', timeout=5) -> Optional[str]:
        """
        Set an AT command and wait for the response.
        """
        with self.lock:  # ensure that just one thread is sending commands at once
            self.write_line(command)
            while True:
                try:
                    line = self.responses.get(timeout=timeout)
                    logging.debug("%s -> %r", command, line)
                    if response == NO_RESPONSE or response in line:
                        return line
                    elif 'ERROR' in line:
                        return None
                except queue.Empty:
                    raise ATException('AT command timeout ({!r})'.format(command))
    
    def __transmitData(self, type:str, data:str) -> Optional[str]:
        sub_command = ['TXLRPKT', 'TXLRSTR']
        if type not in sub_command:
            raise ValueError('type must be one of {}'.format(sub_command))
        command = f"AT+TEST={type}, \"{data}\"" 
        return self.command(command, 'TX DONE', 10)
    
    def send_str(self, text:str) -> bool:
        return self.__transmitData('TXLRSTR', text) is not None
    
    def send_hex(self, text:str):
        return self.__transmitData('TXLRPKT', text) is not None

    def isConnected(self):
        return 'OK' in self.command("AT", response='OK')

    def __str__(self):
        return f"DevEui: {self.DevEui}, DevAddr: {self.DevAddr}, AppEui: {self.AppEui}"

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
            return self.fetch(f"AT+LOG={level}")
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
        return self.fetch(f'AT+ID=DevAddr,\"{formatted_value}\"')

    @property
    def DevEui(self):
        response =  self.fetch('AT+ID=DevEui')
        return hex_value(response)

    @DevEui.setter
    def DevEui(self, value):
        formatted_value = validate_and_format_hex(value, 16)  # DevEui should be 16 hexadecimal characters
        return self.fetch(f'AT+ID=DevEui,\"{formatted_value}\"')
        
    @property
    def AppEui(self):
        response =  self.fetch('AT+ID=AppEui')
        return hex_value(response)
    
    @AppEui.setter
    def AppEui(self, value):
        formatted_value = validate_and_format_hex(value, 16)  # AppEui should be 16 hexadecimal characters
        return self.fetch(f'AT+ID=AppEui,\"{formatted_value}\"')

    # The keys used for communication
    @property
    def NwkSKey(self):
        logging.error("NwkSKey is write-only for security reasons.")
    
    @NwkSKey.setter
    def NwkSKey(self, value):
        formatted_value = validate_and_format_hex(value, 32)  # AppEui should be 16 hexadecimal characters
        return self.fetch(f'AT+KEY=NWKSKEY,\"{formatted_value}\"')

    @property
    def AppSKey(self):
        logging.error('AppSKey is write-only for security reasons.')

    @AppSKey.setter
    def AppSKey(self, value):
        formatted_value = validate_and_format_hex(value, 32)  # AppEui should be 16 hexadecimal characters
        return self.fetch(f'AT+KEY=AppSKey,\"{formatted_value}\"')

    @property
    def AppKey(self):
        logging.error('AppKey is write-only for security reasons.')
    
    @AppKey.setter
    def AppKey(self, value):
        formatted_value = validate_and_format_hex(value, 32)  # AppEui should be 16 hexadecimal characters
        return self.fetch(f'AT+KEY=AppKey,\"{formatted_value}\"')

    @property
    def mode(self) -> str:
        response = self.fetch('AT+MODE?')
        match = re.search(r"\+MODE: (\w+)", response)
        if match:
            return match.group(1)
        else:
            return ""

    @mode.setter
    def mode(self, value) -> str:
        if value not in LORA_MODE:
            raise ValueError('Invalid mode')
        return self.fetch(f'AT+MODE={value}')
    
    def queryRF(self) -> dict:
        if 'TEST' not in self.mode:
            raise LookupError('Not in TEST mode')
        response = self.command('AT+TEST=?', response='RFCFG', timeout=10)
        match = re.search(self.__RF_CONFIG_PATTERN, response)
        if match:
            return {key: match.group(i) for i, key in enumerate(["Frequency", "Spreading Factor", "Bandwidth", 
                                                                 "Transmit Power", "Receive Power", "Power", 
                                                                 "CRC", "IQ", "Network"], 1)}
        return None

    def setRF(self, freq: int = None, sf: str = None, bd: int = None, 
              tx_pr: int = None, rx_pr: int = None, tx_power: int = None, 
              crc: str = None, iq: str = None, net: str = None) -> bool:
        """
        Set RF Configuration: supports set frequency, SF, band width, TX preamble, RX preamble and TX power settings.
        TX and RX shares all configuration except "preamble length", user could choose different preamble
        length. For LoRa communication, it is strongly recommended to set RX preamble length longer thanx
        TX's. Bandwidth only supports 125KHz / 250KHz / 500KHz.
        :param freq: Frequency(MHz)
        :param sf: Spreading Factor
        :param bd: Bandwidth(KHz)
        :param tx_pr: TX Preamble
        :param rx_pr: RX Preamble
        :param tx_power: TX Power
        :param crc: CRC
        :param iq: IQ
        :param net: Network
        :return: True if successful, False if not
        
        _.setRF(freq=868, sf='SF7', bd=250, tx_pr=8, rx_pr=8, tx_power=14, crc='ON', iq='ON', net='ON') # Update all
        _.setRF(sf='SF7') # Update SF
        """
        SET_CMD_TEMPLATE = 'AT+TEST=RFCFG, {},{},{},{},{},{},{},{},{}\n'
        current_config = self.queryRF()
        if current_config is None:
            raise ValueError('Unable to fetch current RF configuration.')
        freq = str(freq).replace('0', '') if freq is not None else current_config['Frequency'].replace('0', '')
        command = SET_CMD_TEMPLATE.format(
            freq or current_config['Frequency'],
            sf or current_config['Spreading Factor'],
            bd or current_config['Bandwidth'],
            tx_pr or current_config['Transmit Power'],
            rx_pr or current_config['Receive Power'],
            tx_power or current_config['Power'],
            crc.upper() or current_config['CRC'],
            iq.upper() or current_config['IQ'],
            net.upper() or current_config['Network'],
        )
        if re.search(self.__RF_CONFIG_PATTERN, self.fetch(command)):
            return True
        else:
            return False
        
    def __tx_lora(self, type, data): 
        """
        TXLRPKT
        :param type: TXLRPKT (HEX) or TXLRSTR (STR)
        :param data: HEX string or ASCII string
        ---
        // Set test mode
        AT+MODE=TEST
        // Query test mode, check RF configuration
        AT+TEST=?
        // Set RF Configuration
        self.setRF(...)
        // Send HEX format packet
        self.tx_lora('TXLRPKT', '00 AA 11 BB 22 CC') 
        // Send ASCII format packet
        self.tx_lora('TXLRSTR', 'Hello World')
        """ 
        command = f"AT+TEST={type}, \"{data}\"" 
        return self.command(command, "+TEST: TX DONE")

    def sendStr(self, data):
        """
        :param data: ASCII string
        AT+TEST=TXLRSTR,"Hello World"
        """
        return self.__tx_lora('TXLRSTR', data)

    def sendHex(self, data):
        """
        :param data: HEX string
        AT+TEST=TXLRPKT,"AA"
        """
        return self.__tx_lora('TXLRPKT', data)
    
    def rx_lora(self) -> bool:
        """
        After enter test mode, user could enter LoRa packet continuous RX mode through RXLRPKT subcommand.
        """
        self.rx_mode = True
        return self.command('AT+TEST=RXLRPKT','RXLRPKT')