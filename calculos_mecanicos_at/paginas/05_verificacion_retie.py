"""
Página de verificación de distancias de seguridad según RETIE.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.distancias_seguridad import (
    obtener_distancia_minima, verificar_distancia_seguridad,
    calcular_altura_minima_soporte, obtener_tabla_distancias,
    calcular_factor_altitud, listar_niveles_tension, DISTANCIAS_RETIE
)
from utils.estilos import encabezado_pagina


# Título
encabezado_pagina(
    "🛡️",
    "Verificación de Distancias de Seguridad RETIE",
    "Verifique el cumplimiento de las distancias mínimas de seguridad según la "
    "Tabla 13.2 del RETIE (Resolución 40117 de 2024). Las distancias dependen del "
    "nivel de tensión, tipo de cruce y altitud sobre el nivel del mar."
)

# Configuración
st.subheader("⚙️ Configuración de Verificación")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### Nivel de Tensión")

    niveles = listar_niveles_tension()
    nivel_tension = st.selectbox(
        "Nivel de tensión de la línea (kV)",
        options=niveles,
        index=2,  # 115 kV por defecto
        help="Seleccione el nivel de tensión nominal de la línea"
    )

with col2:
    st.markdown("#### Altitud")

    altitud = st.number_input(
        "Altitud sobre el nivel del mar (msnm)",
        value=st.session_state.get('condiciones_ambientales', {}).get('altitud_msnm', 1000),
        min_value=0,
        max_value=5000,
        step=100
    )

    # Mostrar factor de corrección
    factor = calcular_factor_altitud(altitud, nivel_tension)

    if factor > 1:
        st.warning(f"⚠️ Factor de corrección por altitud: **{factor:.3f}**")
    else:
        st.success("✓ No requiere corrección por altitud")

with col3:
    st.markdown("#### Flecha Máxima")

    # Usar flecha de hipótesis D si está disponible
    flecha_default = 8.0
    if 'resultados_hipotesis' in st.session_state:
        from modules.hipotesis_calculo import TipoHipotesis
        hip_d = st.session_state['resultados_hipotesis'].get(TipoHipotesis.FLECHA_MAXIMA)
        if hip_d:
            flecha_default = hip_d.flecha

    flecha_maxima = st.number_input(
        "Flecha máxima del conductor (m)",
        value=flecha_default,
        min_value=0.1,
        max_value=50.0,
        step=0.1,
        help="Use la flecha de la Hipótesis D (temperatura máxima)"
    )

st.markdown("---")

# Tabla de distancias RETIE
st.subheader("📋 Tabla de Distancias Mínimas RETIE")

# Obtener tabla completa para el nivel de tensión
tabla_distancias = obtener_tabla_distancias(nivel_tension, altitud)

# Crear DataFrame para mostrar
tipos_cruce = {
    'terreno_transitable': 'Terreno transitable',
    'terreno_no_transitable': 'Terreno no transitable',
    'edificaciones': 'Edificaciones',
    'carreteras': 'Carreteras y calles',
    'ferrocarriles': 'Ferrocarriles',
    'lineas_bt': 'Líneas de baja tensión',
    'lineas_comunicaciones': 'Líneas de comunicaciones',
    'aguas_navegables': 'Aguas navegables',
    'aguas_no_navegables': 'Aguas no navegables'
}

datos_tabla = []
for tipo_key, tipo_nombre in tipos_cruce.items():
    dist_info = tabla_distancias['distancias'].get(tipo_key, {})
    datos_tabla.append({
        'Tipo de Cruce': tipo_nombre,
        'Distancia Base (m)': f"{dist_info.get('distancia_base', 0):.2f}",
        'Factor Altitud': f"{dist_info.get('factor_altitud', 1):.3f}",
        'Distancia Corregida (m)': f"{dist_info.get('distancia_corregida', 0):.2f}"
    })

df_distancias = pd.DataFrame(datos_tabla)
st.dataframe(df_distancias, width='stretch', hide_index=True)

st.info(f"""
**Nivel de tensión:** {nivel_tension} kV |
**Altitud:** {altitud:,} msnm |
**Factor de corrección:** {factor:.3f}
""")

st.markdown("---")

# Verificación de distancias
st.subheader("🔍 Verificación de Distancias")

col_ver1, col_ver2 = st.columns([1, 1])

with col_ver1:
    st.markdown("#### Parámetros de Verificación")

    tipo_cruce = st.selectbox(
        "Tipo de cruce a verificar",
        options=list(tipos_cruce.keys()),
        format_func=lambda x: tipos_cruce[x]
    )

    altura_soporte = st.number_input(
        "Altura del punto de sujeción (m)",
        value=20.0,
        min_value=5.0,
        max_value=100.0,
        step=1.0,
        help="Altura desde el terreno hasta el punto de sujeción del conductor"
    )

    altura_obstaculo = st.number_input(
        "Altura del obstáculo (m)",
        value=0.0,
        min_value=0.0,
        max_value=50.0,
        step=0.5,
        help="Altura del punto más alto del obstáculo sobre el terreno"
    )

with col_ver2:
    st.markdown("#### Resultado de Verificación")

    if st.button("🔄 Verificar", type="primary", width='stretch'):

        resultado = verificar_distancia_seguridad(
            flecha_maxima=flecha_maxima,
            altura_soporte=altura_soporte,
            altura_punto_critico=altura_obstaculo,
            nivel_tension_kv=nivel_tension,
            tipo_cruce=tipo_cruce,
            altitud_msnm=altitud
        )

        # Guardar resultado
        st.session_state['verificacion_distancia'] = resultado

        # Mostrar resultado
        if resultado['cumple']:
            st.success(f"""
            ### ✅ CUMPLE RETIE

            **Distancia disponible:** {resultado['distancia_disponible']:.2f} m
            **Distancia requerida:** {resultado['distancia_requerida']:.2f} m
            **Margen:** {resultado['margen']:.2f} m ({resultado['margen_porcentual']:.1f}%)
            """)
        else:
            st.error(f"""
            ### ❌ NO CUMPLE RETIE

            **Distancia disponible:** {resultado['distancia_disponible']:.2f} m
            **Distancia requerida:** {resultado['distancia_requerida']:.2f} m
            **Déficit:** {abs(resultado['margen']):.2f} m
            """)

        # Mostrar observaciones
        for obs in resultado['observaciones']:
            if 'INCUMPLIMIENTO' in obs:
                st.error(obs)
            elif 'Advertencia' in obs:
                st.warning(obs)
            else:
                st.info(obs)

        # Diagrama visual
        st.markdown("---")
        st.markdown("#### Diagrama de Verificación")

        import plotly.graph_objects as go

        fig = go.Figure()

        # Soporte
        fig.add_trace(go.Scatter(
            x=[0, 0],
            y=[0, altura_soporte],
            mode='lines',
            name='Soporte',
            line=dict(color='black', width=5)
        ))

        # Punto de sujeción
        fig.add_trace(go.Scatter(
            x=[0],
            y=[altura_soporte],
            mode='markers',
            name='Punto de sujeción',
            marker=dict(color='black', size=15)
        ))

        # Conductor (línea punteada indicando flecha)
        fig.add_trace(go.Scatter(
            x=[0, 2],
            y=[altura_soporte, altura_soporte - flecha_maxima],
            mode='lines',
            name='Conductor (flecha máx.)',
            line=dict(color='blue', width=3, dash='dash')
        ))

        # Punto más bajo del conductor
        fig.add_trace(go.Scatter(
            x=[2],
            y=[altura_soporte - flecha_maxima],
            mode='markers',
            name='Punto más bajo',
            marker=dict(color='blue', size=12)
        ))

        # Terreno/obstáculo
        fig.add_trace(go.Scatter(
            x=[-1, 3],
            y=[altura_obstaculo, altura_obstaculo],
            mode='lines',
            name=f'Obstáculo ({altura_obstaculo} m)',
            line=dict(color='brown', width=3)
        ))

        # Línea de distancia mínima requerida
        linea_minima = altura_obstaculo + resultado['distancia_requerida']
        fig.add_trace(go.Scatter(
            x=[-1, 3],
            y=[linea_minima, linea_minima],
            mode='lines',
            name=f'Distancia mín. RETIE ({resultado["distancia_requerida"]:.2f} m)',
            line=dict(color='red', width=2, dash='dot')
        ))

        # Anotaciones
        fig.add_annotation(
            x=1, y=altura_soporte - flecha_maxima/2,
            text=f"Flecha: {flecha_maxima:.2f} m",
            showarrow=True, arrowhead=2
        )

        fig.add_annotation(
            x=2.5, y=(altura_soporte - flecha_maxima + altura_obstaculo)/2,
            text=f"Disponible: {resultado['distancia_disponible']:.2f} m",
            showarrow=True, arrowhead=2,
            arrowcolor='green' if resultado['cumple'] else 'red'
        )

        fig.update_layout(
            title="Diagrama de Distancias de Seguridad",
            xaxis_title="",
            yaxis_title="Altura (m)",
            showlegend=True,
            height=500
        )

        st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Cálculo de altura mínima de soporte
st.subheader("📐 Cálculo de Altura Mínima de Soporte")

col_calc1, col_calc2 = st.columns(2)

with col_calc1:
    tipo_cruce_calc = st.selectbox(
        "Tipo de cruce",
        options=list(tipos_cruce.keys()),
        format_func=lambda x: tipos_cruce[x],
        key="tipo_cruce_calc"
    )

    altura_obs_calc = st.number_input(
        "Altura del obstáculo (m)",
        value=0.0,
        min_value=0.0,
        max_value=50.0,
        key="altura_obs_calc"
    )

    margen_adicional = st.number_input(
        "Margen de seguridad adicional (m)",
        value=0.5,
        min_value=0.0,
        max_value=5.0,
        step=0.1
    )

with col_calc2:
    altura_minima = calcular_altura_minima_soporte(
        flecha_maxima=flecha_maxima,
        altura_punto_critico=altura_obs_calc,
        nivel_tension_kv=nivel_tension,
        tipo_cruce=tipo_cruce_calc,
        altitud_msnm=altitud,
        margen_seguridad=margen_adicional
    )

    st.metric(
        "Altura mínima de soporte requerida",
        f"{altura_minima:.2f} m"
    )

    st.info(f"""
    **Desglose del cálculo:**
    - Flecha máxima: {flecha_maxima:.2f} m
    - Altura obstáculo: {altura_obs_calc:.2f} m
    - Distancia RETIE: {obtener_distancia_minima(nivel_tension, tipo_cruce_calc, altitud):.2f} m
    - Margen adicional: {margen_adicional:.2f} m
    - **Total:** {altura_minima:.2f} m
    """)

st.markdown("---")

# Resumen de verificaciones múltiples
st.subheader("📊 Verificación de Múltiples Cruces")

st.markdown("Ingrese los diferentes cruces a verificar en el vano:")

num_cruces = st.number_input("Número de cruces", min_value=1, max_value=5, value=1)

cruces = []
cols = st.columns(min(num_cruces, 3))

for i in range(num_cruces):
    with cols[i % 3]:
        st.markdown(f"**Cruce {i+1}**")
        tipo = st.selectbox(
            f"Tipo",
            options=list(tipos_cruce.keys()),
            format_func=lambda x: tipos_cruce[x],
            key=f"tipo_cruce_{i}"
        )
        altura = st.number_input(
            f"Altura obstáculo (m)",
            value=0.0,
            min_value=0.0,
            max_value=50.0,
            key=f"altura_obs_{i}"
        )
        cruces.append({'tipo': tipo, 'altura': altura})

if st.button("📋 Verificar Todos los Cruces"):
    resultados_cruces = []

    for i, cruce in enumerate(cruces):
        res = verificar_distancia_seguridad(
            flecha_maxima=flecha_maxima,
            altura_soporte=altura_soporte,
            altura_punto_critico=cruce['altura'],
            nivel_tension_kv=nivel_tension,
            tipo_cruce=cruce['tipo'],
            altitud_msnm=altitud
        )
        res['nombre_cruce'] = tipos_cruce[cruce['tipo']]
        resultados_cruces.append(res)

    # Guardar resultados
    st.session_state['verificaciones_distancia'] = resultados_cruces

    # Mostrar tabla de resultados
    datos_resultados = []
    for res in resultados_cruces:
        datos_resultados.append({
            'Tipo de Cruce': res['nombre_cruce'],
            'Disponible (m)': f"{res['distancia_disponible']:.2f}",
            'Requerida (m)': f"{res['distancia_requerida']:.2f}",
            'Margen (m)': f"{res['margen']:.2f}",
            'Cumple': '✅' if res['cumple'] else '❌'
        })

    df_resultados = pd.DataFrame(datos_resultados)
    st.dataframe(df_resultados, width='stretch', hide_index=True)

    # Resumen
    todos_cumplen = all(r['cumple'] for r in resultados_cruces)
    if todos_cumplen:
        st.success("✅ Todos los cruces cumplen con las distancias mínimas RETIE")
    else:
        st.error("❌ Algunos cruces NO cumplen con las distancias mínimas RETIE")
