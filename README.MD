# Dashboard Logs CEGID

Este proyecto permite analizar archivos de logs generados por CEGID, extraer estadísticas y visualizar los resultados en un dashboard interactivo usando Streamlit.

## Requisitos previos

- **Python 3.8 o superior** instalado en el sistema.
- Recomendado: [Visual Studio Code](https://code.visualstudio.com/) para editar y ejecutar el código.

## Instalación en un PC nuevo

1. **Descarga el proyecto**
   - Clona el repositorio o copia todos los archivos y carpetas en una carpeta local.

2. **Instala las dependencias**
   Abre una terminal en la carpeta del proyecto y ejecuta:
   ```sh
   pip install pandas matplotlib plotly streamlit
   python -m pip install --upgrade pip
   ```

3. **Prepara las carpetas**
   - Coloca los archivos `.log` que deseas analizar en la carpeta `logs/`.
   - No es necesario crear la carpeta `resultados/`, se crea automáticamente.

## Ejecución

1. **Analiza los logs**
   Ejecuta el script principal para procesar los archivos de log:
   ```sh
   python analisis_unificado.py
   ```
   Esto generará los archivos de resultados en la carpeta `resultados/`:
   - `errores_completos.csv`: Todos los errores y warnings encontrados.
   - `estadistica_estados.csv`: Estadística de los estados (INF, WRN, ERR).
   - `mensajes_repetidos.csv`: Mensajes de error agrupados y su cantidad de repeticiones.

2. **Visualiza el dashboard**
   Ejecuta el dashboard con Streamlit:
   ```sh
   streamlit run dashboard.py
   ```
   Se abrirá una interfaz web donde podrás explorar los resultados.

## ¿Cómo funciona?

- **analisis_unificado.py**: Lee todos los archivos `.log` en la carpeta `logs/`, valida la estructura de cada línea, clasifica los mensajes por estado (INF, WRN, ERR), agrupa errores y warnings, y guarda los resultados en archivos CSV.
- **dashboard.py**: Carga los archivos generados y muestra tres pestañas:
  1. **Estadística de Estados**: Gráfica y tabla con el conteo de cada estado.
  2. **Errores por Caja**: Filtra y muestra los errores por cada caja, con opción de ver el top 10.
  3. **Mensajes de error más repetidos**: Lista y gráfica de los mensajes de error agrupados y su frecuencia.

## Estructura de carpetas

```
proyecto_logs/
├── logs/          # Aquí van los archivos .log a analizar
├── resultados/    # Se crea automáticamente
├── img/           # Contiene logoGif.png para el dashboard
├── analisis_unificado.py
├── dashboard.py
```

## Notas adicionales

- Si el dashboard muestra un error de archivo faltante, asegúrate de ejecutar primero `analisis_unificado.py`.
- Puedes personalizar el agrupamiento de mensajes editando la función `agrupar_mensajes` en [`dashboard.py`](dashboard.py).

---

Para dudas o mejoras, revisa la documentacion CEGID: https://www.cegid.com/es/documentacion/