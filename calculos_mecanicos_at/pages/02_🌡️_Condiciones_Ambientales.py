"""
Página de configuración de condiciones ambientales.
"""

import streamlit as st
import json
import pandas as pd
from pathlib import Path
import sys

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.cargas_mecanicas import calcular_densidad_aire

st.set_page_config(page_title="Condiciones Ambientales", page_icon="🌡️", layout="wide")

# Cargar zonas climáticas
@st.cache_data
def cargar_zonas():
    """Carga la base de datos de zonas climáticas desde JSON."""
    ruta = Path(__file__).parent.parent / "config" / "zonas_climaticas.json"
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)

zonas = cargar_zonas()['zonas']

# Título
st.title("🌡️ Condiciones Ambientales")
st.markdown("""
Configure las condiciones climáticas y ambientales de diseño según la ubicación
del proyecto en Colombia. Los parámetros predefinidos están basados en el RETIE
y las condiciones típicas de cada zona geográfica.
""")

st.markdown("---")

# Selección de zona
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📍 Selección de Zona")

    # Selector de zona predefinida
    nombres_zonas = {k: v['nombre'] for k, v in zonas.items()}
    zona_seleccionada = st.selectbox(
        "Zona climática",
        options=list(zonas.keys()),
        format_func=lambda x: zonas[x]['nombre'],
        help="Seleccione la zona geográfica más cercana al proyecto"
    )

    zona = zonas[zona_seleccionada]

    # Mostrar departamentos
    st.markdown(f"**Departamentos:** {', '.join(zona.get('departamentos', []))}")
    st.markdown(f"**Clasificación RETIE:** {zona.get('zona_retie', 'N/A')}")

with col2:
    st.subheader("📊 Parámetros Climáticos")

    # Métricas principales
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.metric(
            "Altitud de referencia",
            f"{zona.get('altitud_referencia_msnm', 0):,} msnm"
        )
        st.metric(
            "Humedad relativa",
            f"{zona.get('humedad_relativa_media_pct', 0)}%"
        )

    with col_b:
        st.metric(
            "Temperatura mínima",
            f"{zona.get('temperatura_minima_C', 0)}°C"
        )
        st.metric(
            "Temperatura media",
            f"{zona.get('temperatura_media_C', 0)}°C"
        )

    with col_c:
        st.metric(
            "Temperatura máxima",
            f"{zona.get('temperatura_maxima_ambiente_C', 0)}°C"
        )
        st.metric(
            "Viento de diseño",
            f"{zona.get('velocidad_viento_diseno_km_h', 0)} km/h"
        )

st.markdown("---")

# Parámetros editables
st.subheader("⚙️ Parámetros de Diseño Editables")
st.markdown("Puede ajustar los valores según las condiciones específicas del proyecto.")

col_edit1, col_edit2, col_edit3 = st.columns(3)

with col_edit1:
    st.markdown("#### Altitud")
    altitud = st.number_input(
        "Altitud del proyecto (msnm)",
        value=zona.get('altitud_referencia_msnm', 0),
        min_value=0,
        max_value=5000,
        step=50,
        help="Altitud promedio de la línea sobre el nivel del mar"
    )

    # Calcular densidad del aire
    densidad = calcular_densidad_aire(altitud)
    st.metric("Densidad del aire calculada", f"{densidad:.4f} kg/m³")

    # Factor de corrección por altitud
    if altitud > 1000:
        factor_altitud = 1 + 0.03 * ((altitud - 1000) / 300)
        st.warning(f"⚠️ Factor de corrección por altitud: {factor_altitud:.3f}")
    else:
        factor_altitud = 1.0
        st.success("✓ No requiere corrección por altitud")

with col_edit2:
    st.markdown("#### Temperaturas")

    temp_minima = st.number_input(
        "Temperatura mínima (°C)",
        value=zona.get('temperatura_minima_C', 15),
        min_value=-10,
        max_value=30,
        step=1,
        help="Temperatura mínima absoluta del aire (Hipótesis B)"
    )

    temp_media = st.number_input(
        "Temperatura media (°C)",
        value=zona.get('temperatura_media_C', 20),
        min_value=0,
        max_value=40,
        step=1,
        help="Temperatura promedio anual (Condición EDS)"
    )

    temp_maxima_ambiente = st.number_input(
        "Temperatura máxima ambiente (°C)",
        value=zona.get('temperatura_maxima_ambiente_C', 35),
        min_value=20,
        max_value=50,
        step=1,
        help="Temperatura máxima del aire"
    )

with col_edit3:
    st.markdown("#### Viento")

    viento_kmh = st.number_input(
        "Velocidad de viento de diseño (km/h)",
        value=zona.get('velocidad_viento_diseno_km_h', 90),
        min_value=50,
        max_value=200,
        step=5,
        help="Velocidad de viento según RETIE/NSR-10"
    )

    viento_ms = viento_kmh / 3.6
    st.metric("Velocidad de viento", f"{viento_ms:.1f} m/s")

    temp_coincidente_viento = st.number_input(
        "Temperatura coincidente con viento máx. (°C)",
        value=15,
        min_value=0,
        max_value=30,
        step=1,
        help="Temperatura típica cuando ocurre viento máximo (Hipótesis A)"
    )

st.markdown("---")

# Configuración de operación del conductor
st.subheader("🔌 Configuración de Operación")

