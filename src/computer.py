from connection import Connection


class Computer:
    def __init__(self):
        self.connection = Connection()

    def query(self, payload):
        return self.connection.execute(0x12, payload)

    def get_status(self):
        result = self.query(bytearray.fromhex("0b03"))
        air_temp = result[22] * 0.75 - 48
        engine_temp = result[23] * 0.75 - 48
        battery_voltage = result[28] * 0.1
        status_obj = {
            "Air temperature": air_temp,
            "Engine temperature": engine_temp,
            "Battery voltage": battery_voltage,
        }
        return status_obj
