from enum import Enum

# Constants
DEFAULT_TIMEOUT = 3000  # milliseconds to max wait for a command to get a response
DEFAULT_TIMEOUT_ReTx = 1000  # milliseconds to max wait for a command to get a response for transferPacketWithConfirmedReTransmission command
DEFAULT_TIMEWAIT = 100  # DO NOT CHANGE: milliseconds to wait after issuing command via serial and not getting an specific response

AT_NO_ACK = None  # For not checking the command response in order to send a command error
# PARAMETERS FIXED
BEFFER_LENGTH_MAX = 512  # reception buffer size. Commands response can be up to 400 bytes according to data sheet examples
MAC_COMMAND_FLAG = "MACCMD:"
kLOCAL_BUFF_MAX = 64
RXWIN1_DELAY = 1000  # DO NOT CHANGE: milliseconds to wait after a transmition is being made in order to open RXWIN1 for reception
RXWIN2_DELAY = 2000  # DO NOT CHANGE: milliseconds to wait after a transmition is being made in order to open RXWIN1 for reception

LORA_BAUDRATE_DEFAULT = 9600

# Power consumption measures with the module at 3.3V
SLEEPPOWER_mA = 0.021  # measured: power consumption when the module is in sleep mode
RXPOWER_mA = 5.65  # measured mA when LoRa-E5 module is working as a receptor
TXPOWER_00dBm_mA = 41.0  # NOT MEASURED. ESTIMATED based on table
TXPOWER_02dBm_mA = 41.5  # measured 41.5 mA at 868 Mhz
TXPOWER_04dBm_mA = 48.1  # measured 48.1 mA at 868 Mhz
TXPOWER_06dBm_mA = 53.5  # measured 53.5 mA at 868 Mhz
TXPOWER_08dBm_mA = 60.6  # measured 60.6 mA at 868 Mhz
TXPOWER_10dBm_mA = 68.3  # measured 68.3 mA at 868 Mhz
TXPOWER_12dBm_mA = 77.3  # measured 77.3 mA at 868 Mhz
TXPOWER_14dBm_mA = 86.8  # measured 86.8 mA at 868 Mhz
TXPOWER_16dBm_mA = 86.8  # Module says that 16 dBm were set up properly, measured 86.8 mA at 868 Mhz. Not checked if the effective TX

# class DeviceID(Enum):
#     DevAddr = 0
#     DevEui = 1
#     AppEui = 2


class BaudRateBpsSupported(Enum):
    BR_9600 = 9600
    BR_38400 = 38400
    BR_115200 = 115200

class DebugLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3
    FATAL = 4
    PANIC = 5
    QUIET = 6

class ClassType(Enum):
    CLASS_A = 0
    CLASS_C = 1

class PhysicalType(Enum):
    UNINIT = -1
    EU434 = 0
    EU868 = 1
    US915 = 2
    US915HYBRID = 3
    US915OLD = 4
    AU915 = 5
    AS923 = 6
    CN470 = 7
    CN779 = 8
    KR920 = 9
    CN470PREQUEL = 10
    STE920 = 11
    IN865 = 12
    RU864 = 13
    UNDEF = 14

class DeviceMode(Enum):
    LWABP = 0
    LWOTAA = 1
    TEST = 2

class OtaaJoinCmd(Enum):
    JOIN = 0
    FORCE = 1

class WindowDelay(Enum):
    RECEIVE_DELAY1 = 0
    RECEIVE_DELAY2 = 1
    JOIN_ACCEPT_DELAY1 = 2
    JOIN_ACCEPT_DELAY2 = 3

class BandWidth(Enum):
    BWX = 0
    BW50 = 50 #kbps
    BW125 = 125
    BW250 = 250
    BW500 = 500

class SpreadingFactor(Enum):
    SF12 = 12
    SF11 = 11
    SF10 = 10
    SF9 = 9
    SF8 = 8
    SF7 = 7
    SFX = 0

class DataRate(Enum):
    DR0 = 0
    DR1 = 1
    DR2 = 2
    DR3 = 3
    DR4 = 4
    DR5 = 5
    DR6 = 6
    DR7 = 7
    DR8 = 8
    DR9 = 9
    DR10 = 10
    DR11 = 11
    DR12 = 12
    DR13 = 13
    DR14 = 14
    DR15 = 15
    DRNONE = 16  # USED FOR KNOWING THAT DATA RATE WAS NOT SET. DO NOT REMOVE