col_op1, col_op2 = st.columns(2)

with col_op1:
    st.markdown("#### Temperatura del Conductor")

    temp_operacion_normal = st.number_input(
        "Temperatura de operación normal (°C)",
        value=75,
        min_value=50,
        max_value=100,
        step=5,
        help="Temperatura máxima del conductor en operación normal (Hipótesis D)"
    )

    temp_emergencia = st.number_input(
        "Temperatura de emergencia (°C)",
        value=100,
        min_value=75,
        max_value=150,
        step=5,
        help="Temperatura máxima en condición de emergencia"
    )

with col_op2:
    st.markdown("#### Tensión EDS")

    tension_eds_pct = st.slider(
        "Porcentaje EDS (%)",
        min_value=12,
        max_value=22,
        value=18,
        step=1,
        help="Tensión de operación diaria (Every Day Stress) como % de la carga de rotura"
    )

    st.info(f"""
    **Condición EDS:** {tension_eds_pct}% de la carga de rotura

    La tensión EDS es la condición de referencia para todos los cálculos.
    Valores típicos: 15-20%

    - EDS bajo (15%): Mayor flecha, menor fatiga
    - EDS alto (20%): Menor flecha, mayor tensión
    """)

st.markdown("---")

# Resumen de parámetros
st.subheader("📋 Resumen de Condiciones de Diseño")

# Guardar en session state
condiciones = {
    'nombre_zona': zona.get('nombre', 'N/A'),
    'altitud_msnm': altitud,
    'densidad_aire': densidad,
    'factor_altitud': factor_altitud,
    'temperatura_minima_C': temp_minima,
    'temperatura_media_C': temp_media,
    'temperatura_maxima_ambiente_C': temp_maxima_ambiente,
    'temperatura_coincidente_viento_C': temp_coincidente_viento,
    'velocidad_viento_diseno_km_h': viento_kmh,
    'velocidad_viento_diseno_m_s': viento_ms,
    'temperatura_operacion_normal_C': temp_operacion_normal,
    'temperatura_emergencia_C': temp_emergencia,
    'tension_eds_porcentaje': tension_eds_pct,
    'humedad_relativa_pct': zona.get('humedad_relativa_media_pct', 75),
    'zona_retie': zona.get('zona_retie', 'N/A')
}

st.session_state['condiciones_ambientales'] = condiciones
st.session_state['zona_climatica'] = zona

# Tabla resumen
col_res1, col_res2 = st.columns(2)

with col_res1:
    datos_resumen = {
        'Parámetro': [
            'Zona climática',
            'Altitud',
            'Densidad del aire',
            'Factor corrección altitud',
            'Temperatura mínima',
            'Temperatura media (EDS)',
            'Temperatura máx. ambiente'
        ],
        'Valor': [
            zona.get('nombre', 'N/A'),
            f"{altitud:,} msnm",
            f"{densidad:.4f} kg/m³",
            f"{factor_altitud:.3f}",
            f"{temp_minima}°C",
            f"{temp_media}°C",
            f"{temp_maxima_ambiente}°C"
        ]
    }
    st.dataframe(pd.DataFrame(datos_resumen), use_container_width=True, hide_index=True)

with col_res2:
    datos_resumen2 = {
        'Parámetro': [
            'Temp. coincidente viento',
            'Velocidad viento diseño',
            'Temp. operación conductor',
            'Temp. emergencia',
            'Tensión EDS',
            'Clasificación RETIE',
            'Humedad relativa'
        ],
        'Valor': [
            f"{temp_coincidente_viento}°C",
            f"{viento_kmh} km/h ({viento_ms:.1f} m/s)",
            f"{temp_operacion_normal}°C",
            f"{temp_emergencia}°C",
            f"{tension_eds_pct}%",
            zona.get('zona_retie', 'N/A'),
            f"{zona.get('humedad_relativa_media_pct', 75)}%"
        ]
    }
    st.dataframe(pd.DataFrame(datos_resumen2), use_container_width=True, hide_index=True)

# Tabla comparativa de todas las zonas
st.markdown("---")
with st.expander("📊 Ver tabla comparativa de todas las zonas climáticas"):
    datos_zonas = []
    for clave, z in zonas.items():
        datos_zonas.append({
            'Zona': z['nombre'],
            'Altitud (msnm)': z.get('altitud_referencia_msnm', 0),
            'T. mín (°C)': z.get('temperatura_minima_C', 0),
            'T. media (°C)': z.get('temperatura_media_C', 0),
            'T. máx (°C)': z.get('temperatura_maxima_ambiente_C', 0),
            'Viento (km/h)': z.get('velocidad_viento_diseno_km_h', 0),
            'Clasificación': z.get('zona_retie', 'N/A')
        })

    df_zonas = pd.DataFrame(datos_zonas)

    def resaltar_zona(row):
        if row['Zona'] == zona.get('nombre', ''):
            return ['background-color: #d4edda'] * len(row)
        return [''] * len(row)

    st.dataframe(
        df_zonas.style.apply(resaltar_zona, axis=1),
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")
st.success(f"""
✅ **Condiciones ambientales configuradas:**
Zona: {zona.get('nombre', 'N/A')} | Altitud: {altitud:,} msnm |
Viento: {viento_kmh} km/h | EDS: {tension_eds_pct}%
""")
