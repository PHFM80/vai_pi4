# vrb_scanner.py
import snap7
from snap7.util import get_bool
import time

class VRBScanner:
    def __init__(self, plc_ip: str):
        self.plc_ip = plc_ip
        self.client = snap7.client.Client()
        
    def conectar(self):
        try:
            self.client.connect(self.plc_ip, 0, 0)
            return self.client.get_connected()
        except Exception as e:
            print(f"[ERROR] No se pudo conectar: {e}")
            return False
    
    def desconectar(self):
        try:
            self.client.disconnect()
        except:
            pass
    
    def escanear_vrb_cambios(self, bytes_to_scan=20, tiempo_monitoreo=60):
        """
        Escanea cambios en las direcciones VRB para identificar cuáles están activas
        """
        print(f"[INFO] Escaneando primeros {bytes_to_scan} bytes VRB por {tiempo_monitoreo} segundos...")
        print("[INFO] Activa/desactiva salidas en el LOGO mientras ejecutas esto")
        
        # Estado inicial
        estado_anterior = {}
        for byte_addr in range(bytes_to_scan):
            for bit_addr in range(8):
                try:
                    data = self.client.read_area(snap7.type.Areas.MK, 0, byte_addr, 1)
                    valor = get_bool(data, 0, bit_addr)
                    estado_anterior[f"VRB{byte_addr}.{bit_addr}"] = valor
                except:
                    estado_anterior[f"VRB{byte_addr}.{bit_addr}"] = None
        
        cambios_detectados = {}
        inicio = time.time()
        
        while (time.time() - inicio) < tiempo_monitoreo:
            for byte_addr in range(bytes_to_scan):
                for bit_addr in range(8):
                    try:
                        data = self.client.read_area(snap7.type.Areas.MK, 0, byte_addr, 1)
                        valor_actual = get_bool(data, 0, bit_addr)
                        direccion = f"VRB{byte_addr}.{bit_addr}"
                        
                        if estado_anterior[direccion] != valor_actual:
                            if direccion not in cambios_detectados:
                                cambios_detectados[direccion] = []
                            
                            cambios_detectados[direccion].append({
                                'tiempo': time.strftime('%H:%M:%S'),
                                'anterior': estado_anterior[direccion],
                                'actual': valor_actual
                            })
                            
                            print(f"[CAMBIO] {direccion}: {estado_anterior[direccion]} → {valor_actual} a las {time.strftime('%H:%M:%S')}")
                            estado_anterior[direccion] = valor_actual
                    except:
                        continue
            
            time.sleep(0.5)  # Escaneo cada 0.5 segundos
        
        return cambios_detectados
    
    def mostrar_estado_actual(self, bytes_to_show=10):
        """
        Muestra el estado actual de las primeras direcciones VRB
        """
        print(f"\n[INFO] Estado actual de VRB (primeros {bytes_to_show} bytes):")
        
        for byte_addr in range(bytes_to_show):
            try:
                data = self.client.read_area(snap7.type.Areas.MK, 0, byte_addr, 1)
                print(f"VRB{byte_addr}: ", end="")
                for bit_addr in range(8):
                    valor = get_bool(data, 0, bit_addr)
                    print(f"{bit_addr}={int(valor)} ", end="")
                print()
            except Exception as e:
                print(f"VRB{byte_addr}: ERROR - {e}")
    
    def test_direccion_especifica(self, direccion: str, tiempo=30):
        """
        Monitorea una dirección específica por un tiempo determinado
        """
        print(f"[INFO] Monitoreando {direccion} por {tiempo} segundos...")
        
        if not direccion.startswith("VRB"):
            print("[ERROR] Dirección debe empezar con VRB")
            return
        
        try:
            byte_str, bit_str = direccion[3:].split(".")
            byte_addr = int(byte_str)
            bit_addr = int(bit_str)
        except:
            print("[ERROR] Formato de dirección inválido. Use: VRBx.y")
            return
        
        inicio = time.time()
        estado_anterior = None
        
        while (time.time() - inicio) < tiempo:
            try:
                data = self.client.read_area(snap7.type.Areas.MK, 0, byte_addr, 1)
                valor_actual = get_bool(data, 0, bit_addr)
                
                if estado_anterior != valor_actual:
                    print(f"[{time.strftime('%H:%M:%S')}] {direccion}: {estado_anterior} → {valor_actual}")
                    estado_anterior = valor_actual
                
                time.sleep(0.5)
            except Exception as e:
                print(f"[ERROR] {e}")
                break

# Función principal para usar el escáner
def main():
    scanner = VRBScanner("192.168.0.1")
    
    if not scanner.conectar():
        print("[ERROR] No se pudo conectar al PLC")
        return
    
    print("=== ESCÁNER DE DIRECCIONES VRB ===")
    print("1. Mostrar estado actual")
    print("2. Escanear cambios (recomendado)")
    print("3. Monitorear dirección específica")
    
    opcion = input("Selecciona una opción (1-3): ")
    
    try:
        if opcion == "1":
            scanner.mostrar_estado_actual()
        
        elif opcion == "2":
            print("\n[INSTRUCCIONES]")
            print("- Activa y desactiva salidas manualmente en el LOGO")
            print("- El escáner detectará qué direcciones cambian")
            print("- Presiona Ctrl+C para terminar antes")
            
            cambios = scanner.escanear_vrb_cambios()
            
            print("\n=== RESUMEN DE CAMBIOS DETECTADOS ===")
            if cambios:
                for direccion, lista_cambios in cambios.items():
                    print(f"\n{direccion}: {len(lista_cambios)} cambios detectados")
                    for cambio in lista_cambios[-3:]:  # Últimos 3 cambios
                        print(f"  {cambio['tiempo']}: {cambio['anterior']} → {cambio['actual']}")
            else:
                print("No se detectaron cambios. Verifica que las salidas estén funcionando.")
        
        elif opcion == "3":
            direccion = input("Ingresa la dirección a monitorear (ej: VRB1.0): ")
            scanner.test_direccion_especifica(direccion)
    
    except KeyboardInterrupt:
        print("\n[INFO] Escaneo interrumpido por el usuario")
    
    finally:
        scanner.desconectar()
        print("[INFO] Desconectado del PLC")

if __name__ == "__main__":
    main()