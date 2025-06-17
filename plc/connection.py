#connection.py
from snap7.logo import Logo

class LOGOConnection:
    def __init__(self, ip: str):
        self.ip = ip
        self.client = Logo()  # Crear instancia sin parámetros
        self.client.connect(self.ip, 0, 0)  # rack=0, slot=0

    def conectar(self) -> None:
        try:
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


