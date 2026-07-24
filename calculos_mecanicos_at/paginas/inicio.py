"""
Página de inicio: presentación del software y acceso a los módulos.

Se ejecuta desde el router (app.py) mediante st.navigation, por lo que aquí no
se llama a st.set_page_config() ni a aplicar_estilos().
"""

from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.estilos import encabezado_pagina

# Rutas relativas al script de entrada (app.py), como las espera st.page_link.
MODULOS = {
    "01": "paginas/01_datos_conductor.py",
    "02": "paginas/02_condiciones_ambientales.py",
    "03": "paginas/03_calculo_mecanico.py",
    "04": "paginas/04_analisis_hipotesis.py",
    "05": "paginas/05_verificacion_retie.py",
    "06": "paginas/06_generar_reporte.py",
}

encabezado_pagina(
    "⚡",
    "Software de Cálculos Mecánicos para Líneas de Alta Tensión",
    "Sistema educativo para el diseño mecánico de líneas de transmisión "
    "eléctrica de 34.5 kV a 500 kV, conforme al RETIE y estándares internacionales."
)

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
    with st.container(key="tarjeta-01"):
        st.markdown("""
        <div class="info-card">
        <h4>🔌 Datos del Conductor</h4>
        <p>Seleccione el tipo de conductor (ACSR, AAAC, AAC) y visualice sus características técnicas.</p>
        <ul>
        <li>Base de datos de conductores</li>
        <li>Propiedades mecánicas y eléctricas</li>
        <li>Comparación de conductores</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(MODULOS["01"], label="Ir a Datos del Conductor",
                     icon="🔌", width='stretch')

with col2:
    with st.container(key="tarjeta-02"):
        st.markdown("""
        <div class="info-card">
        <h4>🌩️ Condiciones Ambientales</h4>
        <p>Defina la zona climática y los parámetros ambientales de diseño según la ubicación en Colombia.</p>
        <ul>
        <li>Zonas climáticas predefinidas</li>
        <li>Temperaturas y vientos de diseño</li>
        <li>Factor de corrección por altitud</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(MODULOS["02"], label="Ir a Condiciones Ambientales",
                     icon="🌩️", width='stretch')

with col3:
    with st.container(key="tarjeta-03"):
        st.markdown("""
        <div class="info-card">
        <h4>🗼 Cálculo Mecánico</h4>
        <p>Ejecute los cálculos de tensión, flecha y cargas mecánicas usando la ecuación de cambio de estado.</p>
        <ul>
        <li>Ecuación cúbica de estado</li>
        <li>Cálculo de vano regulador</li>
        <li>Flechas y longitudes</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(MODULOS["03"], label="Ir a Cálculo Mecánico",
                     icon="🗼", width='stretch')

col4, col5, col6 = st.columns(3)

with col4:
    with st.container(key="tarjeta-04"):
        st.markdown("""
        <div class="success-card">
        <h4>💡 Análisis de Hipótesis</h4>
        <p>Evalúe las 4 hipótesis de cálculo requeridas por el RETIE para el diseño de líneas de transmisión.</p>
        <ul>
        <li>Hipótesis A: Viento máximo</li>
        <li>Hipótesis B: Temperatura mínima</li>
        <li>Hipótesis C: Condición EDS</li>
        <li>Hipótesis D: Flecha máxima</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(MODULOS["04"], label="Ir a Análisis de Hipótesis",
                     icon="💡", width='stretch')

with col5:
    with st.container(key="tarjeta-05"):
        st.markdown("""
        <div class="success-card">
        <h4>🛡️ Verificación RETIE</h4>
        <p>Compruebe el cumplimiento de las distancias mínimas de seguridad según la Tabla 13.2 del RETIE.</p>
        <ul>
        <li>Distancias al terreno</li>
        <li>Cruces con carreteras</li>
        <li>Corrección por altitud</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(MODULOS["05"], label="Ir a Verificación RETIE",
                     icon="🛡️", width='stretch')

with col6:
    with st.container(key="tarjeta-06"):
        st.markdown("""
        <div class="success-card">
        <h4>📋 Generar Reporte</h4>
        <p>Exporte los resultados en un reporte PDF profesional con todos los cálculos y verificaciones.</p>
        <ul>
        <li>Resumen de parámetros</li>
        <li>Tablas de resultados</li>
        <li>Gráficos incluidos</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(MODULOS["06"], label="Ir a Generar Reporte",
                     icon="📋", width='stretch')

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
