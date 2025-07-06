import os
import csv

# Ruta del archivo de entrada y salida
archivo_entrada = 'resultados/errores_completos.csv'
archivo_salida = 'resultados/errores_por_caja.csv'

# Crear carpeta de resultados si no existe
os.makedirs('resultados', exist_ok=True)

# Conjunto para almacenar combinaciones únicas de columnas 7, 8 y 9
datos_filtrados = set()

# Leer el archivo de errores completos
with open(archivo_entrada, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)  # Saltar encabezado
    for row in reader:
        partes = row[0].split('|')
        if len(partes) > 8:
            col7 = partes[6].strip()
            col8 = partes[7].strip()
            col9 = partes[8].strip()
            datos_filtrados.add((col7, col8, col9))

# Guardar los datos filtrados en un nuevo archivo CSV
with open(archivo_salida, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Caja', 'Modulo', 'Flujo'])
    for fila in sorted(datos_filtrados):
        writer.writerow(fila)

print(f"Archivo generado: {archivo_salida}")
