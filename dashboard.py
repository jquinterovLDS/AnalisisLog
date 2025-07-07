import streamlit as st
import pandas as pd
import os
import plotly.express as px

# Rutas a los archivos generados por tu script
CSV_PATH = os.path.join('resultados', 'cantidad_por_caja.csv')
CSV_ESTADOS = os.path.join('resultados', 'estadistica_estados.csv')

st.set_page_config(page_title="Dashboard Errores por Caja", layout="wide")
st.title("Dashboard de Errores por Caja")

if not os.path.exists(CSV_PATH):
    st.error(f"No se encontró el archivo {CSV_PATH}. Ejecuta primero el análisis de logs.")
    st.stop()

df = pd.read_csv(CSV_PATH)

# Normaliza mensajes similares
def agrupar_mensajes(msg):
    if isinstance(msg, str):
        if msg.startswith("Bad password for account"):
            return "Bad password for account"
        if msg.startswith("CBR_005_0458 : WebService.Id(WSS) failed after"):
            return "CBR_005_0458 : WebService.Id(WSS) failed after (X)ms with Exception : (System.Net.Http.HttpRequestException: Bad Request)"
        if msg.startswith("Method 'Cegid.CBR.BasicWebRequestService.Invoke' - Exception - Remote service returned error"):
            return "Method 'Cegid.CBR.BasicWebRequestService.Invoke' - Exception - Remote service returned error"
    return msg

df['MensajeAgrupado'] = df['Mensaje'].apply(agrupar_mensajes)

tab1, tab2, tab3 = st.tabs([
    "Errores por Caja",
    "Mensajes de Error Más Repetidos",
    "Estadística de Estados"
])

color_map = {
    "INF": "#4FC3F7",   # azul claro
    "WRN": "#FFD600",   # amarillo
    "ERR": "#E53935"    # rojo
}

with tab1:
    st.subheader("Errores por Caja")
    cajas = df['Caja'].unique()
    caja_seleccionada = st.selectbox("Selecciona una caja:", ["Todas"] + list(cajas))
    df_caja = df.copy()
    if caja_seleccionada != "Todas":
        df_caja = df_caja[df_caja['Caja'] == caja_seleccionada]
    st.write(f"Total de errores mostrados: {len(df_caja)}")
    st.dataframe(df_caja, use_container_width=True)
    st.subheader("Cantidad de errores por caja")
    conteo = df.groupby('Caja')['Mensaje'].count().sort_values(ascending=False)
    st.bar_chart(conteo)

with tab2:
    st.subheader("Mensajes de error más repetidos (agrupados)")
    top_n = st.slider("¿Cuántos mensajes mostrar?", min_value=5, max_value=50, value=10)
    conteo_mensajes = df['MensajeAgrupado'].value_counts().head(top_n)
    st.bar_chart(conteo_mensajes)
    st.dataframe(conteo_mensajes.reset_index().rename(columns={'index': 'Mensaje', 'MensajeAgrupado': 'Repeticiones'}), use_container_width=True)

with tab3:
    st.subheader("Estadística de Estados")
    if os.path.exists(CSV_ESTADOS):
        df_estados = pd.read_csv(CSV_ESTADOS)
        if 'Estado' in df_estados.columns and 'Cantidad' in df_estados.columns:
            color_map = {
                "INF": "#4FC3F7",   # azul claro
                "WRN": "#FFD600",   # amarillo
                "ERR": "#E53935"    # rojo
            }
            fig = px.bar(
                df_estados,
                x='Estado',
                y='Cantidad',
                text='Cantidad',
                color='Estado',
                color_discrete_map=color_map,
                title="Cantidad por Estado",
            )
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_estados, use_container_width=True)
        else:
            st.warning("El archivo 'estadistica_estados.csv' no tiene las columnas esperadas.")
    else:
        st.warning("No se encontró el archivo 'estadistica_estados.csv'. Ejecuta el análisis primero.")

