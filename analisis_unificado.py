from pathlib import Path
import csv
import re
from datetime import datetime
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

def analizar_logs(archivos_log: List[Path]):
    total_estados = Counter()
    errores = []
    errores_por_caja = defaultdict(int)

    for archivo_log in archivos_log:
        print(f"Procesando archivo: {archivo_log}")
        try:
            with archivo_log.open('r', encoding='utf-8') as f:
                buffer = []
                for linea in f:
                    linea = linea.rstrip('\n')
                    if REGEX_FECHA.match(linea):
                        if buffer:
                            linea_completa = ' '.join(buffer)
                            partes = linea_completa.split('|')
                            if len(partes) > 5:
                                estado = partes[4].strip()
                                total_estados[estado] += 1
                                if estado == 'ERR':
                                    errores.append(linea_completa)
                                    if len(partes) > 6:
                                        modulo = partes[5].strip()
                                        errores_por_caja[modulo] += 1
                            buffer = []
                        buffer.append(linea)
                    else:
                        if buffer:
                            buffer.append(linea)
                if buffer:
                    linea_completa = ' '.join(buffer)
                    partes = linea_completa.split('|')
                    if len(partes) > 5:
                        estado = partes[4].strip()
                        total_estados[estado] += 1
                        if estado == 'ERR':
                            errores.append(linea_completa)
                            if len(partes) > 6:
                                modulo = partes[5].strip()
                                errores_por_caja[modulo] += 1
        except Exception as e:
            print(f"Ocurrió un error al procesar {archivo_log}: {e}")
    return total_estados, errores, errores_por_caja

def guardar_errores_csv(errores: List[str], carpeta_resultados: Path) -> Path:
    archivo_salida = carpeta_resultados / 'errores_completos.csv'
    with archivo_salida.open(mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Escribe encabezados depurados
        writer.writerow(['Fecha', 'Estado', 'Caja', 'Modulo', 'Flujo', 'Mensaje'])
        for linea in errores:
            partes = [p.strip() for p in linea.split('|')]
            # Elimina columnas 2, 3 y 4 (índices 1, 2, 3)
            # Nueva estructura: [0]Fecha, [4]Estado, [5]Caja, [6]Modulo, [7]Flujo, [8:]Mensaje
            if len(partes) > 8:
                nueva_linea = [
                    partes[0],          # Fecha
                    partes[4],          # Estado
                    partes[5],          # Caja
                    partes[6],          # Modulo
                    partes[7],          # Flujo
                    '|'.join(partes[8:])  # Mensaje (puede contener '|')
                ]
            else:
                # Si faltan columnas, rellena con vacío
                nueva_linea = [
                    partes[0] if len(partes) > 0 else '',
                    partes[4] if len(partes) > 4 else '',
                    partes[5] if len(partes) > 5 else '',
                    partes[6] if len(partes) > 6 else '',
                    partes[7] if len(partes) > 7 else '',
                    '|'.join(partes[8:]) if len(partes) > 8 else ''
                ]
            writer.writerow(nueva_linea)
    print(f"\n✅ Se guardaron {len(errores)} errores reales en '{archivo_salida}'.")
    return archivo_salida

def guardar_errores_por_caja(errores: list, carpeta_resultados: Path) -> None:
    # Agrupa errores por caja
    errores_por_caja = defaultdict(list)
    for linea in errores:
        partes = [p.strip() for p in linea.split('|')]
        if len(partes) > 5:
            caja = partes[5]
            mensaje = '|'.join(partes[8:]) if len(partes) > 8 else ''
            errores_por_caja[caja].append(mensaje)
    archivo_salida = carpeta_resultados / 'cantidad_por_caja.csv'
    with archivo_salida.open(mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Caja', 'Cantidad', 'Mensaje'])
        for caja, mensajes in sorted(errores_por_caja.items(), key=lambda x: len(x[1]), reverse=True):
            for mensaje in mensajes:
                writer.writerow([caja, len(mensajes), mensaje])
    print(f"Clasificación por caja guardada en '{archivo_salida}'.")

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
    total_estados, errores, errores_por_caja = analizar_logs(archivos_log)

    print("\nConteo de estados encontrados en los logs:")
    for estado, cantidad in total_estados.items():
        print(f"{estado}: {cantidad}")

    mostrar_estadisticas_estados(total_estados)
    graficar_estadisticas_estados(total_estados, CARPETA_RESULTADOS)
    guardar_estadisticas_estados_csv(total_estados, CARPETA_RESULTADOS)

    print("\nClasificación de errores por caja:")
    for modulo, cantidad in sorted(errores_por_caja.items(), key=lambda x: x[1], reverse=True):
        print(f"{modulo}: {cantidad}")

    guardar_errores_por_caja(errores, CARPETA_RESULTADOS)
    guardar_errores_csv(errores, CARPETA_RESULTADOS)  # <-- AGREGA ESTA LÍNEA

if __name__ == '__main__':
    main()
    # Lanza el dashboard de Streamlit automáticamente
    try:
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
        print("\nSe está abriendo el dashboard en tu navegador...")
    except Exception as e:
        print(f"No se pudo abrir el dashboard automáticamente: {e}")