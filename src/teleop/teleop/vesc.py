import can

class Vesc:

    def __init__(self):
        pass

    def id_conversion(device_id: int, command_id: int) -> int:
        return (command_id << 8) | device_id

    def signal_conversion(msg_data: int, bytes_range: int) -> list[int]:
        data: int = msg_data 
        temp_data: list[int] = []

        # convert signal to byte array, 2 bytes each
        for i in range(bytes_range - 1, -1, -1):
            temp_data.append((data >> (8*i)) & 0xff)

        return temp_data 
    

    