from pathlib import Path
import csv
import re
from datetime import datetime
from typing import List
from collections import Counter, defaultdict

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
        writer.writerow(['Linea de Error'])
        for linea in errores:
            writer.writerow([linea])
    print(f"\n✅ Se guardaron {len(errores)} errores reales en '{archivo_salida}'.")
    return archivo_salida

def guardar_errores_por_caja(errores_por_caja: dict, carpeta_resultados: Path) -> Path:
    archivo_salida = carpeta_resultados / 'cantidad_por_caja.csv'
    with archivo_salida.open(mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Caja', 'Cantidad'])
        for modulo, cantidad in sorted(errores_por_caja.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([modulo, cantidad])
    print(f"Clasificación por módulo guardada en '{archivo_salida}'.")
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

def main():
    archivos_log = obtener_archivos_log(CARPETA_LOGS)
    total_estados, errores, errores_por_caja = analizar_logs(archivos_log)

    print("\nConteo de estados encontrados en los logs:")
    for estado, cantidad in total_estados.items():
        print(f"{estado}: {cantidad}")

    mostrar_estadisticas_estados(total_estados)

    guardar_errores_csv(errores, CARPETA_RESULTADOS)

    print("\nClasificación de errores por caja:")
    for modulo, cantidad in sorted(errores_por_caja.items(), key=lambda x: x[1], reverse=True):
        print(f"{modulo}: {cantidad}")

    guardar_errores_por_caja(errores_por_caja, CARPETA_RESULTADOS)

if __name__ == '__main__':
    main()