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
"""

import streamlit as st
import json
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="Cálculos Mecánicos AT - UTS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar estilos CSS personalizados
def cargar_estilos():
    """Carga estilos CSS personalizados."""
    css = """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1a5276;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #5d6d7e;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-card {
        color: black;
        background-color: #eaf2f8;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2874a6;
        margin-bottom: 1rem;
    }
    .success-card {
        color: black;
        background-color: #e8f8f5;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1e8449;
        margin-bottom: 1rem;
    }
    .warning-card {
        background-color: #fef9e7;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #d4ac0d;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1a5276;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #5d6d7e;
    }
    .disclaimer {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        font-size: 0.85rem;
        color: #6c757d;
        border: 1px solid #dee2e6;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

cargar_estilos()

# Sidebar con información del proyecto
with st.sidebar:
    # Logo (placeholder si no existe)
    logo_path = Path(__file__).parent / "assets" / "logo_uts.png"
    if logo_path.exists():
        st.image(str(logo_path), width=200)
    else:
        st.markdown("### 🎓 UTS")

    st.title("Cálculos Mecánicos en Alta Tensión")

    st.markdown("""
    **Trabajo de Grado**
    Tecnología en Electricidad Industrial
    Unidades Tecnológicas de Santander

    ---
    **Autor:** Jhohan Felipe Manosalva Sierra
    **Director:** Ing. MPE Fabio Alfonso González
    **Año:** 2025
    """)

    st.markdown("---")

    st.markdown("### 📚 Normativa Aplicable")
    st.markdown("""
    - RETIE Res. 40117/2024
    - NTC 2050 (Código Eléctrico)
    - IEEE 738 (Capacidad Térmica)
    - IEC 60826 (Diseño Mecánico)
    """)

    st.markdown("---")

    st.markdown("### 🔧 Navegación")
    st.markdown("""
    Utilice el menú lateral para acceder a los diferentes módulos:
    1. 📊 Datos del Conductor
    2. 🌡️ Condiciones Ambientales
    3. 📐 Cálculo Mecánico
    4. 📈 Análisis de Hipótesis
    5. ✅ Verificación RETIE
    6. 📄 Generar Reporte
    """)

# Contenido principal
st.markdown('<h1 class="main-header">⚡ Software de Cálculos Mecánicos para Líneas de Alta Tensión</h1>',
            unsafe_allow_html=True)

st.markdown('<p class="sub-header">Sistema educativo para el diseño mecánico de líneas de transmisión eléctrica de 34.5 kV a 500 kV</p>',
            unsafe_allow_html=True)

# Descripción
st.markdown("""
Este software permite realizar los cálculos mecánicos requeridos para el diseño
de líneas de transmisión eléctrica, cumpliendo con la normativa colombiana vigente
(RETIE) y estándares internacionales.
""")

# Advertencia educativa
st.markdown("""
<div class="disclaimer">
⚠️ <b>AVISO IMPORTANTE:</b> Este software es de carácter <b>educativo</b> y está diseñado
para fines académicos. Los resultados deben ser verificados por un profesional calificado
antes de su aplicación en proyectos reales. Los cálculos pueden reproducirse manualmente
para fines didácticos.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Tarjetas de navegación
st.markdown("### 🚀 Módulos Disponibles")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="info-card">
    <h4>📊 Datos del Conductor</h4>
    <p>Seleccione el tipo de conductor (ACSR, AAAC, AAC) y visualice sus características técnicas.</p>
    <ul>
    <li>Base de datos de conductores</li>
    <li>Propiedades mecánicas y eléctricas</li>
    <li>Comparación de conductores</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-card">
    <h4>🌡️ Condiciones Ambientales</h4>
    <p>Defina la zona climática y los parámetros ambientales de diseño según la ubicación en Colombia.</p>
    <ul>
    <li>Zonas climáticas predefinidas</li>
    <li>Temperaturas y vientos de diseño</li>
    <li>Factor de corrección por altitud</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="info-card">
    <h4>📐 Cálculo Mecánico</h4>
    <p>Ejecute los cálculos de tensión, flecha y cargas mecánicas usando la ecuación de cambio de estado.</p>
    <ul>
    <li>Ecuación cúbica de estado</li>
    <li>Cálculo de vano regulador</li>
    <li>Flechas y longitudes</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown("""
    <div class="success-card">
    <h4>📈 Análisis de Hipótesis</h4>
    <p>Evalúe las 4 hipótesis de cálculo requeridas por el RETIE para el diseño de líneas de transmisión.</p>
    <ul>
    <li>Hipótesis A: Viento máximo</li>
    <li>Hipótesis B: Temperatura mínima</li>
    <li>Hipótesis C: Condición EDS</li>
    <li>Hipótesis D: Flecha máxima</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class="success-card">
    <h4>✅ Verificación RETIE</h4>
    <p>Compruebe el cumplimiento de las distancias mínimas de seguridad según la Tabla 13.2 del RETIE.</p>
    <ul>
    <li>Distancias al terreno</li>
    <li>Cruces con carreteras</li>
    <li>Corrección por altitud</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown("""
    <div class="success-card">
    <h4>📄 Generar Reporte</h4>
    <p>Exporte los resultados en un reporte PDF profesional con todos los cálculos y verificaciones.</p>
    <ul>
    <li>Resumen de parámetros</li>
    <li>Tablas de resultados</li>
    <li>Gráficos incluidos</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Información adicional
col_info1, col_info2 = st.columns(2)

with col_info1:
    st.markdown("### 📖 Fundamento Teórico")
    st.markdown("""
    El software implementa los siguientes métodos de cálculo:

    **Ecuación de Cambio de Estado:**
    La ecuación cúbica que relaciona la tensión mecánica del conductor
    bajo diferentes condiciones de temperatura y carga:

    `σ₂³ - σ₂² × A - B = 0`

    **Donde:**
    - A = σ₁ - E×α×(t₂-t₁) + (E×a²×g₁²)/(24×σ₁²)
    - B = (E×a²×g₂²)/24

    **Métodos de solución disponibles:**
    - Método de Cardano (analítico)
    - Newton-Raphson (iterativo)
    - Método de Brent (híbrido)
    """)

with col_info2:
    st.markdown("### 🎯 Aplicaciones")
    st.markdown("""
    Este software es útil para:

    - **Estudiantes:** Aprender los fundamentos del diseño mecánico
      de líneas de transmisión
    - **Docentes:** Herramienta didáctica para enseñanza de
      cálculos eléctricos
    - **Profesionales:** Verificación rápida de cálculos preliminares

    **Niveles de tensión soportados:**
    - 34.5 kV (Subtransmisión)
    - 57.5 kV
    - 115 kV (Transmisión)
    - 230 kV
    - 500 kV (Extra Alta Tensión)
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; font-size: 0.85rem;">
<p>Desarrollado como Trabajo de Grado para el programa de Tecnología en Electricidad Industrial</p>
<p>Unidades Tecnológicas de Santander - Bucaramanga, Colombia - 2025</p>
<p>© 2025 Jhohan Felipe Manosalva Sierra - Todos los derechos reservados</p>
</div>
""", unsafe_allow_html=True)
