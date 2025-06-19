#connection.py
import snap7

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

    def write_bool(self, area: str, address: int, value: bool):
        try:
            byte = 1 if value else 0
            self.client.write_area(snap7.type.Areas.MK, 0, address, bytes([byte]))
        except Exception as e:
            print(f"[ERROR] No se pudo escribir en {area}{address}: {e}")
            raise

