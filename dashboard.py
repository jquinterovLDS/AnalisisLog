import streamlit as st
import pandas as pd
import os
import plotly.express as px

# Haz el dashboard más ancho
st.set_page_config(page_title="Dashboard Logs CEGID", layout="wide")

# Aumenta el tamaño del texto de las pestañas
st.markdown("""
    <style>
    /* Selector más específico para tabs de Streamlit */
    div[data-testid="stTabs"] button[role="tab"] > div {
        font-size: 2.0rem !important;
        font-weight: bold !important;
        padding: 1.2rem 2.5rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# Logo PNG centrado desde archivo local
st.image("img/logoGif.png", width=220)

st.markdown("<h1 style='color:#003366; text-align:center;'>Dashboard Logs Errores CEGID</h1>", unsafe_allow_html=True)

# Rutas a los archivos generados por tu script
CSV_PATH = os.path.join('resultados', 'errores_completos.csv')
CSV_ESTADOS = os.path.join('resultados', 'estadistica_estados.csv')

if not os.path.exists(CSV_PATH):
    st.error(f"No se encontró el archivo {CSV_PATH}. Ejecuta primero el análisis de logs.")
    st.stop()

df = pd.read_csv(CSV_PATH)

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
    "INF": "#1565C0",   # azul oscuro (más sobrio)
    "WRN": "#FFD600",   # amarillo
    "ERR": "#E53935"    # rojo
}

with tab1:
    st.markdown("### Errores por Caja")
    cajas = df['Caja'].unique()
    caja_seleccionada = st.selectbox("Selecciona una caja:", ["Todas"] + list(cajas))
    df_caja = df.copy()
    if caja_seleccionada != "Todas":
        df_caja = df_caja[df_caja['Caja'] == caja_seleccionada]
    st.write(f"Total de errores mostrados: **{len(df_caja)}**")
    st.metric("Total de errores", len(df))
    st.dataframe(df_caja, use_container_width=True, hide_index=True)
    st.markdown("#### Cantidad de errores por caja")
    conteo = df.groupby('Caja')['Mensaje'].count().sort_values(ascending=False).reset_index()
    fig = px.bar(
        conteo,
        x='Caja',
        y='Mensaje',
        color='Mensaje',
        color_continuous_scale='Blues',
        title="Errores por Caja"
    )
    fig.update_layout(
        plot_bgcolor='#f4f8fb',
        paper_bgcolor='#f4f8fb',
        font_color='#003366',
        xaxis_title="Caja",
        yaxis_title="Cantidad de Errores",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("### Mensajes de error más repetidos (agrupados)")
    filtro = st.text_input("Buscar mensaje:")
    conteo_mensajes = df['MensajeAgrupado'].value_counts().reset_index()
    conteo_mensajes.columns = ['Mensaje', 'Repeticiones']
    if filtro:
        conteo_mensajes = conteo_mensajes[conteo_mensajes['Mensaje'].str.contains(filtro, case=False, na=False)]
    conteo_mensajes['MensajeCorto'] = conteo_mensajes['Mensaje'].str.slice(0, 50) + "..."
    fig2 = px.bar(
        conteo_mensajes,
        y='MensajeCorto',
        x='Repeticiones',
        orientation='h',
        color='Repeticiones',
        color_continuous_scale='Blues',
        title="Top Mensajes de Error (truncados)"
    )
    fig2.update_layout(
        plot_bgcolor='#f4f8fb',
        paper_bgcolor='#f4f8fb',
        font_color='#003366',
        yaxis_title="Mensaje (truncado)",
        xaxis_title="Repeticiones",
        showlegend=True,
        height=min(60 * len(conteo_mensajes), 2000),
        margin=dict(l=350, r=40, t=40, b=40)
    )
    fig2.update_yaxes(tickfont=dict(size=12))
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("#### Tabla de mensajes completos")
    st.dataframe(conteo_mensajes[['Mensaje', 'Repeticiones']], use_container_width=True, hide_index=True)

with tab3:
    st.markdown("### Estadística de Estados")
    if os.path.exists(CSV_ESTADOS):
        df_estados = pd.read_csv(CSV_ESTADOS)
        if 'Estado' in df_estados.columns and 'Cantidad' in df_estados.columns:
            color_map = {
                "INF": "#1565C0",   # azul oscuro (más sobrio)
                "WRN": "#FFD600",   # amarillo
                "ERR": "#E53935"    # rojo
            }
            fig3 = px.bar(
                df_estados,
                x='Estado',
                y='Cantidad',
                text='Cantidad',
                color='Estado',
                color_discrete_map=color_map,
                title="Cantidad por Estado",
            )
            fig3.update_traces(textposition='outside')
            fig3.update_layout(
                plot_bgcolor='#f4f8fb',
                paper_bgcolor='#f4f8fb',
                font_color='#003366',
                xaxis_title="Estado",
                yaxis_title="Cantidad",
                showlegend=False
            )
            st.plotly_chart(fig3, use_container_width=True)
            st.dataframe(df_estados, use_container_width=True, hide_index=True)
        else:
            st.warning("El archivo 'estadistica_estados.csv' no tiene las columnas esperadas.")
    else:
        st.warning("No se encontró el archivo 'estadistica_estados.csv'. Ejecuta el análisis primero.")
