from machine import UART, Pin
from utime import ticks_ms, sleep


NEW_LINE = "\r\n"
BAUDRATE = 115200


class SIM800L:
    def __init__(self, tx_pin=0, rx_pin=1, power_pin=22, debug=False):
        self.modem = UART(0, BAUDRATE, tx=Pin(tx_pin), rx=Pin(rx_pin))
        self.power = Pin(power_pin, Pin.OUT)
        self.debug = debug
        self.reboot()
        self._ensure_connected_to_network()

    def exec(self, command, timeout=1000, eol=NEW_LINE):
        response = self.query(command, timeout, eol)
        if "OK" not in response:
            raise Exception("Unknown response for '%s': %s" %
                            (command, response))

    def query(self, command, timeout=1000, eol=NEW_LINE):
        if self.debug:
            print("[Debug] AT Write - %s\n" % command)
        self.modem.write((command + eol).encode())
        response = self._read_buffer(timeout)
        if self.debug:
            print("[Debug] AT Read - %s\n" % response)
        return response

    def send_sms(self, number, message):
        response = self.query('AT+CMGS="%s"' % number, eol="\n")
        if ">" not in response:
            raise Exception("Unknown response: %s" % response)
        self.exec(message, timeout=10000, eol="\x1A")

    def reboot(self, attempts=10):
        self._power_cycle()
        while attempts > 0:
            try:
                self.exec("AT")  # Check modem ready
                self.exec("ATE1")  # Enable command echo
                self.exec("AT+CMGF=1")  # Enable SMS text mode
                return
            except:
                attempts -= 1
                sleep(1)
        raise Exception("Failed to reboot")

    def _ensure_connected_to_network(self, attempts=50):
        while attempts > 0:
            try:
                network_response = self.query("AT+COPS?").split(NEW_LINE)[1]
                if "+COPS:" in network_response and "," in network_response:
                    return
            except:
                attempts -= 1
                sleep(1)
        raise Exception("Failed to connect")

    def _power_cycle(self):
        self.power.value(1)
        sleep(1.5)
        self.power.value(0)

    def _read_buffer(self, timeout):
        buffer = bytes()
        now = ticks_ms()
        while (ticks_ms() - now) < timeout and len(buffer) < 1025:
            if self.modem.any():
                buffer += self.modem.read(1)
        return buffer.decode()
