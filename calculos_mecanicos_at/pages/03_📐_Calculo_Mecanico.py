"""
Página de cálculo mecánico principal.
Usa la fórmula de viento Fv = 0.0042 × V² × d / 1000 y
la ecuación de cambio de estado según el ejemplo de clase.
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.ecuacion_estado import resolver_ecuacion_estado
from modules.catenaria import (
    calcular_flecha_parabolica, calcular_flecha_catenaria,
    comparar_metodos, calcular_curva_catenaria
)
from modules.cargas_mecanicas import calcular_cargas_hipotesis
from modules.vano_regulador import calcular_vano_regulador, verificar_canton
from utils.graficas import graficar_catenaria_plotly

st.set_page_config(page_title="Cálculo Mecánico", page_icon="📐", layout="wide")

st.title("📐 Cálculo Mecánico")
st.markdown("""
Cálculos mecánicos de tensión, flecha y cargas usando la ecuación de cambio de estado.
- Fuerza de viento: **Fv = 0.0042 × V² × d / 1000**
- Factor de carga: **m = √(1 + (Fv/W)²)**
- Ecuación de estado: **t₂³ + A·t₂² - B = 0**
""")

# Verificar datos previos
if 'conductor' not in st.session_state:
    st.warning("Primero debe seleccionar un conductor en la página 'Datos del Conductor'")
    st.stop()

if 'condiciones_ambientales' not in st.session_state:
    st.warning("Primero debe configurar las condiciones ambientales")
    st.stop()

conductor = st.session_state['conductor']
condiciones = st.session_state['condiciones_ambientales']

st.markdown("---")

# Configuración de vanos
st.subheader("Configuración del Vano")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("#### Ingreso de Vanos")

    modo_ingreso = st.radio(
        "Modo de ingreso",
        options=["Vano único", "Múltiples vanos (cantón)"],
        horizontal=True
    )

    if modo_ingreso == "Vano único":
        vano_unico = st.number_input(
            "Longitud del vano (m)",
            value=300.0, min_value=50.0, max_value=1500.0, step=10.0
        )
        vanos = [vano_unico]
        vano_regulador = vano_unico
    else:
        vanos_texto = st.text_area(
            "Ingrese los vanos separados por comas",
            value="250, 300, 200, 150, 120",
            help="Ejemplo del ejercicio: 250, 300, 200, 150, 120"
        )
        try:
            vanos_texto = vanos_texto.replace('\n', ',')
            vanos = [float(v.strip()) for v in vanos_texto.split(',') if v.strip()]
            if len(vanos) == 0:
                st.error("Debe ingresar al menos un vano")
                st.stop()
            vano_regulador = calcular_vano_regulador(vanos)
        except ValueError as e:
            st.error(f"Error al parsear vanos: {e}")
            st.stop()

with col2:
    st.markdown("#### Resumen del Cantón")

    verificacion = verificar_canton(vanos, vano_regulador)

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("Número de vanos", len(vanos))
        st.metric("Vano regulador (ar)", f"{vano_regulador:.4f} m")
        st.metric("Longitud total", f"{sum(vanos):.1f} m")
    with col_m2:
        st.metric("Vano máximo", f"{max(vanos):.1f} m")
        st.metric("Vano mínimo", f"{min(vanos):.1f} m")
        relacion = verificacion.get('relacion', verificacion.get('relacion_max_regulador'))
        st.metric("Relación max/reg", f"{relacion:.2f}" if isinstance(relacion, (int, float)) else "N/A")

    if verificacion['valido']:
        st.success("Cantón válido")
    else:
        st.error("Cantón inválido - revisar advertencias")
    for adv in verificacion.get('advertencias', []):
        st.warning(adv)

    # Mostrar fórmula del vano regulador
    st.markdown(f"""
    **Fórmula:** ar = √(Σai³ / Σai) = √({sum(v**3 for v in vanos):.1f} / {sum(vanos):.1f}) = **{vano_regulador:.4f} m**
    """)

st.session_state['vanos'] = vanos
st.session_state['vano_regulador'] = vano_regulador

st.markdown("---")

# Parámetros de cálculo
st.subheader("Parámetros de Cálculo")

col_param1, col_param2, col_param3 = st.columns(3)

seccion = conductor.get('seccion_total_mm2', 100)
carga_rotura = conductor.get('carga_rotura_kgf', 10000)
tension_rotura_unitaria = carga_rotura / seccion

with col_param1:
    st.markdown("#### Condición Inicial (EDS - Hip. C)")

    fs_inicial = st.number_input(
        "Factor de Seguridad (FS) para EDS",
        value=5.0, min_value=2.0, max_value=10.0, step=0.5,
        help="FS = 5 según CREG (equivale a 20% de carga de rotura)"
    )
    tension_eds = tension_rotura_unitaria / fs_inicial

    st.metric("Tensión EDS (tc)", f"{tension_eds:.4f} kg/mm²")
    st.metric("% Carga de rotura", f"{1/fs_inicial*100:.1f}%")

    temp_inicial = st.number_input(
        "Temperatura inicial (°C)",
        value=float(condiciones.get('temperatura_media_C', 20)),
        min_value=-10.0, max_value=50.0
    )

    viento_inicial_kmh = st.number_input(
        "Viento inicial (km/h)",
        value=10.0, min_value=0.0, max_value=200.0, step=5.0,
        help="Velocidad de viento en condición EDS"
    )

with col_param2:
    st.markdown("#### Condición Final")

    temp_final = st.number_input(
        "Temperatura final (°C)",
        value=float(condiciones.get('temperatura_operacion_normal_C', 75)),
        min_value=-20.0, max_value=150.0
    )

    viento_final_kmh = st.number_input(
        "Viento final (km/h)",
        value=0.0, min_value=0.0, max_value=200.0, step=5.0,
        help="Velocidad de viento en condición final"
    )

with col_param3:
    st.markdown("#### Método de Solución")

    metodo = st.selectbox(
        "Método numérico",
        options=["cardano", "newton", "brentq"],
        format_func=lambda x: {
            "cardano": "Cardano (Analítico)",
            "newton": "Newton-Raphson (Iterativo)",
            "brentq": "Brent (Híbrido)"
        }[x]
    )

st.markdown("---")

# Ejecutar cálculo
if st.button("Calcular", type="primary", use_container_width=True):

    with st.spinner("Calculando..."):

        E = conductor.get('modulo_elasticidad_final_kgf_mm2', 7700)
        alpha = conductor.get('coef_dilatacion_1_C', 0.0000193)
        diametro = conductor.get('diametro_mm', 20)
        peso_kg_km = conductor.get('peso_kg_km', 1000)

        # Cargas en condición inicial (EDS)
        cargas_ini = calcular_cargas_hipotesis(conductor, viento_inicial_kmh)
        g_inicial = cargas_ini['carga_especifica']

        # Cargas en condición final
        cargas_fin = calcular_cargas_hipotesis(conductor, viento_final_kmh)
        g_final = cargas_fin['carga_especifica']

        try:
            resultado = resolver_ecuacion_estado(
                sigma_1=tension_eds,
                t_1=temp_inicial,
                t_2=temp_final,
                g_1=g_inicial,
                g_2=g_final,
                a=vano_regulador,
                E=E,
                alpha=alpha,
                metodo=metodo
            )

            st.success("Cálculo completado exitosamente")

            st.session_state['resultado_calculo'] = resultado
            st.session_state['cargas'] = {
                'peso_conductor': cargas_fin['peso_conductor'],
                'carga_viento': cargas_fin['fuerza_viento'],
                'peso_resultante': cargas_fin['peso_resultante'],
                'carga_especifica': g_final,
                'carga_especifica_peso_propio': cargas_fin['carga_especifica_peso'],
                'factor_carga': cargas_fin['factor_carga'],
            }

            # Resultados
            st.markdown("---")
            st.subheader("Resultados del Cálculo")

            t2 = resultado['sigma_2']
            tension_total = t2 * seccion
            fs_resultado = tension_rotura_unitaria / t2
            flecha = resultado['flecha']

            col_res1, col_res2, col_res3 = st.columns(3)

            with col_res1:
                st.markdown("#### Tensión")
                st.metric("Tensión unitaria final (t₂)", f"{t2:.4f} kg/mm²")
                st.metric("Tensión total (T)", f"{tension_total:.1f} kgf")
                st.metric("Factor de Seguridad (FS)", f"{fs_resultado:.2f}")

            with col_res2:
                st.markdown("#### Flecha")
                st.metric("Flecha máxima", f"{flecha:.4f} m")
                # Parámetro catenario h = t₂/w
                w = cargas_fin['carga_especifica_peso']
                h_cat = t2 / w if w > 0 else 0
                st.metric("Parámetro catenario (h=t/w)", f"{h_cat:.4f} m")
                st.metric("Relación f/a", f"{(flecha/vano_regulador)*100:.3f}%")

            with col_res3:
                st.markdown("#### Cargas")
                st.metric("Fv (viento)", f"{cargas_fin['fuerza_viento']:.4f} kg/m")
                st.metric("Factor carga (m)", f"{cargas_fin['factor_carga']:.4f}")
                st.metric("Longitud conductor", f"{resultado['longitud_conductor']:.3f} m")

            # Tabla detallada
            st.markdown("---")
            st.subheader("Detalle del Cálculo")

            col_det1, col_det2 = st.columns(2)

            with col_det1:
                st.markdown("**Datos de Entrada**")
                datos_entrada = {
                    'Parámetro': [
                        'Temperatura inicial (°C)', 'Temperatura final (°C)',
                        'Viento inicial (km/h)', 'Viento final (km/h)',
                        'Tensión inicial tc (kg/mm²)', 'FS inicial',
                        'Vano regulador (m)',
                        'E (kgf/mm²)', 'α (1/°C)',
                        'Fv inicial (kg/m)', 'm inicial',
                        'g₁ (kg/m/mm²)',
                        'Fv final (kg/m)', 'm final',
                        'g₂ (kg/m/mm²)',
                    ],
                    'Valor': [
                        f"{temp_inicial}", f"{temp_final}",
                        f"{viento_inicial_kmh}", f"{viento_final_kmh}",
                        f"{tension_eds:.4f}", f"{fs_inicial}",
                        f"{vano_regulador:.4f}",
                        f"{E:.1f}", f"{alpha:.6e}",
                        f"{cargas_ini['fuerza_viento']:.4f}", f"{cargas_ini['factor_carga']:.4f}",
                        f"{g_inicial:.6e}",
                        f"{cargas_fin['fuerza_viento']:.4f}", f"{cargas_fin['factor_carga']:.4f}",
                        f"{g_final:.6e}",
                    ]
                }
                st.dataframe(pd.DataFrame(datos_entrada), use_container_width=True, hide_index=True)

            with col_det2:
                st.markdown("**Resultados**")
                datos_salida = {
                    'Parámetro': [
                        'Parámetro A', 'Parámetro B',
                        'Tensión final t₂ (kg/mm²)', 'Tensión total T (kgf)',
                        'Factor de seguridad FS',
                        'Flecha máxima (m)', 'Longitud conductor (m)',
                        'Método usado', 'ΔT (°C)',
                    ],
                    'Valor': [
                        f"{resultado['parametro_A']:.4f}", f"{resultado['parametro_B']:.4f}",
                        f"{t2:.4f}", f"{tension_total:.1f}",
                        f"{fs_resultado:.2f}",
                        f"{flecha:.4f}", f"{resultado['longitud_conductor']:.3f}",
                        resultado['metodo_usado'], f"{temp_final - temp_inicial}",
                    ]
                }
                st.dataframe(pd.DataFrame(datos_salida), use_container_width=True, hide_index=True)

            # Calcular hipótesis adicionales
            st.markdown("---")
            st.subheader("Comparación de Hipótesis")

            hipotesis_config = [
                {
                    'nombre': 'Hip. A - Viento máx.',
                    'temp': float(condiciones.get('temperatura_coincidente_viento_C', 15)),
                    'viento_kmh': float(condiciones.get('velocidad_viento_diseno_km_h', 90)),
                    'color': '#e74c3c',
                    'dash': 'solid',
                },
                {
                    'nombre': 'Hip. B - Temp. mínima',
                    'temp': float(condiciones.get('temperatura_minima_C', 10)),
                    'viento_kmh': 0.0,
                    'color': '#3498db',
                    'dash': 'dash',
                },
                {
                    'nombre': 'Hip. C - EDS',
                    'temp': temp_inicial,
                    'viento_kmh': viento_inicial_kmh,
                    'color': '#2ecc71',
                    'dash': 'dot',
                },
                {
                    'nombre': 'Hip. D - Temp. máx. operación',
                    'temp': float(condiciones.get('temperatura_operacion_normal_C', 75)),
                    'viento_kmh': 0.0,
                    'color': '#f39c12',
                    'dash': 'dashdot',
                },
            ]

            resultados_hipotesis = []
            hipotesis_grafica = []

            for hip in hipotesis_config:
                cargas_hip = calcular_cargas_hipotesis(conductor, hip['viento_kmh'])
                g_hip = cargas_hip['carga_especifica']
                try:
                    res_hip = resolver_ecuacion_estado(
                        sigma_1=tension_eds,
                        t_1=temp_inicial,
                        t_2=hip['temp'],
                        g_1=g_inicial,
                        g_2=g_hip,
                        a=vano_regulador,
                        E=E,
                        alpha=alpha,
                        metodo=metodo
                    )
                    fs_hip = tension_rotura_unitaria / res_hip['sigma_2']
                    resultados_hipotesis.append({
                        'Hipótesis': hip['nombre'],
                        'Temp. (°C)': hip['temp'],
                        'Viento (km/h)': hip['viento_kmh'],
                        'Tensión t₂ (kg/mm²)': f"{res_hip['sigma_2']:.4f}",
                        'Flecha (m)': f"{res_hip['flecha']:.4f}",
                        'FS': f"{fs_hip:.2f}",
                    })
                    hipotesis_grafica.append({
                        'nombre': hip['nombre'],
                        'flecha': res_hip['flecha'],
                        'color': hip['color'],
                        'dash': hip['dash'],
                        'width': 3,
                    })
                except (ValueError, Exception):
                    resultados_hipotesis.append({
                        'Hipótesis': hip['nombre'],
                        'Temp. (°C)': hip['temp'],
                        'Viento (km/h)': hip['viento_kmh'],
                        'Tensión t₂ (kg/mm²)': 'Error',
                        'Flecha (m)': 'Error',
                        'FS': '-',
                    })

            st.dataframe(pd.DataFrame(resultados_hipotesis), use_container_width=True, hide_index=True)

            # Gráfico con todas las hipótesis
            st.markdown("---")
            st.subheader("Perfil del Conductor - Todas las Hipótesis")

            altura_soporte = st.slider("Altura del punto de sujeción (m)", min_value=10, max_value=50, value=20)

            fig = graficar_catenaria_plotly(
                vano=vano_regulador,
                flecha=flecha,
                altura_soporte=altura_soporte,
                titulo=f"Perfil del Conductor - Vano regulador: {vano_regulador:.1f} m",
                hipotesis=hipotesis_grafica
            )
            st.plotly_chart(fig, use_container_width=True)

            # Verificación
            st.markdown("---")
            if fs_resultado >= 2:
                st.success(f"FS = {fs_resultado:.2f} >= 2 (Cumple)")
            else:
                st.error(f"FS = {fs_resultado:.2f} < 2 (No cumple - considere cambiar conductor)")

        except ValueError as e:
            st.error(f"Error en el cálculo: {e}")
        except Exception as e:
            st.error(f"Error inesperado: {e}")

st.markdown("---")
st.info(f"""
**Configuración actual:**
- Conductor: {st.session_state.get('calibre', 'No seleccionado')} (ACSR)
- Sección: {seccion:.2f} mm², E = {conductor.get('modulo_elasticidad_final_kgf_mm2', 0):.1f} kgf/mm²
- Vano regulador: {vano_regulador:.4f} m
""")
