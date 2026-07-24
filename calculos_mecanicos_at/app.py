"""
Software de Cálculos Mecánicos para Líneas de Transmisión de Alta Tensión

Aplicación principal desarrollada con Streamlit para el programa de
Tecnología en Electricidad Industrial de las Unidades Tecnológicas de Santander.

Autor: Jhohan Felipe Manosalva Sierra
Director: Ing. MPE Fabio Alfonso González
Año: 2025

Este software cumple con:
- RETIE Resolución 40117 de 2024
- NTC 2050 (Código Eléctrico Colombiano)
- IEEE 738-2023 (Capacidad Térmica)
- IEC 60826:2017 (Diseño Mecánico)

Este archivo es únicamente el enrutador: declara las páginas con st.navigation
y ejecuta la seleccionada. El contenido de la portada está en paginas/inicio.py.
"""

from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from utils.estilos import aplicar_estilos

# set_page_config y los estilos se aplican una sola vez, aquí: con st.navigation
# la página seleccionada se ejecuta dentro de este mismo script.
st.set_page_config(
    page_title="Cálculos Mecánicos AT",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

aplicar_estilos()

paginas = [
    st.Page("paginas/inicio.py", title="Inicio", icon="🏠", default=True),
    st.Page("paginas/01_datos_conductor.py", title="Datos del Conductor", icon="🔌"),
    st.Page("paginas/02_condiciones_ambientales.py", title="Condiciones Ambientales", icon="🌩️"),
    st.Page("paginas/03_calculo_mecanico.py", title="Cálculo Mecánico", icon="🗼"),
    st.Page("paginas/04_analisis_hipotesis.py", title="Análisis de Hipótesis", icon="💡"),
    st.Page("paginas/05_verificacion_retie.py", title="Verificación RETIE", icon="🛡️"),
    st.Page("paginas/06_generar_reporte.py", title="Generar Reporte", icon="📋"),
]

navegacion = st.navigation(paginas)

# La normativa queda bajo el menú de navegación y ahora se ve en todas las páginas.
with st.sidebar:
    st.markdown("### 📚 Normativa Aplicable")
    st.markdown("""
    - RETIE Res. 40117/2024
    - NTC 2050 (Código Eléctrico)
    - IEEE 738 (Capacidad Térmica)
    - IEC 60826 (Diseño Mecánico)
    """)

navegacion.run()
