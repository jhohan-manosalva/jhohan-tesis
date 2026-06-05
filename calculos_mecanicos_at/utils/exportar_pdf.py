"""
Módulo de generación de reportes PDF.

Genera reportes profesionales con los resultados de los cálculos mecánicos
usando la librería ReportLab.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
from typing import Dict, List, Optional
import io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def crear_grafica_perfil_hipotesis(
    vano: float,
    resultados_hipotesis: Dict,
    altura_soporte: float = 20
) -> io.BytesIO:
    """
    Genera una imagen PNG del perfil del conductor con todas las hipótesis.

    Returns:
        BytesIO con la imagen PNG
    """
    fig, ax = plt.subplots(figsize=(16, 8))

    x = np.linspace(-vano / 2, vano / 2, 200)

    colores = {
        'A': ('#e74c3c', '-',  'Hip. A - Viento máx.'),
        'B': ('#3498db', '--', 'Hip. B - Temp. mínima'),
        'C': ('#2ecc71', ':',  'Hip. C - EDS'),
        'D': ('#f39c12', '-.', 'Hip. D - Temp. máx. operación'),
    }

    for tipo, resultado in resultados_hipotesis.items():
        hip_key = resultado.tipo.value
        f = resultado.flecha
        color, estilo, nombre = colores.get(hip_key, ('#999999', '-', hip_key))

        if f > 0:
            c = vano ** 2 / (8 * f)
            sag = c * (np.cosh(vano / (2 * c)) - np.cosh(x / c))
            y = altura_soporte - sag
        else:
            y = np.full_like(x, altura_soporte)

        ax.plot(x, y, color=color, linestyle=estilo, linewidth=2,
                label=f"{nombre} (f={f:.2f} m)")

    # Soportes
    ax.plot([-vano / 2, -vano / 2], [0, altura_soporte], 'k-', linewidth=3)
    ax.plot([vano / 2, vano / 2], [0, altura_soporte], 'k-', linewidth=3)
    ax.plot([-vano / 2, vano / 2], [altura_soporte, altura_soporte], 'ko', markersize=8)

    # Terreno
    ax.axhline(y=0, color='brown', linewidth=2)
    ax.fill_between([-vano / 2 * 1.1, vano / 2 * 1.1], -1, 0,
                    color='brown', alpha=0.2)

    ax.set_xlabel('Distancia horizontal (m)', fontsize=12)
    ax.set_ylabel('Altura (m)', fontsize=12)
    ax.set_title(f'Perfil del Conductor - Vano: {vano:.1f} m', fontsize=14, fontweight='bold')
    ax.legend(loc='lower center', fontsize=10, ncol=2)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-vano / 2 * 1.1, vano / 2 * 1.1)
    ax.set_ylim(-1, altura_soporte * 1.2)

    plt.tight_layout()

    img_buffer = io.BytesIO()
    fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    img_buffer.seek(0)

    return img_buffer


def crear_grafica_verificacion_distancias(
    verificaciones: List[Dict],
    altura_soporte: float,
    flecha_maxima: float
) -> io.BytesIO:
    """
    Genera una imagen PNG del diagrama de verificación de distancias.

    Args:
        verificaciones: Lista de dicts con resultados de verificación
        altura_soporte: Altura del punto de sujeción (m)
        flecha_maxima: Flecha máxima del conductor (m)

    Returns:
        BytesIO con la imagen PNG
    """
    fig, ax = plt.subplots(figsize=(14, 8))

    punto_bajo = altura_soporte - flecha_maxima

    # Soporte
    ax.plot([0, 0], [0, altura_soporte], 'k-', linewidth=5)
    ax.plot([0], [altura_soporte], 'ko', markersize=12)

    # Conductor (curva simplificada)
    x_cond = np.linspace(0, 4, 50)
    y_cond = altura_soporte - flecha_maxima * np.sin(np.pi * x_cond / 8)
    ax.plot(x_cond, y_cond, 'b--', linewidth=3, label=f'Conductor (flecha={flecha_maxima:.2f} m)')
    ax.plot([2], [punto_bajo], 'bo', markersize=10)

    # Flecha anotación
    ax.annotate('', xy=(0.5, punto_bajo), xytext=(0.5, altura_soporte),
                arrowprops=dict(arrowstyle='<->', color='blue', lw=1.5))
    ax.text(0.7, (punto_bajo + altura_soporte) / 2, f'Flecha\n{flecha_maxima:.2f} m',
            fontsize=9, color='blue', va='center')

    # Terreno
    ax.axhline(y=0, color='brown', linewidth=2)
    ax.fill_between([-1, 5], -1, 0, color='brown', alpha=0.2)

    # Verificaciones
    colores_cruce = ['#e74c3c', '#f39c12', '#27ae60', '#3498db', '#9b59b6']
    for i, v in enumerate(verificaciones):
        color = colores_cruce[i % len(colores_cruce)]
        alt_obs = v.get('altura_obstaculo', 0)
        dist_req = v['distancia_requerida']
        linea_minima = alt_obs + dist_req

        # Línea del obstáculo
        ax.axhline(y=linea_minima, color=color, linewidth=1.5, linestyle=':',
                    label=f"{v['tipo_cruce']}: {dist_req:.2f} m req.")

        cumple_texto = 'OK' if v['cumple'] else 'NO CUMPLE'
        marcador = 'v' if v['cumple'] else 'x'
        ax.text(4.2, linea_minima, f'{cumple_texto}', fontsize=8, color=color,
                va='center', fontweight='bold')

    # Línea del punto más bajo
    ax.axhline(y=punto_bajo, color='blue', linewidth=1, linestyle='-.',
                alpha=0.5, label=f'Punto más bajo: {punto_bajo:.2f} m')

    ax.set_xlabel('Distancia horizontal (m)', fontsize=11)
    ax.set_ylabel('Altura (m)', fontsize=11)
    ax.set_title('Diagrama de Verificación de Distancias RETIE', fontsize=13, fontweight='bold')
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-1, 5.5)
    ax.set_ylim(-1, altura_soporte * 1.15)

    plt.tight_layout()

    img_buffer = io.BytesIO()
    fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    img_buffer.seek(0)

    return img_buffer


def crear_estilos():
    """Crea los estilos personalizados para el reporte."""
    estilos = getSampleStyleSheet()

    # Título principal
    estilos.add(ParagraphStyle(
        name='TituloPrincipal',
        parent=estilos['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor('#1a5276')
    ))

    # Subtítulo
    estilos.add(ParagraphStyle(
        name='Subtitulo',
        parent=estilos['Heading2'],
        fontSize=14,
        alignment=TA_LEFT,
        spaceAfter=10,
        spaceBefore=15,
        textColor=colors.HexColor('#2874a6')
    ))

    # Texto normal justificado
    estilos.add(ParagraphStyle(
        name='TextoNormal',
        parent=estilos['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=6
    ))

    # Texto pequeño para notas
    estilos.add(ParagraphStyle(
        name='Nota',
        parent=estilos['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_LEFT
    ))

    # Encabezado de tabla
    estilos.add(ParagraphStyle(
        name='EncabezadoTabla',
        parent=estilos['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.white
    ))

    return estilos


def crear_tabla_conductor(conductor: dict, estilos) -> Table:
    """Crea la tabla de propiedades del conductor."""
    datos = [
        ['Propiedad', 'Valor', 'Unidad'],
        ['Código', conductor.get('codigo_bird', 'N/A'), '-'],
        ['Calibre', conductor.get('calibre_awg_kcmil', 'N/A'), '-'],
        ['Sección total', f"{conductor.get('seccion_total_mm2', 0):.2f}", 'mm²'],
        ['Diámetro', f"{conductor.get('diametro_mm', 0):.2f}", 'mm'],
        ['Peso', f"{conductor.get('peso_kg_km', 0):.1f}", 'kg/km'],
        ['Carga de rotura', f"{conductor.get('carga_rotura_kgf', 0):,.0f}", 'kgf'],
        ['Módulo de elasticidad', f"{conductor.get('modulo_elasticidad_final_kgf_mm2', 0):,.0f}", 'kgf/mm²'],
        ['Coef. dilatación', f"{conductor.get('coef_dilatacion_1_C', 0):.2e}", '1/°C'],
    ]

    tabla = Table(datos, colWidths=[5*cm, 4*cm, 2*cm])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2874a6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#eaf2f8')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eaf2f8')])
    ]))

    return tabla


def crear_tabla_zona_climatica(zona: dict, estilos) -> Table:
    """Crea la tabla de condiciones ambientales."""
    datos = [
        ['Parámetro', 'Valor', 'Unidad'],
        ['Zona', zona.get('nombre', 'N/A'), '-'],
        ['Altitud de referencia', f"{zona.get('altitud_referencia_msnm', 0):,.0f}", 'msnm'],
        ['Temperatura mínima', f"{zona.get('temperatura_minima_C', 0):.1f}", '°C'],
        ['Temperatura media', f"{zona.get('temperatura_media_C', 0):.1f}", '°C'],
        ['Temperatura máxima', f"{zona.get('temperatura_maxima_ambiente_C', 0):.1f}", '°C'],
        ['Velocidad viento diseño', f"{zona.get('velocidad_viento_diseno_m_s', 0):.1f}", 'm/s'],
        ['Velocidad viento diseño', f"{zona.get('velocidad_viento_diseno_km_h', 0):.0f}", 'km/h'],
    ]

    tabla = Table(datos, colWidths=[5*cm, 4*cm, 2*cm])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e8449')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f6f3')])
    ]))

    return tabla


def crear_tabla_hipotesis(resultados_hipotesis: Dict, estilos) -> Table:
    """Crea la tabla de resultados de hipótesis."""
    datos = [
        ['Hipótesis', 'Temp.\n(°C)', 'Viento\n(m/s)', 'Tensión\n(kg/mm²)', 'Tensión\n(kg)', 'Límite\n(%)', 'Util.\n(%)', 'Flecha\n(m)', 'Cumple']
    ]

    for tipo, resultado in resultados_hipotesis.items():
        cumple_texto = '✓' if resultado.cumple_limite else '✗'
        datos.append([
            resultado.tipo.value,
            f"{resultado.temperatura:.0f}",
            f"{resultado.velocidad_viento:.1f}",
            f"{resultado.tension_calculada:.3f}",
            f"{resultado.tension_total:.0f}",
            f"{resultado.porcentaje_limite:.0f}",
            f"{resultado.factor_utilizacion*100:.1f}",
            f"{resultado.flecha:.2f}",
            cumple_texto
        ])

    tabla = Table(datos, colWidths=[1.5*cm, 1.5*cm, 1.5*cm, 2*cm, 2*cm, 1.5*cm, 1.5*cm, 1.5*cm, 1.5*cm])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8e44ad')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5eef8')])
    ]))

    return tabla


def crear_tabla_vanos(vanos: List[float], vano_regulador: float, estilos) -> Table:
    """Crea la tabla de vanos del cantón."""
    datos = [['Vano #', 'Longitud (m)']]

    for i, vano in enumerate(vanos):
        datos.append([f"{i+1}", f"{vano:.1f}"])

    datos.append(['Vano regulador', f"{vano_regulador:.2f}"])
    datos.append(['Longitud total', f"{sum(vanos):.1f}"])

    tabla = Table(datos, colWidths=[4*cm, 4*cm])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c0392b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BACKGROUND', (0, -2), (-1, -1), colors.HexColor('#fadbd8')),
        ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
    ]))

    return tabla


def crear_tabla_verificacion_distancias(verificaciones: List[Dict], estilos) -> Table:
    """Crea la tabla de verificación de distancias."""
    datos = [['Tipo de cruce', 'Disponible (m)', 'Requerida (m)', 'Margen (m)', 'Cumple']]

    for v in verificaciones:
        cumple_texto = '✓' if v['cumple'] else '✗'
        datos.append([
            v['tipo_cruce'],
            f"{v['distancia_disponible']:.2f}",
            f"{v['distancia_requerida']:.2f}",
            f"{v['margen']:.2f}",
            cumple_texto
        ])

    tabla = Table(datos, colWidths=[4*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2*cm])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f8f5')])
    ]))

    return tabla


def generar_reporte_pdf(
    datos_proyecto: Dict,
    conductor: Dict,
    zona_climatica: Dict,
    vanos: List[float],
    vano_regulador: float,
    resultados_hipotesis: Dict,
    verificaciones_distancia: List[Dict],
    nivel_tension_kv: float,
    ruta_salida: str = None
) -> bytes:
    """
    Genera el reporte PDF completo.

    Args:
        datos_proyecto: Información del proyecto
        conductor: Propiedades del conductor
        zona_climatica: Condiciones ambientales
        vanos: Lista de vanos
        vano_regulador: Vano regulador calculado
        resultados_hipotesis: Resultados de las 4 hipótesis
        verificaciones_distancia: Verificaciones de distancias
        nivel_tension_kv: Nivel de tensión de la línea
        ruta_salida: Ruta del archivo PDF (opcional)

    Returns:
        Bytes del PDF generado
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    estilos = crear_estilos()
    elementos = []

    # Título
    elementos.append(Paragraph(
        "REPORTE DE CÁLCULOS MECÁNICOS<br/>LÍNEA DE TRANSMISIÓN",
        estilos['TituloPrincipal']
    ))

    # Información del proyecto
    elementos.append(Paragraph("1. INFORMACIÓN DEL PROYECTO", estilos['Subtitulo']))
    info_proyecto = f"""
    <b>Nombre del proyecto:</b> {datos_proyecto.get('nombre', 'N/A')}<br/>
    <b>Nivel de tensión:</b> {nivel_tension_kv} kV<br/>
    <b>Ubicación:</b> {zona_climatica.get('nombre', 'N/A')}<br/>
    <b>Fecha del reporte:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>
    <b>Elaborado por:</b> {datos_proyecto.get('autor', 'N/A')}<br/>
    <b>Institución:</b> {datos_proyecto.get('institucion', 'Unidades Tecnológicas de Santander (UTS) - Programa de Electricidad Industrial')}
    """
    elementos.append(Paragraph(info_proyecto, estilos['TextoNormal']))
    elementos.append(Spacer(1, 0.5*cm))

    # Conductor
    elementos.append(Paragraph("2. CONDUCTOR SELECCIONADO", estilos['Subtitulo']))
    elementos.append(crear_tabla_conductor(conductor, estilos))
    elementos.append(Spacer(1, 0.5*cm))

    # Condiciones ambientales
    elementos.append(Paragraph("3. CONDICIONES AMBIENTALES", estilos['Subtitulo']))
    elementos.append(crear_tabla_zona_climatica(zona_climatica, estilos))
    elementos.append(Spacer(1, 0.5*cm))

    # Vanos
    elementos.append(Paragraph("4. CONFIGURACIÓN DEL CANTÓN", estilos['Subtitulo']))
    elementos.append(crear_tabla_vanos(vanos, vano_regulador, estilos))
    elementos.append(Spacer(1, 0.5*cm))

    # Nueva página para resultados
    elementos.append(PageBreak())

    # Hipótesis
    elementos.append(Paragraph("5. ANÁLISIS DE HIPÓTESIS DE CÁLCULO", estilos['Subtitulo']))
    elementos.append(Paragraph(
        """Las siguientes hipótesis se calcularon según los requisitos del RETIE
        (Resolución 40117 de 2024) y la norma IEC 60826:""",
        estilos['TextoNormal']
    ))
    elementos.append(Spacer(1, 0.3*cm))
    elementos.append(crear_tabla_hipotesis(resultados_hipotesis, estilos))
    elementos.append(Spacer(1, 0.5*cm))

    # Descripción de hipótesis
    descripcion_hip = """
    <b>Hipótesis A - Viento Máximo:</b> Determina cargas máximas sobre estructuras. Límite: 50% carga de rotura.<br/>
    <b>Hipótesis B - Temperatura Mínima:</b> Verifica tensión máxima por contracción térmica. Límite: 35% carga de rotura.<br/>
    <b>Hipótesis C - EDS:</b> Tensión de operación diaria, prevención de fatiga. Típico: 15-18% carga de rotura.<br/>
    <b>Hipótesis D - Flecha Máxima:</b> Verifica distancias de seguridad a temperatura máxima del conductor.
    """
    elementos.append(Paragraph(descripcion_hip, estilos['Nota']))
    elementos.append(Spacer(1, 0.5*cm))

    # Gráfico de perfil del conductor con todas las hipótesis
    try:
        img_buffer = crear_grafica_perfil_hipotesis(
            vano=vano_regulador,
            resultados_hipotesis=resultados_hipotesis,
            altura_soporte=20
        )
        img = Image(img_buffer, width=16*cm, height=8*cm)
        elementos.append(img)
        elementos.append(Spacer(1, 0.3*cm))
        elementos.append(Paragraph(
            "Figura 1: Perfil del conductor para cada hipótesis de cálculo.",
            estilos['Nota']
        ))
        elementos.append(Spacer(1, 0.5*cm))
    except Exception:
        elementos.append(Paragraph(
            "No se pudo generar el gráfico de perfil del conductor.",
            estilos['Nota']
        ))

    # Verificación de distancias
    elementos.append(Paragraph("6. VERIFICACIÓN DE DISTANCIAS DE SEGURIDAD", estilos['Subtitulo']))
    if verificaciones_distancia:
        elementos.append(crear_tabla_verificacion_distancias(verificaciones_distancia, estilos))
        elementos.append(Spacer(1, 0.5*cm))

        # Diagrama de verificación de distancias
        try:
            # Obtener flecha máxima de Hip. D
            flecha_max = max(r.flecha for r in resultados_hipotesis.values())
            img_verif = crear_grafica_verificacion_distancias(
                verificaciones=verificaciones_distancia,
                altura_soporte=20,
                flecha_maxima=flecha_max
            )
            img_v = Image(img_verif, width=16*cm, height=8*cm)
            elementos.append(img_v)
            elementos.append(Spacer(1, 0.3*cm))
            elementos.append(Paragraph(
                "Figura 2: Diagrama de verificación de distancias de seguridad RETIE.",
                estilos['Nota']
            ))
        except Exception:
            elementos.append(Paragraph(
                "No se pudo generar el diagrama de verificación.",
                estilos['Nota']
            ))
    else:
        elementos.append(Paragraph("No se realizaron verificaciones de distancia.", estilos['TextoNormal']))
    elementos.append(Spacer(1, 0.5*cm))

    # Conclusiones
    elementos.append(Paragraph("7. CONCLUSIONES Y RECOMENDACIONES", estilos['Subtitulo']))

    # Determinar si todo cumple
    hipotesis_ok = all(r.cumple_limite for r in resultados_hipotesis.values())
    distancias_ok = all(v.get('cumple', False) for v in verificaciones_distancia) if verificaciones_distancia else True

    if hipotesis_ok and distancias_ok:
        conclusion = """
        <font color="green"><b>✓ DISEÑO CUMPLE CON NORMATIVA RETIE</b></font><br/><br/>
        El análisis mecánico realizado demuestra que el conductor seleccionado cumple con
        todos los requisitos establecidos en el RETIE (Resolución 40117 de 2024) para las
        condiciones de la zona climática especificada.
        """
    else:
        problemas = []
        if not hipotesis_ok:
            problemas.append("- Algunas hipótesis exceden los límites de tensión permitidos")
        if not distancias_ok:
            problemas.append("- Algunas distancias de seguridad no cumplen los mínimos RETIE")

        conclusion = f"""
        <font color="red"><b>✗ DISEÑO REQUIERE AJUSTES</b></font><br/><br/>
        Se han identificado los siguientes problemas:<br/>
        {'<br/>'.join(problemas)}<br/><br/>
        Se recomienda revisar el diseño y realizar los ajustes necesarios antes de proceder.
        """

    elementos.append(Paragraph(conclusion, estilos['TextoNormal']))
    elementos.append(Spacer(1, 1*cm))

    # Pie de página
    elementos.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    elementos.append(Spacer(1, 0.3*cm))
    pie = """
    <font size="8" color="grey">
    Este reporte fue generado automáticamente por el Software de Cálculos Mecánicos para
    Líneas de Alta Tensión - UTS. Los resultados deben ser verificados por un profesional
    calificado antes de su uso en proyectos reales.<br/><br/>
    <b>Referencias normativas:</b> RETIE Res. 40117/2024, IEEE 738-2023, IEC 60826:2017, NTC 2050
    </font>
    """
    elementos.append(Paragraph(pie, estilos['TextoNormal']))

    # Construir PDF
    doc.build(elementos)

    # Obtener bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()

    # Guardar archivo si se especifica ruta
    if ruta_salida:
        with open(ruta_salida, 'wb') as f:
            f.write(pdf_bytes)

    return pdf_bytes
