import re
import matplotlib.pyplot as plt
from datetime import datetime

# Función para leer y procesar los archivos de log
def procesar_logs(archivos):
    errores = []
    alertas = []
    otros = []
    INF = []
    fechas_errores = []

    for archivo in archivos:
        with open(archivo, 'r') as f:
            for linea in f:
                if "ERR" in linea:
                    errores.append(linea)
                    fecha = re.search(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}\.\d{3}', linea)
                    if fecha:
                        fechas_errores.append(datetime.strptime(fecha.group(), '%m/%d/%Y %H:%M:%S.%f'))
                elif "ALERTA" in linea:
                    alertas.append(linea)
                elif "INF" in linea:
                    INF.append(linea)
                else:
                    otros.append(linea)

    return errores, alertas, otros, INF, fechas_errores

# Función para generar estadísticas
def generar_estadisticas(errores, alertas, otros, INF):
    return len(errores), len(alertas), len(otros), len(INF)

# Función para clasificar errores
def clasificar_errores(errores):
    clasificacion = {}
    for error in errores:
        tipo = re.search(r'TipoError:\s*(\w+)', error)
        if tipo:
            tipo_error = tipo.group(1)
            clasificacion[tipo_error] = clasificacion.get(tipo_error, 0) + 1
    return clasificacion

# Función para crear gráfica
def crear_grafica(fechas_errores):
    if fechas_errores:
        plt.hist(fechas_errores, bins=24)
        plt.xlabel('Fecha y Hora')
        plt.ylabel('Número de Errores')
        plt.title('Distribución de Errores por Fecha y Hora')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    else:
        print("No hay fechas de errores para graficar.")

# Archivos de log a analizar
archivos = ['WebApplication_2025.07.03_085.Log', 'WebApplication_2025.07.03_086.Log']

# Procesar los logs
errores, alertas, otros, INF, fechas_errores = procesar_logs(archivos)

# Generar estadísticas
total_errores, total_alertas, total_otros, total_INF = generar_estadisticas(errores, alertas, otros, INF)
print(f'Total Errores: {total_errores}')
print(f'Total Alertas: {total_alertas}')
print(f'Total Otros: {total_otros}')
print(f'Total INF: {total_INF}')

# Clasificar errores
clasificacion_errores = clasificar_errores(errores)
print('Clasificación de Errores:')
for tipo, cantidad in clasificacion_errores.items():
    print(f'{tipo}: {cantidad}')

# Crear gráfica
crear_grafica(fechas_errores)
