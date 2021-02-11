import serial


class ProtocolError(Exception):
    pass


class Connection:
    def __init__(self):
        self.device = serial.Serial(
            "/dev/ttyUSB0", 9600, parity=serial.PARITY_EVEN, timeout=0.5
        )

    def checksum(self, message):
        result = 0
        for b in message:
            result ^= b
        return result

    def write(self, address, payload):
        size = 2 + len(payload) + 1
        p = bytearray()
        p.append(address)
        p.append(size)
        for x in payload:
            p.append(x)
        p.append(self.checksum(p))
        self.device.write(p)

    def read(self):
        try:
            address, size = self.device.read(2)
            the_rest = self.device.read(size - 2)
        except IndexError:
            return None
        payload, checksum = the_rest[:-1], the_rest[-1]
        if not checksum == self.checksum(
            address.to_bytes(1, "little") + size.to_bytes(1, "little") + payload
        ):
            raise ProtocolError("invalid checksum")
        return payload, address

    def execute(self, address, payload):
        self.write(address, payload)
        echo, _ = self.read()
        reply, sender = self.read()
        if not reply:
            print("No response - Invalid Address ...")
            return None
        status = reply[0]
        if sender != address:
            print("Unexpected address")
            return
        if status != 0xA0:
            if status == 0xA1:
                print("Computer busy")
            elif status == 0xA2:
                print("Invalid parameter")
            elif status == 0xFF:
                print("Invalid command")
            else:
                print("Unknown status")
            return None
        return reply[1:]
