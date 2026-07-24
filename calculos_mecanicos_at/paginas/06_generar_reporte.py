"""
Página de generación de reporte PDF.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.exportar_pdf import generar_reporte_pdf
from utils.estilos import encabezado_pagina


# Título
encabezado_pagina(
    "📋",
    "Generación de Reporte PDF",
    "Genere un reporte profesional en formato PDF con todos los resultados de los "
    "cálculos mecánicos, análisis de hipótesis y verificaciones de distancias."
)

# Verificar datos necesarios
datos_completos = True
mensajes_faltantes = []

if 'conductor' not in st.session_state:
    datos_completos = False
    mensajes_faltantes.append("❌ Conductor no seleccionado")
else:
    st.success("✅ Conductor seleccionado")

if 'condiciones_ambientales' not in st.session_state:
    datos_completos = False
    mensajes_faltantes.append("❌ Condiciones ambientales no configuradas")
else:
    st.success("✅ Condiciones ambientales configuradas")

if 'vanos' not in st.session_state or 'vano_regulador' not in st.session_state:
    datos_completos = False
    mensajes_faltantes.append("❌ Vanos no configurados")
else:
    st.success("✅ Vanos configurados")

if 'resultados_hipotesis' not in st.session_state:
    datos_completos = False
    mensajes_faltantes.append("❌ Análisis de hipótesis no realizado")
else:
    st.success("✅ Análisis de hipótesis completado")

if mensajes_faltantes:
    for msg in mensajes_faltantes:
        st.warning(msg)

st.markdown("---")

# Información del proyecto
st.subheader("📝 Información del Proyecto")

col1, col2 = st.columns(2)

with col1:
    nombre_proyecto = st.text_input(
        "Nombre del proyecto",
        value="Línea de Transmisión - Estudio Mecánico"
    )

    ubicacion = st.text_input(
        "Ubicación",
        value=st.session_state.get('condiciones_ambientales', {}).get('nombre_zona', 'Colombia')
    )

    nivel_tension = st.selectbox(
        "Nivel de tensión (kV)",
        options=[34.5, 57.5, 115, 230, 500],
        index=2
    )

with col2:
    autor = "Jhohan Felipe Manosalva Sierra"
    institucion = "Unidades Tecnológicas de Santander (UTS) - Programa de Electricidad Industrial"
    st.markdown(f"**Elaborado por:** {autor}")
    st.markdown(f"**Institución:** {institucion}")

    fecha = st.date_input(
        "Fecha del reporte",
        value=datetime.now()
    )

    observaciones = st.text_area(
        "Observaciones adicionales",
        value="",
        height=100
    )

st.markdown("---")

# Resumen de datos para el reporte
st.subheader("📋 Resumen de Datos para el Reporte")

col_res1, col_res2 = st.columns(2)

with col_res1:
    st.markdown("#### Conductor")
    if 'conductor' in st.session_state:
        conductor = st.session_state['conductor']
        st.markdown(f"""
        - **Código:** {conductor.get('codigo_bird', conductor.get('codigo', 'N/A'))}
        - **Sección:** {conductor.get('seccion_total_mm2', 0):.2f} mm²
        - **Carga de rotura:** {conductor.get('carga_rotura_kgf', 0):,} kgf
        """)
    else:
        st.info("No hay conductor seleccionado")

    st.markdown("#### Condiciones Ambientales")
    if 'condiciones_ambientales' in st.session_state:
        cond = st.session_state['condiciones_ambientales']
        st.markdown(f"""
        - **Zona:** {cond.get('nombre_zona', 'N/A')}
        - **Altitud:** {cond.get('altitud_msnm', 0):,} msnm
        - **Viento de diseño:** {cond.get('velocidad_viento_diseno_km_h', 0)} km/h
        """)
    else:
        st.info("No hay condiciones configuradas")

with col_res2:
    st.markdown("#### Vanos")
    if 'vanos' in st.session_state:
        vanos = st.session_state['vanos']
        vano_regulador = st.session_state['vano_regulador']
        st.markdown(f"""
        - **Número de vanos:** {len(vanos)}
        - **Vano regulador:** {vano_regulador:.2f} m
        - **Longitud total:** {sum(vanos):.1f} m
        """)
    else:
        st.info("No hay vanos configurados")

    st.markdown("#### Hipótesis")
    if 'resultados_hipotesis' in st.session_state:
        resultados = st.session_state['resultados_hipotesis']
        todas_cumplen = all(r.cumple_limite for r in resultados.values())
        estado = "✅ Todas cumplen" if todas_cumplen else "⚠️ Revisar"
        st.markdown(f"""
        - **Estado:** {estado}
        - **Hipótesis calculadas:** 4
        """)
    else:
        st.info("No hay hipótesis calculadas")

st.markdown("---")

# Contenido a incluir
st.subheader("📑 Contenido del Reporte")

col_cont1, col_cont2 = st.columns(2)

with col_cont1:
    incluir_conductor = st.checkbox("Datos del conductor", value=True)
    incluir_condiciones = st.checkbox("Condiciones ambientales", value=True)
    incluir_vanos = st.checkbox("Tabla de vanos", value=True)

with col_cont2:
    incluir_hipotesis = st.checkbox("Análisis de hipótesis", value=True)
    incluir_distancias = st.checkbox("Verificación de distancias", value=True)
    incluir_conclusiones = st.checkbox("Conclusiones", value=True)

st.markdown("---")

# Generar reporte
st.subheader("📥 Descargar Reporte")

if st.button("🔄 Generar Reporte PDF", type="primary", width='stretch', disabled=not datos_completos):

    if not datos_completos:
        st.error("❌ Complete todos los pasos previos antes de generar el reporte")
    else:
        with st.spinner("Generando reporte PDF..."):

            try:
                # Preparar datos del proyecto
                datos_proyecto = {
                    'nombre': nombre_proyecto,
                    'ubicacion': ubicacion,
                    'autor': autor,
                    'institucion': institucion,
                    'fecha': fecha.strftime('%d/%m/%Y'),
                    'observaciones': observaciones
                }

                # Obtener datos de session state
                conductor = st.session_state['conductor']
                zona_climatica = st.session_state.get('zona_climatica', st.session_state['condiciones_ambientales'])
                vanos = st.session_state['vanos']
                vano_regulador = st.session_state['vano_regulador']
                resultados_hipotesis = st.session_state['resultados_hipotesis']

                # Verificaciones de distancia (si existen)
                verificaciones = st.session_state.get('verificaciones_distancia', [])

                # Generar PDF
                pdf_bytes = generar_reporte_pdf(
                    datos_proyecto=datos_proyecto,
                    conductor=conductor,
                    zona_climatica=zona_climatica,
                    vanos=vanos,
                    vano_regulador=vano_regulador,
                    resultados_hipotesis=resultados_hipotesis,
                    verificaciones_distancia=verificaciones,
                    nivel_tension_kv=nivel_tension
                )

                st.success("✅ Reporte generado exitosamente")

                # Botón de descarga
                nombre_archivo = f"Reporte_Mecanico_{nombre_proyecto.replace(' ', '_')}_{fecha.strftime('%Y%m%d')}.pdf"

                st.download_button(
                    label="📥 Descargar Reporte PDF",
                    data=pdf_bytes,
                    file_name=nombre_archivo,
                    mime="application/pdf",
                    width='stretch'
                )

                # Mostrar vista previa de información
                st.markdown("---")
                st.markdown("### 📋 Vista Previa del Contenido")

                with st.expander("Ver resumen del reporte", expanded=True):

                    st.markdown(f"""
                    **REPORTE DE CÁLCULOS MECÁNICOS**
                    **LÍNEA DE TRANSMISIÓN**

                    ---

                    **1. INFORMACIÓN DEL PROYECTO**
                    - Nombre: {nombre_proyecto}
                    - Nivel de tensión: {nivel_tension} kV
                    - Ubicación: {ubicacion}
                    - Fecha: {fecha.strftime('%d/%m/%Y')}
                    - Elaborado por: {autor}

                    ---

                    **2. CONDUCTOR SELECCIONADO**
                    - Código: {conductor.get('codigo_bird', conductor.get('codigo', 'N/A'))}
                    - Sección: {conductor.get('seccion_total_mm2', 0):.2f} mm²
                    - Diámetro: {conductor.get('diametro_mm', 0):.2f} mm
                    - Carga de rotura: {conductor.get('carga_rotura_kgf', 0):,} kgf

                    ---

                    **3. RESULTADOS DE HIPÓTESIS**
                    """)

                    # Tabla de hipótesis
                    from modules.hipotesis_calculo import generar_tabla_comparativa
                    tabla = generar_tabla_comparativa(resultados_hipotesis)
                    st.dataframe(pd.DataFrame(tabla), width='stretch', hide_index=True)

                    todas_cumplen = all(r.cumple_limite for r in resultados_hipotesis.values())
                    if todas_cumplen:
                        st.success("✅ DISEÑO CUMPLE CON NORMATIVA RETIE")
                    else:
                        st.error("❌ DISEÑO REQUIERE AJUSTES")

            except Exception as e:
                st.error(f"❌ Error al generar el reporte: {e}")
                import traceback
                st.code(traceback.format_exc())

# Información adicional
st.markdown("---")
st.info("""
**Nota:** El reporte PDF incluirá:
- Encabezado con información del proyecto
- Tablas de propiedades del conductor
- Condiciones ambientales de diseño
- Resultados de las 4 hipótesis RETIE
- Verificación de distancias de seguridad
- Conclusiones y recomendaciones
- Referencias normativas aplicables

El reporte generado es de carácter educativo y debe ser verificado por un
profesional calificado antes de su uso en proyectos reales.
""")
