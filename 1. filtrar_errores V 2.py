import os
import csv
import re
from datetime import datetime

# Carpeta donde están los archivos .Log
carpeta_logs = './logs'
os.makedirs('resultados', exist_ok=True)
errores_reales = []

# Expresión regular para detectar líneas que comienzan con una fecha
regex_fecha = re.compile(r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}\.\d{3}')

# Obtener todos los archivos .Log en la carpeta
try:
    archivos_log = [os.path.join(carpeta_logs, f) for f in os.listdir(carpeta_logs) if f.endswith('.Log')]
except FileNotFoundError:
    print(f"La carpeta '{carpeta_logs}' no existe. Por favor créala y agrega tus archivos .Log.")
    exit()

# Procesar cada archivo
for archivo_log in archivos_log:
    print(f"Procesando archivo: {archivo_log}")
    try:
        with open(archivo_log, 'r', encoding='utf-8') as f:
            buffer = []
            for linea in f:
                linea = linea.rstrip('\n')
                if regex_fecha.match(linea):
                    if buffer:
                        linea_completa = ' '.join(buffer)
                        partes = linea_completa.split('|')
                        if len(partes) > 5 and partes[4].strip() == 'ERR':
                            errores_reales.append(linea_completa)
                        buffer = []
                    buffer.append(linea)
                else:
                    if buffer:
                        buffer.append(linea)

            if buffer:
                linea_completa = ' '.join(buffer)
                partes = linea_completa.split('|')
                if len(partes) > 5 and partes[4].strip() == 'ERR':
                    errores_reales.append(linea_completa)

    except Exception as e:
        print(f"Ocurrió un error al procesar {archivo_log}: {e}")

# Generar nombre de archivo con marca de tiempo
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
archivo_salida = f'resultados/errores_completos_{timestamp}.csv'

# Guardar los errores reales en un archivo CSV
with open(archivo_salida, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Linea de Error'])
    for linea in errores_reales:
        writer.writerow([linea])

print(f"\n✅ Se guardaron {len(errores_reales)} errores reales en '{archivo_salida}'.")
