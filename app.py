import streamlit as st
import pandas as pd
import requests

# Función para obtener datos desde la API
@st.cache_data
def get_country_data():
    url = "https://restcountries.com/v3.1/all"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Procesar los datos en un DataFrame
        processed_data = []
        for country in data:
            processed_data.append({
                "nombre_pais": country.get("name", {}).get("common", "N/A"),
                "Region_geografica": country.get("region", "N/A"),
                "Poblacion_total": country.get("population", 0),
                "Area_km²": country.get("area", 0.0),
                "Numero_frontera": len(country.get("borders", [])),
                "Numero_idiomas": len(country.get("languages", {})),
                "Numero_zonas_horarias": len(country.get("timezones", [])),
            })
        return pd.DataFrame(processed_data)
    else:
        st.error("No se pudo obtener datos de la API.")
        return pd.DataFrame()

# Cargar los datos desde la API
data = get_country_data()

# Configuración de la página
st.set_page_config(page_title="Visualización de Datos de Países", layout="wide")

# Páginas de la aplicación
def pagina_descripcion():
    st.title("Descripción del Proyecto")
    st.write("""
    Esta aplicación utiliza datos en tiempo real de la API pública REST Countries para realizar análisis y visualizaciones interactivas.
    """)
    st.write("### Ejemplo de Datos:")
    st.dataframe(data.head())
    st.write("Fuente de datos: [REST Countries API](https://restcountries.com/v3.1/all)")

def pagina_interaccion():
    st.title("Interacción con los Datos")
    st.write("### Datos Originales:")
    st.dataframe(data)

    st.write("### Estadísticas Básicas")
    columna = st.selectbox("Seleccione una columna para analizar", options=data.select_dtypes(include=["int64", "float64"]).columns)
    if columna:
        st.write(f"**Media:** {data[columna].mean()}")
        st.write(f"**Mediana:** {data[columna].median()}")
        st.write(f"**Desviación Estándar:** {data[columna].std()}")

    st.write("### Ordenar Datos")
    columna_orden = st.selectbox("Seleccione una columna para ordenar", options=data.columns)
    orden = st.radio("Orden:", ["Ascendente", "Descendente"])
    if columna_orden:
        datos_ordenados = data.sort_values(by=columna_orden, ascending=(orden == "Ascendente"))
        st.dataframe(datos_ordenados)

    st.write("### Filtrar Datos")
    filtro_columna = st.selectbox("Seleccione una columna numérica para filtrar", options=data.select_dtypes(include=["int64", "float64"]).columns)
    if filtro_columna:
        min_val = float(data[filtro_columna].min())
        max_val = float(data[filtro_columna].max())
        rango = st.slider("Seleccione un rango", min_val, max_val, (min_val, max_val))
        datos_filtrados = data[(data[filtro_columna] >= rango[0]) & (data[filtro_columna] <= rango[1])]
        st.dataframe(datos_filtrados)

        # Botón para descargar
        st.download_button("Descargar datos filtrados", datos_filtrados.to_csv(index=False), "datos_filtrados.csv")

def pagina_graficos():
    st.title("Visualización de Datos")
    
    st.write("### Crear un Gráfico")
    tipo_grafico = st.selectbox("Seleccione un tipo de gráfico", options=["Barras", "Línea", "Dispersión"])
    x_col = st.selectbox("Seleccione la variable para el eje X", options=data.select_dtypes(include=["int64", "float64"]).columns)
    y_col = st.selectbox("Seleccione la variable para el eje Y", options=data.select_dtypes(include=["int64", "float64"]).columns)

    if tipo_grafico and x_col and y_col:
        if tipo_grafico == "Barras":
            st.bar_chart(data[[x_col, y_col]].set_index(x_col))
        elif tipo_grafico == "Línea":
            st.line_chart(data[[x_col, y_col]].set_index(x_col))
        elif tipo_grafico == "Dispersión":
            import altair as alt
            chart = alt.Chart(data).mark_circle(size=60).encode(
                x=alt.X(x_col, scale=alt.Scale(zero=False)),
                y=alt.Y(y_col, scale=alt.Scale(zero=False)),
                tooltip=["nombre_pais"]
            )
            st.altair_chart(chart, use_container_width=True)

# Mapeo de páginas
paginas = {
    "Descripción del Proyecto": pagina_descripcion,
    "Interacción con los Datos": pagina_interaccion,
    "Visualización de Datos": pagina_graficos,
}

# Menú de navegación
st.sidebar.title("Navegación")
opcion = st.sidebar.radio("Seleccione una página", list(paginas.keys()))

# Ejecutar la página seleccionada
paginas[opcion]()
