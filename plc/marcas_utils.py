# \plc\marcas_utils.py

def convertir_marca_logo_a_bytebit(marca_logo: str) -> tuple[int, int]:
    """
    Convierte 'M1', 'M2', ..., 'M32' a (byte, bit) reales para Snap7.
    """
    import re
    match = re.match(r'^M(\d+)$', marca_logo.upper())
    if not match:
        raise ValueError(f"Formato de marca inválido: {marca_logo}")
    
    numero = int(match.group(1)) - 1  # M1 → 0
    byte = numero // 8
    bit = numero % 8
    return byte, bit
