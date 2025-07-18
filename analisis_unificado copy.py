from pathlib import Path
import csv
import re
from typing import List, Tuple
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import subprocess
import sys
import pandas as pd
import logging

CARPETA_LOGS = Path('./logs')
CARPETA_RESULTADOS = Path('resultados')
CARPETA_RESULTADOS.mkdir(exist_ok=True)
REGEX_FECHA = re.compile(r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}\.\d{3}')
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def validar_estructura_log(linea: str) -> bool:
    """Valida que una línea de log tenga la estructura esperada."""
    partes = linea.split('|')
    return (
        len(partes) >= 5 and 
        REGEX_FECHA.match(partes[0]) and
        partes[4].strip() in {'INF', 'WRN', 'ERR'}
    )
    # ...existing code...

def obtener_archivos_log(carpeta: Path) -> List[Path]:
    if not carpeta.exists():
        logging.error(f"La carpeta '{carpeta}' no existe. Por favor créala y agrega tus archivos .Log.")
        sys.exit(1)
    return [f for f in carpeta.iterdir() if f.suffix.lower() == '.log']

def _procesar_linea_buffer(buffer: List[str], total_estados: Counter, errores: List[str], warnings: List[str]):
    """Procesa un buffer de líneas que componen una única entrada de log."""
    if not buffer:
        return

    linea_completa = ' '.join(buffer)
    if not validar_estructura_log(linea_completa):
        logging.warning(f"Estructura de log no válida - {linea_completa[:50]}...")
        return
    partes = linea_completa.split('|')
    estado = partes[4].strip() if len(partes) > 4 else ''
    if estado:
        total_estados[estado] += 1
        if estado == 'ERR':
            errores.append(linea_completa)
        elif estado == 'WRN':
            warnings.append(linea_completa)

def analizar_logs(archivos_log: List[Path]) -> Tuple[Counter, List[str], List[str]]:
    total_estados: Counter = Counter()
    errores: List[str] = []
    warnings: List[str] = []

    for archivo_log in archivos_log:
        logging.info(f"Procesando archivo: {archivo_log}")
        try:
            with archivo_log.open('r', encoding='utf-8') as f:
                buffer: List[str] = []
                for linea in f:
                    linea = linea.rstrip('\n')
                    if REGEX_FECHA.match(linea):
                        _procesar_linea_buffer(buffer, total_estados, errores, warnings)
                        buffer = [linea] # Iniciar nuevo buffer
                    elif buffer: # Solo agregar si ya estamos en un buffer
                        buffer.append(linea)
                _procesar_linea_buffer(buffer, total_estados, errores, warnings) # Procesar el último buffer
        except Exception as e:
            logging.error(f"Ocurrió un error al procesar {archivo_log}: {e}")
    return total_estados, errores, warnings

def guardar_errores_csv(errores: List[str], carpeta_resultados: Path, nombre_archivo: str = 'errores_completos.csv') -> Path:
    """Guarda los errores en un archivo CSV con columnas bien definidas."""
    archivo_salida = carpeta_resultados / nombre_archivo
    with archivo_salida.open(mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Fecha', 'Estado', 'Caja', 'Modulo', 'Flujo', 'Mensaje'])
        for linea in errores:
            partes = [p.strip() for p in linea.split('|')]
            if len(partes) < 8:
                logging.warning(f"Línea con formato inesperado: {linea[:50]}...")
                continue
            fecha = partes[0]
            estado = partes[4]
            caja = partes[5]
            modulo = partes[6]
            flujo = partes[7]
            mensaje = '|'.join(partes[8:])
            writer.writerow([fecha, estado, caja, modulo, flujo, mensaje])
    return archivo_salida

def mostrar_estadisticas_estados(total_estados: Counter):
    total_lineas = sum(total_estados.values())
    print("\n--- Estadísticas de Estados ---")
    print(f"Total de líneas procesadas: {total_lineas}")
    if total_lineas == 0:
        print("No hay líneas para analizar.")
        return
    for estado, cantidad in total_estados.items():
        porcentaje = (cantidad / total_lineas) * 100
        print(f"{estado}: {cantidad} ({porcentaje:.2f}%)")
    estado_mas_frecuente = total_estados.most_common(1)[0]
    print(f"Estado más frecuente: {estado_mas_frecuente[0]} ({estado_mas_frecuente[1]} veces)")

def graficar_estadisticas_estados(total_estados: Counter, carpeta_resultados: Path):
    if not total_estados:
        print("No hay datos para graficar.")
        return
    estados = list(total_estados.keys())
    cantidades = list(total_estados.values())
    plt.figure(figsize=(8, 5))
    bars = plt.bar(estados, cantidades, color='skyblue')
    plt.xlabel('Estado')
    plt.ylabel('Cantidad')
    plt.title('Conteo de Estados en los Logs')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    # Etiquetas encima de cada barra
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, str(int(yval)), ha='center', va='bottom')
    plt.close()
    # Imagen NO se guarda en resultados

