import os
import csv
import re

archivo_log = 'WebApplication_2025.07.03_085.Log'
os.makedirs('resultados', exist_ok=True)
errores_reales = []

regex_fecha = re.compile(r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}\.\d{3}')

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

    with open('resultados/errores_completos.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Linea de Error'])
        for linea in errores_reales:
            writer.writerow([linea])

    print(f"Se guardaron {len(errores_reales)} errores reales en 'resultados/errores_completos.csv'.")

except FileNotFoundError:
    print(f"No se encontró el archivo: {archivo_log}")
except Exception as e:
    print(f"Ocurrió un error durante el procesamiento: {e}")
