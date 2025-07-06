import os
import csv
from collections import defaultdict

# Ruta del archivo de entrada
archivo_entrada = 'resultados/errores_completos.csv'
archivo_salida = 'resultados/clasificacion_por_modulo.csv'

# Diccionario para contar errores por módulo
conteo_modulos = defaultdict(int)

# Leer el archivo de errores completos
with open(archivo_entrada, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)  # Saltar encabezado
    for row in reader:
        if row:
            linea = row[0]
            partes = linea.split('|')
            if len(partes) > 6:
                modulo = partes[5].strip()
                conteo_modulos[modulo] += 1

# Guardar la clasificación por módulo en un nuevo archivo CSV
os.makedirs('resultados', exist_ok=True)
with open(archivo_salida, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Modulo', 'Cantidad'])
    for modulo, cantidad in sorted(conteo_modulos.items(), key=lambda x: x[1], reverse=True):
        writer.writerow([modulo, cantidad])

print(f"Clasificación por módulo guardada en '{archivo_salida}'.")