def guardar_estadisticas_estados_csv(total_estados: Counter, carpeta_resultados: Path):
    archivo_salida = carpeta_resultados / 'estadistica_estados.csv'
    total_lineas = sum(total_estados.values())
    with archivo_salida.open(mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Estado', 'Cantidad', 'Porcentaje'])
        for estado, cantidad in total_estados.items():
            porcentaje = (cantidad / total_lineas) * 100 if total_lineas else 0
            writer.writerow([estado, cantidad, f"{porcentaje:.2f}"])
    # print(f"Resumen de estados guardado en '{archivo_salida}'.")

def analizar_codigos_excepcion(archivo_errores):
    if not archivo_errores.exists():
        print(f"No se encontró el archivo {archivo_errores}")
        return
    df = pd.read_csv(archivo_errores)
    codigos = []
    # Regex: busca "Exception code" seguido de cualquier cantidad de espacios, dos puntos o tabulaciones, y luego el código
    patron = re.compile(r'Exception code\s*[:\t ]+\s*([A-Z0-9_]+)', re.IGNORECASE)
    for mensaje in df['Mensaje']:
        if isinstance(mensaje, str):
            encontrados = patron.findall(mensaje)
            codigos.extend(encontrados)
    conteo = Counter(codigos)
    print("\n--- Conteo de Exception code en mensajes de error ---")
    for codigo, cantidad in conteo.most_common():
        print(f"{codigo}: {cantidad} veces")
    if not conteo:
        print("No se encontraron códigos de excepción en los mensajes.")

def main():
    archivos_log = obtener_archivos_log(CARPETA_LOGS)
    if not archivos_log:
        return

    total_estados, errores, warnings = analizar_logs(archivos_log)

    # Unificar errores y warnings en un solo archivo
    errores_unificados = errores + warnings
    archivo_errores = guardar_errores_csv(errores_unificados, CARPETA_RESULTADOS)

    graficar_estadisticas_estados(total_estados, CARPETA_RESULTADOS)
    guardar_estadisticas_estados_csv(total_estados, CARPETA_RESULTADOS)

    # Mostrar resumen final
    mostrar_estadisticas_estados(total_estados)
    logging.info(f"\n✅ Se guardaron {len(errores_unificados)} errores/warnings en '{archivo_errores}'.")
    logging.info("Archivos generados:")
    logging.info(f" - Errores y warnings completos: {archivo_errores}")
    logging.info(f" - Estadística de estados (csv): {CARPETA_RESULTADOS / 'estadistica_estados.csv'}")
    
    analizar_codigos_excepcion(archivo_errores)

if __name__ == '__main__':
    main()

    # Lanza el dashboard de Streamlit automáticamente solo si no está ya abierto
    import psutil
    def is_streamlit_running():
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                if proc.info['name'] and 'streamlit' in proc.info['name'].lower():
                    return True
                if proc.info['cmdline'] and any('streamlit' in str(arg).lower() for arg in proc.info['cmdline']):
                    return True
            except Exception:
                continue
        return False

    if not is_streamlit_running():
        try:
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
            logging.info("\nSe está abriendo el dashboard en tu navegador...")
        except Exception as e:
            logging.error(f"\n❌ No se pudo abrir el dashboard automáticamente: {e}")
            logging.info("   Para verlo, ejecuta en tu terminal: streamlit run dashboard.py")
