
#connection.py
import snap7
from snap7.type import Areas

class LOGOConnection:
    def __init__(self, ip: str):
        self.ip = ip
        self.client = snap7.client.Client()

    def conectar(self) -> None:
        try:
            self.client.connect(self.ip, 0, 0)
            if self.client.get_connected():
                print(f"Conectado a PLC en {self.ip}")
            else:
                print(f"No se pudo conectar a {self.ip}")
        except Exception as e:
            print(f"[ERROR] Fallo conexión al PLC {self.ip}: {e}")

    def desconectar(self) -> None:
        try:
            self.client.disconnect()
            print(f"Desconectado de PLC en {self.ip}")
        except Exception as e:
            print(f"[ERROR] Fallo al desconectar del PLC {self.ip}: {e}")

    def read_bool(self, area: str, direccion: int, bit: int = 0) -> bool:
        try:
            resultado = self.client.read_area(Areas.MK, 0, direccion, 1)
            byte = resultado[0]
            return bool((byte >> bit) & 1)
        except Exception as e:
            print(f"[ERROR] Al leer marca {area}{direccion} bit {bit}: {e}")
            return False

    def write_bool(self, area: str, direccion: int, value: bool, bit: int = 0):
        try:
            byte_actual = self.client.read_area(Areas.MK, 0, direccion, 1)[0]
            if value:
                byte_modificado = byte_actual | (1 << bit)
            else:
                byte_modificado = byte_actual & ~(1 << bit)
            self.client.write_area(Areas.MK, 0, direccion, bytes([byte_modificado]))
        except Exception as e:
            print(f"[ERROR] No se pudo escribir en {area}{direccion} bit {bit}: {e}")
            raise