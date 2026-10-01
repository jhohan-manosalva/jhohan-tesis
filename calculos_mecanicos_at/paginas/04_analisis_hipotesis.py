"""
Página de análisis de las 4 hipótesis de cálculo según CREG 025/1995.

Metodología del ejemplo de clase:
1. Calcular Fv para cada hipótesis: Fv = 0.0042 × V² × d / 1000
2. Calcular factor de carga: m = √(1 + (Fv/W)²)
3. Condición inicial: Hip C con FS = 5
4. Ecuación de estado C→A, C→B, C→D
5. Verificar FS para cada hipótesis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.hipotesis_calculo import (
    TipoHipotesis, analizar_todas_hipotesis,
    obtener_resumen_hipotesis, generar_tabla_comparativa
)
from modules.cargas_mecanicas import calcular_cargas_hipotesis
from modules.vano_regulador import calcular_vano_critico
from utils.graficas import graficar_comparacion_hipotesis
from utils.estilos import encabezado_pagina


encabezado_pagina(
    "💡",
    "Análisis de Hipótesis de Cálculo",
    "Evaluación de las 4 hipótesis según <b>CREG 025/1995</b> y <b>RETIE</b>. Cada hipótesis "
    "tiene su propia temperatura, velocidad de viento y factor de seguridad requerido."
)

# Verificar datos previos
if 'conductor' not in st.session_state:
    st.warning("Primero debe seleccionar un conductor en la página 'Datos del Conductor'")
    st.stop()

if 'condiciones_ambientales' not in st.session_state:
    st.warning("Primero debe configurar las condiciones ambientales")
    st.stop()

if 'vano_regulador' not in st.session_state:
    st.warning("Primero debe configurar los vanos en 'Cálculo Mecánico'")
    st.stop()

conductor = st.session_state['conductor']
condiciones = st.session_state['condiciones_ambientales']
vano_regulador = st.session_state['vano_regulador']

# Info actual
st.markdown("---")
col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.metric("Conductor", st.session_state.get('calibre', 'N/A'))
with col_info2:
    st.metric("Vano regulador", f"{vano_regulador:.4f} m")
with col_info3:
    st.metric("Zona climática", condiciones.get('nombre_zona', 'N/A'))

st.markdown("---")

# Descripción de hipótesis
st.subheader("Descripción de las Hipótesis (CREG 025/1995)")

with st.expander("Ver descripción detallada", expanded=True):
    col_h1, col_h2 = st.columns(2)

    with col_h1:
        st.markdown("""
        #### Hipótesis A - Viento Máximo
        - **Temperatura:** Coincidente con viento máximo
        - **Viento:** Máximo de diseño (V_max)
        - **FS requerido:** 2 ≤ FS ≤ 3
        - **Propósito:** Cargas máximas sobre estructuras

        #### Hipótesis B - Temperatura Mínima
        - **Temperatura:** Mínima absoluta
        - **Viento:** Reducido
        - **FS requerido:** 2 ≤ FS ≤ 3
        - **Propósito:** Tensión máxima por contracción, flecha mínima
        """)

    with col_h2:
        st.markdown("""
        #### Hipótesis C - Condición EDS (Referencia)
        - **Temperatura:** Media anual
        - **Viento:** Bajo
        - **FS requerido:** FS ≥ 5 (≈ 20% carga rotura)
        - **Propósito:** Operación diaria, prevención de fatiga

        #### Hipótesis D - Flecha Máxima
        - **Temperatura:** Máxima del conductor (70-100°C)
        - **Viento:** Sin viento (0 km/h)
        - **FS requerido:** 2 ≤ FS ≤ 3
        - **Propósito:** Verificar distancias al terreno
        """)

st.markdown("---")

# Configuración del análisis - PARÁMETROS POR HIPÓTESIS
st.subheader("Configuración de las Hipótesis")

# Obtener valores por defecto de las condiciones ambientales
v_max_default = condiciones.get('velocidad_viento_diseno_km_h',
                                condiciones.get('velocidad_viento_diseno_m_s', 25) * 3.6)
t_min_default = condiciones.get('temperatura_minima_C', 15)
t_med_default = condiciones.get('temperatura_media_C', 20)
t_max_default = condiciones.get('temperatura_operacion_normal_C', 75)

st.markdown("Configure los parámetros de **cada hipótesis** (temperatura, viento, FS):")

col_a, col_b, col_c, col_d = st.columns(4)

with col_a:
    st.markdown("**Hip. A - Viento Máx**")
    temp_A = st.number_input("Temp A (°C)", value=float(t_min_default + 5), key="temp_a")
    viento_A = st.number_input("Viento A (km/h)", value=float(v_max_default), key="viento_a")
    fs_min_A = st.number_input("FS mín A", value=3.0, min_value=1.0, max_value=10.0, key="fs_a")

with col_b:
    st.markdown("**Hip. B - Temp. Mín**")
    temp_B = st.number_input("Temp B (°C)", value=float(t_min_default), key="temp_b")
    viento_B = st.number_input("Viento B (km/h)", value=float(v_max_default * 0.15), key="viento_b")
    fs_min_B = st.number_input("FS mín B", value=2.0, min_value=1.0, max_value=10.0, key="fs_b")

with col_c:
    st.markdown("**Hip. C - EDS (Ref.)**")
    temp_C = st.number_input("Temp C (°C)", value=float(t_med_default), key="temp_c")
    viento_C = st.number_input("Viento C (km/h)", value=10.0, key="viento_c")
    fs_min_C = st.number_input("FS mín C", value=5.0, min_value=2.0, max_value=10.0, key="fs_c")

with col_d:
    st.markdown("**Hip. D - Flecha Máx**")
    temp_D = st.number_input("Temp D (°C)", value=float(t_max_default), key="temp_d")
    viento_D = st.number_input("Viento D (km/h)", value=0.0, key="viento_d")
    fs_min_D = st.number_input("FS mín D", value=2.0, min_value=1.0, max_value=10.0, key="fs_d")

# Construir parámetros
params_hipotesis = {
    'A': {'temperatura': temp_A, 'viento_kmh': viento_A, 'fs_min': fs_min_A},
    'B': {'temperatura': temp_B, 'viento_kmh': viento_B, 'fs_min': fs_min_B},
    'C': {'temperatura': temp_C, 'viento_kmh': viento_C, 'fs_min': fs_min_C},
    'D': {'temperatura': temp_D, 'viento_kmh': viento_D, 'fs_min': fs_min_D},
}

# Mostrar tabla de Fv y m antes de calcular
st.markdown("---")
st.subheader("Cargas por Hipótesis (Fv y m)")

diametro = conductor.get('diametro_mm', 20)
peso_kg_m = conductor.get('peso_kg_km', 1000) / 1000

tabla_cargas = []
for hip_key, params in params_hipotesis.items():
    cargas = calcular_cargas_hipotesis(conductor, params['viento_kmh'])
    tabla_cargas.append({
        'Hipótesis': hip_key,
        'Temp (°C)': params['temperatura'],
        'V (km/h)': params['viento_kmh'],
        f'Fv = 0.0042×V²×{diametro:.3f}/1000': round(cargas['fuerza_viento'], 4),
        f'm = √(1+(Fv/{peso_kg_m:.4f})²)': round(cargas['factor_carga'], 4),
        'W\' (kg/m)': round(cargas['peso_resultante'], 4),
        'g = W\'/S (kg/m/mm²)': f"{cargas['carga_especifica']:.6e}",
        'FS mín': params['fs_min'],
    })

st.dataframe(pd.DataFrame(tabla_cargas), width='stretch', hide_index=True)

st.markdown("---")

# Ejecutar análisis
if st.button("Ejecutar Análisis de Hipótesis", type="primary", width='stretch'):

    with st.spinner("Analizando hipótesis..."):

        try:
            zona_climatica = {
                'nombre': condiciones.get('nombre_zona', 'N/A'),
                'temperatura_minima_C': t_min_default,
                'temperatura_media_C': t_med_default,
                'velocidad_viento_diseno_km_h': v_max_default,
            }

            resultados = analizar_todas_hipotesis(
                conductor=conductor,
                vano_regulador=vano_regulador,
                zona_climatica=zona_climatica,
                temperatura_operacion=temp_D,
                altitud_msnm=condiciones.get('altitud_msnm', 0),
                params_hipotesis=params_hipotesis
            )

            st.session_state['resultados_hipotesis'] = resultados

            resumen = obtener_resumen_hipotesis(resultados)

            st.success("Análisis completado")

            # Resumen
            st.markdown("---")
            st.subheader("Resumen del Análisis")

            seccion = conductor.get('seccion_total_mm2', 100)
            carga_rotura = conductor.get('carga_rotura_kgf', 10000)
            tR = carga_rotura / seccion

            col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
            with col_sum1:
                st.metric("Hip. crítica", resumen['nombre_hipotesis_critica'].split('-')[0].strip(),
                         delta="Todas cumplen" if resumen['todas_cumplen'] else "Revisar")
            with col_sum2:
                st.metric("Tensión máxima", f"{resumen['tension_maxima']:.4f} kg/mm²")
            with col_sum3:
                st.metric("Flecha máxima", f"{resumen['flecha_maxima']:.4f} m")
            with col_sum4:
                st.metric("tR unitaria", f"{tR:.4f} kg/mm²")

            # Tabla comparativa
            st.markdown("---")
            st.subheader("Tabla Comparativa de Resultados")

            tabla = generar_tabla_comparativa(resultados)
            df_tabla = pd.DataFrame(tabla)

            def colorear_cumplimiento(val):
                if val == '✓':
                    return 'background-color: #d4edda; color: #155724'
                elif val == '✗':
                    return 'background-color: #f8d7da; color: #721c24'
                return ''

            st.dataframe(
                df_tabla.style.map(colorear_cumplimiento, subset=['Cumple']),
                width='stretch',
                hide_index=True
            )

            # Tensiones totales
            st.markdown("---")
            st.subheader("Tensiones y Alturas de Torre")

            for tipo, res in resultados.items():
                hip_letter = res.tipo.value
                t_hip = res.tension_calculada
                T_hip = res.tension_total
                f_hip = res.flecha
                fs_hip = res.factor_seguridad

                status = "✓" if res.cumple_limite else "✗"
                st.markdown(f"""
                **Hip {hip_letter}**: t = {t_hip:.4f} kg/mm², T = {T_hip:.1f} kgf,
                f = {f_hip:.4f} m, FS = {fs_hip:.2f} {status}
                """)

            # Gráficos
            st.markdown("---")
            st.subheader("Gráficos Comparativos")

            col_graf1, col_graf2 = st.columns(2)
            with col_graf1:
                fig_tension = graficar_comparacion_hipotesis(resultados, tipo="tension")
                st.plotly_chart(fig_tension, width='stretch')
            with col_graf2:
                fig_flecha = graficar_comparacion_hipotesis(resultados, tipo="flecha")
                st.plotly_chart(fig_flecha, width='stretch')

            # Verificación de cumplimiento
            st.markdown("---")
            st.subheader("Verificación de Cumplimiento")

            cols = st.columns(4)
            for i, (tipo, resultado) in enumerate(resultados.items()):
                with cols[i]:
                    if resultado.cumple_limite:
                        st.success(f"""
                        **{resultado.tipo.value} - CUMPLE**

                        t = {resultado.tension_calculada:.4f} kg/mm²
                        FS = {resultado.factor_seguridad:.2f}
                        FS mín = {resultado.fs_minimo}
                        m = {resultado.factor_carga:.4f}
                        """)
                    else:
                        st.error(f"""
                        **{resultado.tipo.value} - NO CUMPLE**

                        t = {resultado.tension_calculada:.4f} kg/mm²
                        FS = {resultado.factor_seguridad:.2f}
                        FS mín = {resultado.fs_minimo}
                        """)

            # Vano crítico
            st.markdown("---")
            st.subheader("Análisis de Vano Crítico")

            try:
                alpha = conductor.get('coef_dilatacion_1_C', 0.0000193)
                cargas_A = calcular_cargas_hipotesis(conductor, viento_A)
                cargas_B = calcular_cargas_hipotesis(conductor, viento_B)

                tmax_adm = tR / fs_min_A  # Tensión máxima admisible (con FS de hip A)

                vano_critico = calcular_vano_critico(
                    tmax=tmax_adm,
                    W=peso_kg_m,
                    alpha=alpha,
                    theta_A=temp_A,
                    theta_B=temp_B,
                    mA=cargas_A['factor_carga'],
                    mB=cargas_B['factor_carga'],
                )

                col_vc1, col_vc2 = st.columns(2)
                with col_vc1:
                    st.metric("Vano regulador (ar)", f"{vano_regulador:.4f} m")
                    if vano_critico != float('inf'):
                        st.metric("Vano crítico (ac)", f"{vano_critico:.4f} m")
                    else:
                        st.metric("Vano crítico (ac)", "No aplica")

                with col_vc2:
                    st.markdown(f"""
                    **Fórmula:** ac = (tmax/W) × √(24×α×(θA-θB) / (mA²-mB²))

                    - tmax = {tmax_adm:.4f} kg/mm²
                    - W = {peso_kg_m:.4f} kg/m
                    - α = {alpha:.6e} 1/°C
                    - θA = {temp_A}°C, θB = {temp_B}°C
                    - mA = {cargas_A['factor_carga']:.4f}, mB = {cargas_B['factor_carga']:.4f}
                    """)

                    if vano_critico != float('inf'):
                        if vano_regulador > vano_critico:
                            st.info("ar > ac → **Hipótesis A (viento)** domina")
                        elif vano_regulador < vano_critico:
                            st.info("ar < ac → **Hipótesis B (temperatura)** domina")
                        else:
                            st.info("ar ≈ ac → Hipótesis A = Hipótesis B")

            except Exception as e:
                st.warning(f"No se pudo calcular el vano crítico: {e}")

        except Exception as e:
            st.error(f"Error durante el análisis: {e}")
            import traceback
            st.code(traceback.format_exc())

elif 'resultados_hipotesis' in st.session_state:
    st.info("Mostrando resultados del análisis anterior. Presione el botón para recalcular.")
    resultados = st.session_state['resultados_hipotesis']
    tabla = generar_tabla_comparativa(resultados)
    st.dataframe(pd.DataFrame(tabla), width='stretch', hide_index=True)
