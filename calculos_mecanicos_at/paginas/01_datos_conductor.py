"""
Página de selección y visualización de datos del conductor.
Usa exclusivamente los datos del archivo CABLES ACSR.xlsx.
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.estilos import encabezado_pagina


# Constantes de materiales para ACSR
E_ALUMINIO = 6300    # kgf/mm² - Módulo de elasticidad del aluminio EC
E_ACERO = 20000      # kgf/mm² - Módulo de elasticidad del acero galvanizado
ALPHA_ALUMINIO = 23e-6    # 1/°C - Coeficiente de dilatación térmica aluminio
ALPHA_ACERO = 11.5e-6     # 1/°C - Coeficiente de dilatación térmica acero


@st.cache_data
def cargar_conductores_excel():
    """Carga la base de datos de conductores ACSR desde el archivo Excel."""
    ruta = Path(__file__).parent.parent.parent / "CABLES ACSR.xlsx"
    if not ruta.exists():
        st.error(f"No se encontró el archivo: {ruta}")
        st.stop()

    df = pd.read_excel(ruta, sheet_name='cables', header=0)

    # Eliminar la fila de sub-encabezados (fila 0 con 'ALUMINIO', 'ACERO', etc.)
    df = df.iloc[1:].reset_index(drop=True)

    # Renombrar columnas
    df.columns = [
        'CODIGO', 'CORRIENTE', 'PESO_KG_KM', 'CALIBRE',
        'HILOS_AL', 'HILOS_AC', 'DIAMETRO_MM',
        'SECCION_AL_MM2', 'SECCION_TOTAL_MM2', 'RMG_MM',
        'CARGA_ROTURA_KG', 'RESISTENCIA_75',
        'DIAM_HILO_AL_MM', 'DIAM_HILO_AC_MM', 'Xa',
        'AUX1', 'AUX2', 'AUX3', 'AUX4'
    ]

    # Convertir columnas numéricas
    cols_num = ['CORRIENTE', 'PESO_KG_KM', 'HILOS_AL', 'HILOS_AC', 'DIAMETRO_MM',
                'SECCION_AL_MM2', 'SECCION_TOTAL_MM2', 'RMG_MM', 'CARGA_ROTURA_KG',
                'RESISTENCIA_75', 'DIAM_HILO_AL_MM', 'DIAM_HILO_AC_MM', 'Xa']
    for col in cols_num:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Eliminar filas sin código
    df = df.dropna(subset=['CODIGO']).reset_index(drop=True)

    # Calcular sección de acero
    df['SECCION_AC_MM2'] = df['SECCION_TOTAL_MM2'] - df['SECCION_AL_MM2']

    # Calcular módulo de elasticidad combinado
    # E = (Sal × EAl + Sac × EAc) / (Sal + Sac)
    df['E_COMBINADO'] = (
        (df['SECCION_AL_MM2'] * E_ALUMINIO + df['SECCION_AC_MM2'] * E_ACERO)
        / df['SECCION_TOTAL_MM2']
    )

    # Calcular coeficiente de dilatación combinado
    # α = (αAl × Sal × EAl + αAc × Sac × EAc) / (Sal × EAl + Sac × EAc)
    num_alpha = (ALPHA_ALUMINIO * df['SECCION_AL_MM2'] * E_ALUMINIO +
                 ALPHA_ACERO * df['SECCION_AC_MM2'] * E_ACERO)
    den_alpha = (df['SECCION_AL_MM2'] * E_ALUMINIO + df['SECCION_AC_MM2'] * E_ACERO)
    df['ALPHA_COMBINADO'] = num_alpha / den_alpha

    # Carga específica (peso unitario / sección)
    df['CARGA_ESPECIFICA'] = (df['PESO_KG_KM'] / 1000) / df['SECCION_TOTAL_MM2']

    # Tensión de rotura unitaria
    df['TENSION_ROTURA_UNIT'] = df['CARGA_ROTURA_KG'] / df['SECCION_TOTAL_MM2']

    return df


def conductor_a_dict(row):
    """Convierte una fila del DataFrame a diccionario compatible con session_state."""
    sal = row['SECCION_AL_MM2']
    sac = row['SECCION_AC_MM2']
    s_total = row['SECCION_TOTAL_MM2']

    return {
        'codigo_bird': row['CODIGO'],
        'calibre_awg_kcmil': str(row['CALIBRE']),
        'seccion_total_mm2': s_total,
        'seccion_aluminio_mm2': sal,
        'seccion_acero_mm2': sac,
        'diametro_mm': row['DIAMETRO_MM'],
        'peso_kg_km': row['PESO_KG_KM'],
        'carga_rotura_kgf': row['CARGA_ROTURA_KG'],
        'modulo_elasticidad_final_kgf_mm2': row['E_COMBINADO'],
        'modulo_elasticidad_inicial_kgf_mm2': row['E_COMBINADO'],
        'coef_dilatacion_1_C': row['ALPHA_COMBINADO'],
        'resistencia_ac_75C_ohm_km': row['RESISTENCIA_75'],
        'ampacidad_75C_A': row['CORRIENTE'],
        'hilos_aluminio': int(row['HILOS_AL']),
        'hilos_acero': int(row['HILOS_AC']),
        'diam_hilo_al_mm': row['DIAM_HILO_AL_MM'],
        'diam_hilo_ac_mm': row['DIAM_HILO_AC_MM'],
        'rmg_mm': row['RMG_MM'],
        'xa': row.get('Xa', 0),
        'carga_especifica': row['CARGA_ESPECIFICA'],
        'tension_rotura_unitaria': row['TENSION_ROTURA_UNIT'],
    }


# Cargar datos
df_conductores = cargar_conductores_excel()

# Título
encabezado_pagina(
    "🔌",
    "Datos del Conductor ACSR",
    "Seleccione el conductor ACSR para el diseño de la línea. Los datos provienen "
    "del catálogo <b>CABLES ACSR.xlsx</b> con 67 conductores normalizados."
)

# Selección de conductor
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Selección de Conductor")

    # Modo de búsqueda
    modo_busqueda = st.radio(
        "Buscar por",
        options=["Código (nombre)", "Calibre (AWG/kcmil)"],
        horizontal=True
    )

    if modo_busqueda == "Código (nombre)":
        codigos = df_conductores['CODIGO'].tolist()
        seleccion = st.selectbox(
            "Código del conductor",
            options=codigos,
            help="Nombre comercial del conductor ACSR (código de ave)"
        )
        idx = df_conductores[df_conductores['CODIGO'] == seleccion].index[0]
    else:
        calibres = df_conductores['CALIBRE'].unique().tolist()
        calibre_sel = st.selectbox(
            "Calibre",
            options=calibres,
            help="Calibre en AWG o kcmil"
        )
        # Si hay varios con el mismo calibre, mostrar opciones
        opciones = df_conductores[df_conductores['CALIBRE'] == calibre_sel]
        if len(opciones) > 1:
            codigo_sel = st.selectbox(
                "Código (varios conductores con este calibre)",
                options=opciones['CODIGO'].tolist()
            )
            idx = opciones[opciones['CODIGO'] == codigo_sel].index[0]
        else:
            idx = opciones.index[0]

    # Obtener conductor seleccionado
    row_sel = df_conductores.loc[idx]
    conductor = conductor_a_dict(row_sel)

    # Guardar en session state
    st.session_state['conductor'] = conductor
    st.session_state['tipo_conductor'] = 'ACSR'
    st.session_state['calibre'] = conductor['codigo_bird']

with col2:
    st.subheader(f"Propiedades: {conductor['codigo_bird']} ({conductor['calibre_awg_kcmil']})")

    # Información básica en métricas
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.metric("Código", conductor['codigo_bird'])
        st.metric("Calibre", conductor['calibre_awg_kcmil'])

    with col_b:
        st.metric("Sección Total", f"{conductor['seccion_total_mm2']:.2f} mm²")
        st.metric("Diámetro", f"{conductor['diametro_mm']:.3f} mm")

    with col_c:
        st.metric("Peso", f"{conductor['peso_kg_km']:.1f} kg/km")
        st.metric("Carga de Rotura", f"{conductor['carga_rotura_kgf']:.1f} kgf")

st.markdown("---")

# Tabla detallada de propiedades
st.subheader("Propiedades Detalladas")

col_prop1, col_prop2 = st.columns(2)

with col_prop1:
    st.markdown("#### Propiedades Mecánicas")

    props_mecanicas = {
        "Propiedad": [
            "Sección aluminio (Sal)",
            "Sección acero (Sac)",
            "Sección total (Sal + Sac)",
            "Diámetro nominal",
            "Peso por kilómetro",
            "Carga de rotura",
            "Tensión rotura unitaria (tR/S)",
            "Hilos aluminio / acero",
            "Diám. hilo Al / Ac",
        ],
        "Valor": [
            f"{conductor['seccion_aluminio_mm2']:.3f}",
            f"{conductor['seccion_acero_mm2']:.3f}",
            f"{conductor['seccion_total_mm2']:.3f}",
            f"{conductor['diametro_mm']:.3f}",
            f"{conductor['peso_kg_km']:.1f}",
            f"{conductor['carga_rotura_kgf']:.1f}",
            f"{conductor['tension_rotura_unitaria']:.4f}",
            f"{conductor['hilos_aluminio']} / {conductor['hilos_acero']}",
            f"{conductor['diam_hilo_al_mm']:.4f} / {conductor['diam_hilo_ac_mm']:.4f}",
        ],
        "Unidad": [
            "mm²", "mm²", "mm²", "mm", "kg/km", "kgf",
            "kgf/mm²", "-", "mm"
        ]
    }
    st.dataframe(pd.DataFrame(props_mecanicas), width='stretch', hide_index=True)

with col_prop2:
    st.markdown("#### Propiedades Calculadas y Eléctricas")

    props_calc = {
        "Propiedad": [
            "Módulo elasticidad combinado (E)",
            "Coef. dilatación combinado (α)",
            "Carga específica (w = W/S)",
            "Resistencia AC a 75°C",
            "Corriente nominal",
            "RMG",
        ],
        "Valor": [
            f"{conductor['modulo_elasticidad_final_kgf_mm2']:.1f}",
            f"{conductor['coef_dilatacion_1_C']:.6e}",
            f"{conductor['carga_especifica']:.6e}",
            f"{conductor['resistencia_ac_75C_ohm_km']:.4f}" if conductor['resistencia_ac_75C_ohm_km'] else "N/A",
            f"{conductor['ampacidad_75C_A']:.0f}",
            f"{conductor['rmg_mm']:.5f}" if conductor['rmg_mm'] else "N/A",
        ],
        "Unidad": [
            "kgf/mm²", "1/°C", "kg/m/mm²",
            "Ω/km", "A", "mm"
        ]
    }
    st.dataframe(pd.DataFrame(props_calc), width='stretch', hide_index=True)

    # Fórmulas utilizadas
    st.markdown("#### Fórmulas de Composición")
    st.markdown(f"""
    - **E** = (Sal×EAl + Sac×EAc) / (Sal+Sac)
      = ({conductor['seccion_aluminio_mm2']:.2f}×{E_ALUMINIO} + {conductor['seccion_acero_mm2']:.2f}×{E_ACERO}) / {conductor['seccion_total_mm2']:.2f}
      = **{conductor['modulo_elasticidad_final_kgf_mm2']:.1f}** kgf/mm²
    - **α** = (αAl×Sal×EAl + αAc×Sac×EAc) / (Sal×EAl + Sac×EAc)
      = **{conductor['coef_dilatacion_1_C']:.6e}** 1/°C
    """)

st.markdown("---")

# Factores de seguridad y tensiones de referencia
st.subheader("Tensiones de Referencia (Factor de Seguridad)")

tR = conductor['tension_rotura_unitaria']
S = conductor['seccion_total_mm2']
CR = conductor['carga_rotura_kgf']

col_fs1, col_fs2 = st.columns(2)

with col_fs1:
    st.markdown(f"""
    | FS | Tensión unitaria (kg/mm²) | Tensión total (kgf) | % Rotura |
    |---|---|---|---|
    | **FS = 2** | {tR/2:.4f} | {CR/2:.1f} | 50.0% |
    | **FS = 3** | {tR/3:.4f} | {CR/3:.1f} | 33.3% |
    | **FS = 5** (EDS) | {tR/5:.4f} | {CR/5:.1f} | 20.0% |
    """)

with col_fs2:
    st.markdown("""
    **Criterios CREG 025/1995:**
    - **Hip. A** (Viento máx): 2 ≤ FS ≤ 3
    - **Hip. B** (Temp. mín): 2 ≤ FS ≤ 3
    - **Hip. C** (EDS): FS ≥ 5
    - **Hip. D** (Flecha máx): 2 ≤ FS ≤ 3
    """)

st.markdown("---")

# Tabla comparativa de todos los conductores
st.subheader("Catálogo Completo de Conductores ACSR")

# Crear DataFrame de comparación
df_comp = df_conductores[[
    'CODIGO', 'CALIBRE', 'SECCION_TOTAL_MM2', 'DIAMETRO_MM',
    'PESO_KG_KM', 'CARGA_ROTURA_KG', 'CORRIENTE', 'E_COMBINADO',
    'SECCION_AL_MM2', 'SECCION_AC_MM2'
]].copy()

df_comp.columns = [
    'Código', 'Calibre', 'Sección (mm²)', 'Diámetro (mm)',
    'Peso (kg/km)', 'Rotura (kgf)', 'Corriente (A)', 'E (kgf/mm²)',
    'Sal (mm²)', 'Sac (mm²)'
]

df_comp = df_comp.sort_values('Sección (mm²)')

# Resaltar fila seleccionada
def resaltar_seleccionado(row):
    if row['Código'] == conductor['codigo_bird']:
        return ['background-color: #d4edda'] * len(row)
    return [''] * len(row)

st.dataframe(
    df_comp.style.apply(resaltar_seleccionado, axis=1),
    width='stretch',
    hide_index=True,
    height=400
)

# Información del conductor seleccionado
st.markdown("---")
st.info(f"""
**Conductor seleccionado:** {conductor['codigo_bird']} - Calibre {conductor['calibre_awg_kcmil']} (ACSR)
- Sección: {conductor['seccion_total_mm2']:.2f} mm² (Al: {conductor['seccion_aluminio_mm2']:.2f} + Ac: {conductor['seccion_acero_mm2']:.2f})
- Carga de rotura: {conductor['carga_rotura_kgf']:.1f} kgf
- E = {conductor['modulo_elasticidad_final_kgf_mm2']:.1f} kgf/mm², α = {conductor['coef_dilatacion_1_C']:.2e} 1/°C
""")
