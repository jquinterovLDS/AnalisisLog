import os
import csv

# Ruta del archivo de log original
archivo_log = 'WebApplication_2025.07.03_085.Log'

# Crear carpeta de resultados si no existe
os.makedirs('resultados', exist_ok=True)

# Lista para almacenar errores reales
errores_reales = []

# Leer y filtrar líneas
with open(archivo_log, 'r', encoding='utf-8') as f:
    for linea in f:
        partes = linea.strip().split('|')
        if len(partes) > 5:
            categoria = partes[4].strip()
            if categoria == 'ERR':
                errores_reales.append(linea.strip())

# Guardar los errores reales en un archivo CSV
archivo_salida = 'resultados/errores_completos.csv'
with open(archivo_salida, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Linea de Error'])
    for linea in errores_reales:
        writer.writerow([linea])

print(f"Se guardaron {len(errores_reales)} errores reales en '{archivo_salida}'.")
