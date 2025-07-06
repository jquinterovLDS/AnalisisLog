from pathlib import Path
import csv
import re
from datetime import datetime
from typing import List
from collections import Counter

CARPETA_LOGS = Path('./logs')
CARPETA_RESULTADOS = Path('resultados')
CARPETA_RESULTADOS.mkdir(exist_ok=True)
REGEX_FECHA = re.compile(r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}\.\d{3}')

def obtener_archivos_log(carpeta: Path) -> List[Path]:
    if not carpeta.exists():
        print(f"La carpeta '{carpeta}' no existe. Por favor créala y agrega tus archivos .Log.")
        exit()
    return [f for f in carpeta.iterdir() if f.suffix.lower() == '.log']

def extraer_errores(archivo_log: Path) -> List[str]:
    errores = []
    try:
        with archivo_log.open('r', encoding='utf-8') as f:
            buffer = []
            for linea in f:
                linea = linea.rstrip('\n')
                if REGEX_FECHA.match(linea):
                    if buffer:
                        linea_completa = ' '.join(buffer)
                        partes = linea_completa.split('|')
                        if len(partes) > 5 and partes[4].strip() == 'ERR':
                            errores.append(linea_completa)
                        buffer = []
                    buffer.append(linea)
                else:
                    if buffer:
                        buffer.append(linea)
            if buffer:
                linea_completa = ' '.join(buffer)
                partes = linea_completa.split('|')
                if len(partes) > 5 and partes[4].strip() == 'ERR':
                    errores.append(linea_completa)
    except Exception as e:
        print(f"Ocurrió un error al procesar {archivo_log}: {e}")
    return errores

def extraer_estados(archivo_log: Path) -> Counter:
    estados = Counter()
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
                            estados[estado] += 1
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
                    estados[estado] += 1
    except Exception as e:
        print(f"Ocurrió un error al procesar {archivo_log}: {e}")
    return estados

def guardar_errores_csv(errores: List[str], carpeta_resultados: Path) -> None:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archivo_salida = carpeta_resultados / f'errores_completos_{timestamp}.csv'
    with archivo_salida.open(mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Linea de Error'])
        for linea in errores:
            writer.writerow([linea])
    print(f"\n✅ Se guardaron {len(errores)} errores reales en '{archivo_salida}'.")

def main():
    archivos_log = obtener_archivos_log(CARPETA_LOGS)
    errores_reales = []
    total_estados = Counter()
    for archivo_log in archivos_log:
        print(f"Procesando archivo: {archivo_log}")
        errores_reales.extend(extraer_errores(archivo_log))
        total_estados += extraer_estados(archivo_log)
    guardar_errores_csv(errores_reales, CARPETA_RESULTADOS)
    print("\nConteo de estados encontrados en los logs:")
    for estado, cantidad in total_estados.items():
        print(f"{estado}: {cantidad}")

if __name__ == '__main__':
    main()