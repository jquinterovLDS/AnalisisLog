from pathlib import Path
import csv
import re
from datetime import datetime # No se usa directamente, pero es bueno tenerla por si acaso
from typing import List
from collections import Counter, defaultdict
import matplotlib.pyplot as plt  # <-- Agrega esto al inicio
import subprocess
import sys

CARPETA_LOGS = Path('./logs')
CARPETA_RESULTADOS = Path('resultados')
CARPETA_RESULTADOS.mkdir(exist_ok=True)
REGEX_FECHA = re.compile(r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}\.\d{3}')

def obtener_archivos_log(carpeta: Path) -> List[Path]:
    if not carpeta.exists():
        print(f"La carpeta '{carpeta}' no existe. Por favor créala y agrega tus archivos .Log.")
        exit()
    return [f for f in carpeta.iterdir() if f.suffix.lower() == '.log']

def _procesar_linea_buffer(buffer: List[str], total_estados: Counter, errores: List[str]):
    """Procesa un buffer de líneas que componen una única entrada de log."""
    if not buffer:
        return

    linea_completa = ' '.join(buffer)
    partes = linea_completa.split('|')
    if len(partes) > 5:
        estado = partes[4].strip()
        total_estados[estado] += 1
        if estado == 'ERR':
            errores.append(linea_completa)

def analizar_logs(archivos_log: List[Path]) -> (Counter, List[str]):
    total_estados = Counter()
    errores = []

    for archivo_log in archivos_log:
        print(f"Procesando archivo: {archivo_log}")
        try:
            with archivo_log.open('r', encoding='utf-8') as f:
                buffer = []
                for linea in f:
                    linea = linea.rstrip('\n')
                    if REGEX_FECHA.match(linea):
                        _procesar_linea_buffer(buffer, total_estados, errores)
                        buffer = [linea] # Iniciar nuevo buffer
                    elif buffer: # Solo agregar si ya estamos en un buffer
                        buffer.append(linea)
                _procesar_linea_buffer(buffer, total_estados, errores) # Procesar el último buffer
        except Exception as e:
            print(f"Ocurrió un error al procesar {archivo_log}: {e}")
    return total_estados, errores

def guardar_errores_csv(errores: List[str], carpeta_resultados: Path) -> Path:
    """Guarda los errores en un archivo CSV con columnas bien definidas."""
    archivo_salida = carpeta_resultados / 'errores_completos.csv'
    with archivo_salida.open(mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Fecha', 'Estado', 'Caja', 'Modulo', 'Flujo', 'Mensaje'])
        for linea in errores:
            partes = [p.strip() for p in linea.split('|')]
            # Rellenar con cadenas vacías si faltan columnas para evitar IndexError
            partes.extend([''] * (9 - len(partes)))

            fecha = partes[0]
            estado = partes[4]
            caja = partes[5]
            modulo = partes[6]
            flujo = partes[7]
            # Unir el resto como mensaje, ya que puede contener '|'
            mensaje = '|'.join(partes[8:])

            writer.writerow([fecha, estado, caja, modulo, flujo, mensaje])

    print(f"\n✅ Se guardaron {len(errores)} errores en '{archivo_salida}'.")
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
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, int(yval), ha='center', va='bottom')
    ruta_imagen = carpeta_resultados / 'estadistica_estados.png'
    plt.savefig(ruta_imagen)
    plt.close()
    print(f"Imagen de estadística de estados guardada en '{ruta_imagen}'.")

def guardar_estadisticas_estados_csv(total_estados: Counter, carpeta_resultados: Path):
    archivo_salida = carpeta_resultados / 'estadistica_estados.csv'
    total_lineas = sum(total_estados.values())
    with archivo_salida.open(mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Estado', 'Cantidad', 'Porcentaje'])
        for estado, cantidad in total_estados.items():
            porcentaje = (cantidad / total_lineas) * 100 if total_lineas else 0
            writer.writerow([estado, cantidad, f"{porcentaje:.2f}"])
    print(f"Resumen de estados guardado en '{archivo_salida}'.")

def main():
    archivos_log = obtener_archivos_log(CARPETA_LOGS)
    if not archivos_log:
        return

    total_estados, errores = analizar_logs(archivos_log)

    print("\nConteo de estados encontrados en los logs:")
    for estado, cantidad in total_estados.items():
        print(f"{estado}: {cantidad}")

    guardar_errores_csv(errores, CARPETA_RESULTADOS)
    mostrar_estadisticas_estados(total_estados)
    graficar_estadisticas_estados(total_estados, CARPETA_RESULTADOS)
    guardar_estadisticas_estados_csv(total_estados, CARPETA_RESULTADOS)

if __name__ == '__main__':
    main()
    # Lanza el dashboard de Streamlit automáticamente
    try:
        # Nota: Este método puede ser frágil. Una mejor práctica es ejecutar
        # el script de análisis y luego, por separado, el comando:
        # streamlit run dashboard.py
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
        print("\nSe está abriendo el dashboard en tu navegador...")
    except Exception as e:
        print(f"\n❌ No se pudo abrir el dashboard automáticamente: {e}")
        print("   Para verlo, ejecuta en tu terminal: streamlit run dashboard.py")