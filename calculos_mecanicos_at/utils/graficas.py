"""
Módulo de funciones de visualización gráfica.

Proporciona funciones para generar gráficos de:
- Curvas de catenaria y parábola
- Comparación de hipótesis
- Perfiles de tensión y temperatura
- Diagramas de distancias de seguridad
"""

import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Optional, Tuple


def graficar_catenaria_matplotlib(
    vano: float,
    flecha: float,
    altura_soporte: float = 20,
    titulo: str = "Perfil del Conductor",
    mostrar_cotas: bool = True,
    distancia_terreno: float = None,
    figsize: Tuple[int, int] = (12, 6)
) -> plt.Figure:
    """
    Genera un gráfico del perfil del conductor usando Matplotlib.

    Args:
        vano: Longitud del vano (m)
        flecha: Flecha máxima (m)
        altura_soporte: Altura de los soportes (m)
        titulo: Título del gráfico
        mostrar_cotas: Si se muestran las cotas
        distancia_terreno: Distancia mínima al terreno (m)
        figsize: Tamaño de la figura

    Returns:
        Figura de Matplotlib
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Generar puntos de la catenaria
    x = np.linspace(-vano/2, vano/2, 100)

    if flecha > 0:
        c = vano**2 / (8 * flecha)
        sag = c * (np.cosh(vano / (2 * c)) - np.cosh(x / c))
        y = altura_soporte - sag
    else:
        y = np.full_like(x, altura_soporte)

    # Graficar conductor
    ax.plot(x, y, 'b-', linewidth=2, label='Conductor')

    # Graficar soportes
    ax.plot([-vano/2, -vano/2], [0, altura_soporte], 'k-', linewidth=3)
    ax.plot([vano/2, vano/2], [0, altura_soporte], 'k-', linewidth=3)

    # Puntos de sujeción
    ax.plot([-vano/2, vano/2], [altura_soporte, altura_soporte], 'ko', markersize=8)

    # Terreno
    ax.axhline(y=0, color='brown', linestyle='-', linewidth=2, label='Terreno')
    ax.fill_between([-vano/2*1.1, vano/2*1.1], [-1, -1], [0, 0],
                    color='brown', alpha=0.3)

    # Mostrar flecha
    if mostrar_cotas and flecha > 0:
        y_min = min(y)
        ax.annotate('', xy=(0, y_min), xytext=(0, altura_soporte),
                   arrowprops=dict(arrowstyle='<->', color='red'))
        ax.text(5, (y_min + altura_soporte)/2, f'Flecha\n{flecha:.2f} m',
               fontsize=10, color='red')

    # Mostrar distancia al terreno
    if distancia_terreno is not None:
        y_min = min(y)
        ax.axhline(y=distancia_terreno, color='green', linestyle='--',
                  label=f'Distancia mín. RETIE: {distancia_terreno:.1f} m')

    # Configurar ejes
    ax.set_xlabel('Distancia horizontal (m)', fontsize=12)
    ax.set_ylabel('Altura (m)', fontsize=12)
    ax.set_title(titulo, fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-vano/2*1.1, vano/2*1.1)
    ax.set_ylim(-1, altura_soporte*1.2)

    plt.tight_layout()
    return fig


def graficar_catenaria_plotly(
    vano: float,
    flecha: float,
    altura_soporte: float = 20,
    titulo: str = "Perfil del Conductor",
    distancia_terreno: float = None,
    hipotesis: List[Dict] = None
) -> go.Figure:
    """
    Genera un gráfico interactivo del perfil del conductor usando Plotly.

    Args:
        vano: Longitud del vano (m)
        flecha: Flecha máxima (m) - usada si hipotesis es None
        altura_soporte: Altura de los soportes (m)
        titulo: Título del gráfico
        distancia_terreno: Distancia mínima al terreno (m)
        hipotesis: Lista de dicts con claves 'nombre', 'flecha', 'color', 'dash'
                   para graficar múltiples curvas

    Returns:
        Figura de Plotly
    """
    fig = go.Figure()

    x = np.linspace(-vano/2, vano/2, 100)

    if hipotesis:
        for hip in hipotesis:
            f = hip['flecha']
            if f > 0:
                c = vano**2 / (8 * f)
                sag = c * (np.cosh(vano / (2 * c)) - np.cosh(x / c))
                y = altura_soporte - sag
            else:
                y = np.full_like(x, altura_soporte)

            fig.add_trace(go.Scatter(
                x=x, y=y,
                mode='lines',
                name=f"{hip['nombre']} (f={f:.2f} m)",
                line=dict(
                    color=hip.get('color', 'blue'),
                    width=hip.get('width', 2),
                    dash=hip.get('dash', 'solid')
                )
            ))
    else:
        if flecha > 0:
            c = vano**2 / (8 * flecha)
            sag = c * (np.cosh(vano / (2 * c)) - np.cosh(x / c))
            y = altura_soporte - sag
        else:
            y = np.full_like(x, altura_soporte)

        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode='lines',
            name='Conductor',
            line=dict(color='blue', width=3)
        ))

    # Soportes
    fig.add_trace(go.Scatter(
        x=[-vano/2, -vano/2, None, vano/2, vano/2],
        y=[0, altura_soporte, None, 0, altura_soporte],
        mode='lines',
        name='Soportes',
        line=dict(color='black', width=4)
    ))

    # Puntos de sujeción
    fig.add_trace(go.Scatter(
        x=[-vano/2, vano/2],
        y=[altura_soporte, altura_soporte],
        mode='markers',
        name='Puntos de sujeción',
        marker=dict(color='black', size=10)
    ))

    # Terreno
    fig.add_trace(go.Scatter(
        x=[-vano/2*1.1, vano/2*1.1],
        y=[0, 0],
        mode='lines',
        name='Terreno',
        line=dict(color='brown', width=3),
        fill='tozeroy',
        fillcolor='rgba(139, 69, 19, 0.2)'
    ))

    # Distancia mínima RETIE
    if distancia_terreno is not None:
        fig.add_hline(
            y=distancia_terreno,
            line_dash="dash",
            line_color="green",
            annotation_text=f"Distancia mín. RETIE: {distancia_terreno:.1f} m"
        )

    fig.update_layout(
        title=dict(text=titulo, x=0.5, font=dict(size=16)),
        xaxis_title="Distancia horizontal (m)",
        yaxis_title="Altura (m)",
        showlegend=True,
        hovermode='x unified'
    )

    return fig


def graficar_comparacion_hipotesis(
    resultados: Dict,
    tipo: str = "tension"
) -> go.Figure:
    """
    Genera un gráfico de barras comparando las hipótesis.

    Args:
        resultados: Diccionario con resultados de hipótesis
        tipo: "tension" o "flecha"

    Returns:
        Figura de Plotly
    """
    hipotesis = []
    valores = []
    colores = []
    limites = []

    color_map = {
        'A': '#FF6B6B',  # Rojo
        'B': '#4ECDC4',  # Turquesa
        'C': '#45B7D1',  # Azul
        'D': '#96CEB4'   # Verde
    }

    for tipo_hip, resultado in resultados.items():
        hipotesis.append(resultado.nombre)

        if tipo == "tension":
            valores.append(resultado.tension_calculada)
            limites.append(resultado.tension_limite)
        else:
            valores.append(resultado.flecha)
            limites.append(None)

        colores.append(color_map.get(tipo_hip.value, '#888888'))

    fig = go.Figure()

    # Barras de valores
    fig.add_trace(go.Bar(
        x=hipotesis,
        y=valores,
        name='Calculado',
        marker_color=colores,
        text=[f'{v:.2f}' for v in valores],
        textposition='outside'
    ))

    # Líneas de límite (solo para tensión)
    if tipo == "tension" and any(limites):
        fig.add_trace(go.Scatter(
            x=hipotesis,
            y=limites,
            mode='markers+lines',
            name='Límite RETIE',
            marker=dict(color='red', size=10, symbol='diamond'),
            line=dict(color='red', dash='dash')
        ))

    titulo = "Comparación de Tensiones por Hipótesis" if tipo == "tension" else "Comparación de Flechas por Hipótesis"
    y_titulo = "Tensión (kg/mm²)" if tipo == "tension" else "Flecha (m)"

    fig.update_layout(
        title=dict(text=titulo, x=0.5),
        xaxis_title="Hipótesis",
        yaxis_title=y_titulo,
        barmode='group',
        showlegend=True
    )

    return fig


def graficar_tabla_tension_temperatura(
    temperaturas: List[float],
    tensiones: List[float],
    flechas: List[float],
    titulo: str = "Variación de Tensión y Flecha con Temperatura"
) -> go.Figure:
    """
    Genera un gráfico de tensión y flecha vs temperatura.

    Args:
        temperaturas: Lista de temperaturas (°C)
        tensiones: Lista de tensiones (kg/mm²)
        flechas: Lista de flechas (m)
        titulo: Título del gráfico

    Returns:
        Figura de Plotly con dos ejes Y
    """
    fig = go.Figure()

    # Tensión
    fig.add_trace(go.Scatter(
        x=temperaturas,
        y=tensiones,
        mode='lines+markers',
        name='Tensión',
        line=dict(color='blue', width=2),
        marker=dict(size=8)
    ))

    # Flecha (eje secundario)
    fig.add_trace(go.Scatter(
        x=temperaturas,
        y=flechas,
        mode='lines+markers',
        name='Flecha',
        line=dict(color='red', width=2),
        marker=dict(size=8),
        yaxis='y2'
    ))

    fig.update_layout(
        title=dict(text=titulo, x=0.5),
        xaxis_title="Temperatura (°C)",
        yaxis=dict(title="Tensión (kg/mm²)", side='left', color='blue'),
        yaxis2=dict(title="Flecha (m)", side='right', overlaying='y', color='red'),
        legend=dict(x=0.1, y=1.1, orientation='h'),
        hovermode='x unified'
    )

    return fig


def graficar_perfil_canton(
    vanos: List[float],
    flechas: List[float],
    alturas_soporte: List[float],
    titulo: str = "Perfil del Cantón"
) -> go.Figure:
    """
    Genera un gráfico del perfil completo de un cantón.

    Args:
        vanos: Lista de longitudes de vanos (m)
        flechas: Lista de flechas por vano (m)
        alturas_soporte: Lista de alturas de soportes (m)
        titulo: Título del gráfico

    Returns:
        Figura de Plotly
    """
    fig = go.Figure()

    x_acumulado = 0
    todos_x = []
    todos_y = []

    for i, (vano, flecha, altura) in enumerate(zip(vanos, flechas, alturas_soporte[:-1])):
        altura_siguiente = alturas_soporte[i + 1] if i + 1 < len(alturas_soporte) else altura

        # Puntos del vano
        x_local = np.linspace(0, vano, 50)

        if flecha > 0:
            c = vano**2 / (8 * flecha)
            # Ajustar para desnivel
            y_cat = c * (np.cosh((x_local - vano/2) / c) - np.cosh(0))
            y_local = altura - y_cat + (altura_siguiente - altura) * x_local / vano
        else:
            y_local = np.linspace(altura, altura_siguiente, 50)

        todos_x.extend(x_acumulado + x_local)
        todos_y.extend(y_local)

        x_acumulado += vano

    # Conductor
    fig.add_trace(go.Scatter(
        x=todos_x,
        y=todos_y,
        mode='lines',
        name='Conductor',
        line=dict(color='blue', width=2)
    ))

    # Soportes
    x_soportes = [0]
    for v in vanos:
        x_soportes.append(x_soportes[-1] + v)

    for i, (x_s, h_s) in enumerate(zip(x_soportes, alturas_soporte)):
        fig.add_trace(go.Scatter(
            x=[x_s, x_s],
            y=[0, h_s],
            mode='lines',
            name=f'Soporte {i+1}' if i == 0 else None,
            showlegend=(i == 0),
            line=dict(color='black', width=3)
        ))

    # Terreno
    fig.add_trace(go.Scatter(
        x=[0, x_soportes[-1]],
        y=[0, 0],
        mode='lines',
        name='Terreno',
        line=dict(color='brown', width=2),
        fill='tozeroy',
        fillcolor='rgba(139, 69, 19, 0.2)'
    ))

    fig.update_layout(
        title=dict(text=titulo, x=0.5),
        xaxis_title="Distancia (m)",
        yaxis_title="Altura (m)",
        showlegend=True
    )

    return fig


def graficar_ampacity(
    resultados_ampacity: List[Dict],
    titulo: str = "Capacidad Térmica del Conductor"
) -> go.Figure:
    """
    Genera un gráfico de ampacity vs condiciones.

    Args:
        resultados_ampacity: Lista de resultados de cálculo de ampacity
        titulo: Título del gráfico

    Returns:
        Figura de Plotly
    """
    # Agrupar por temperatura ambiente
    temps_amb = sorted(set(r['T_ambiente'] for r in resultados_ampacity))

    fig = go.Figure()

    for t_amb in temps_amb:
        datos = [r for r in resultados_ampacity if r['T_ambiente'] == t_amb]
        temps_cond = [r['T_conductor'] for r in datos]
        ampacity = [r['ampacity'] for r in datos]

        fig.add_trace(go.Scatter(
            x=temps_cond,
            y=ampacity,
            mode='lines+markers',
            name=f'T_amb = {t_amb}°C'
        ))

    fig.update_layout(
        title=dict(text=titulo, x=0.5),
        xaxis_title="Temperatura del conductor (°C)",
        yaxis_title="Ampacity (A)",
        showlegend=True
    )

    return fig


def crear_indicador_cumplimiento(cumple: bool, valor: float, limite: float, titulo: str) -> go.Figure:
    """
    Crea un indicador visual de cumplimiento.

    Args:
        cumple: Si cumple o no el criterio
        valor: Valor actual
        limite: Valor límite
        titulo: Título del indicador

    Returns:
        Figura de Plotly con indicador tipo gauge
    """
    color = "green" if cumple else "red"
    porcentaje = (valor / limite) * 100 if limite > 0 else 0

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=porcentaje,
        title={'text': titulo},
        delta={'reference': 100, 'relative': False},
        gauge={
            'axis': {'range': [0, 150], 'ticksuffix': '%'},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 80], 'color': "lightgreen"},
                {'range': [80, 100], 'color': "yellow"},
                {'range': [100, 150], 'color': "lightcoral"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))

    fig.update_layout(height=250)

    return fig
