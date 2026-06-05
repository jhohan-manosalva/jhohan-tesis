"""
Módulo de cálculo de vano regulador y vano crítico.

El vano regulador es un vano ficticio que representa el comportamiento
mecánico de un cantón completo (conjunto de vanos entre estructuras de anclaje).

El vano crítico determina qué hipótesis de cálculo gobierna el diseño.

Referencias:
    - RETIE Resolución 40117 de 2024
    - IEC 60826:2017
    - IEEE Std 524-2016
"""

import numpy as np
from typing import List, Optional


def calcular_vano_regulador(vanos: List[float]) -> float:
    """
    Calcula el vano regulador (Ruling Span) de un cantón.

    El vano regulador es un vano ficticio equivalente que representa
    el comportamiento mecánico de todo el cantón. Se utiliza para
    calcular tensiones y flechas uniformes en el cantón.

    Fórmula: Lr = √(Σ(Li³) / Σ(Li))

    Args:
        vanos: Lista de longitudes de vanos individuales del cantón (m)

    Returns:
        Vano regulador en metros

    Raises:
        ValueError: Si la lista está vacía o contiene valores no positivos

    Example:
        >>> vanos = [280, 320, 300, 290, 310]
        >>> Lr = calcular_vano_regulador(vanos)
        >>> print(f"Vano regulador: {Lr:.2f} m")
    """
    if not vanos:
        raise ValueError("La lista de vanos no puede estar vacía")

    if any(v <= 0 for v in vanos):
        raise ValueError("Todos los vanos deben ser positivos")

    # Suma de vanos al cubo
    suma_cubos = sum(v**3 for v in vanos)

    # Suma de vanos
    suma_vanos = sum(vanos)

    # Vano regulador
    vano_regulador = np.sqrt(suma_cubos / suma_vanos)

    return vano_regulador


def calcular_vano_regulador_ponderado(
    vanos: List[float],
    desniveles: Optional[List[float]] = None
) -> dict:
    """
    Calcula el vano regulador considerando desniveles entre estructuras.

    Para vanos con desniveles significativos, se puede aplicar una
    corrección al cálculo del vano regulador.

    Args:
        vanos: Lista de longitudes de vanos (m)
        desniveles: Lista de desniveles entre estructuras (m), opcional

    Returns:
        dict con:
        - vano_regulador: Vano regulador básico
        - vano_regulador_corregido: Vano regulador con corrección
        - vanos_equivalentes: Vanos horizontales equivalentes
    """
    vano_regulador_basico = calcular_vano_regulador(vanos)

    if desniveles is None or len(desniveles) != len(vanos):
        return {
            'vano_regulador': vano_regulador_basico,
            'vano_regulador_corregido': vano_regulador_basico,
            'vanos_equivalentes': vanos,
            'usa_correccion': False
        }

    # Calcular vanos equivalentes considerando desnivel
    # Vano inclinado real: L_inclinado = √(L_horizontal² + h²)
    vanos_equivalentes = [
        np.sqrt(v**2 + h**2) for v, h in zip(vanos, desniveles)
    ]

    vano_regulador_corregido = calcular_vano_regulador(vanos_equivalentes)

    return {
        'vano_regulador': vano_regulador_basico,
        'vano_regulador_corregido': vano_regulador_corregido,
        'vanos_equivalentes': vanos_equivalentes,
        'usa_correccion': True,
        'desniveles': desniveles
    }


def calcular_vano_critico(
    E: float = None,
    S: float = None,
    alpha: float = None,
    delta_T: float = None,
    g_1: float = None,
    g_2: float = None,
    sigma_adm: float = None,
    # Parámetros del ejemplo de clase
    tmax: float = None,
    W: float = None,
    theta_A: float = None,
    theta_B: float = None,
    mA: float = None,
    mB: float = None,
) -> float:
    """
    Calcula el vano crítico entre dos hipótesis de cálculo.

    Fórmula del ejemplo de clase:
        ac = (tmax / W) × √(24 × α × (θA - θB) / (mA² - mB²))

    Fórmula alternativa clásica:
        ac = √[(24 × E × S × α × ΔT) / ((g₂² - g₁²) × σ_adm)]

    Args:
        # Fórmula del ejemplo:
        tmax: Tensión máxima admisible (kg/mm²)
        W: Peso del conductor (kg/m)
        alpha: Coeficiente de dilatación térmica (1/°C)
        theta_A: Temperatura hipótesis A (°C)
        theta_B: Temperatura hipótesis B (°C)
        mA: Factor de carga hipótesis A
        mB: Factor de carga hipótesis B

        # Fórmula clásica:
        E: Módulo de elasticidad (kg/mm²)
        S: Sección del conductor (mm²)
        delta_T: Diferencia de temperatura (°C)
        g_1, g_2: Cargas específicas (kg/m/mm²)
        sigma_adm: Tensión admisible (kg/mm²)

    Returns:
        Vano crítico en metros, o float('inf') si no aplica
    """
    # Fórmula del ejemplo de clase
    if tmax is not None and W is not None and mA is not None and mB is not None:
        if alpha is None or alpha <= 0:
            raise ValueError("El coeficiente de dilatación debe ser positivo")
        if W <= 0:
            raise ValueError("El peso del conductor debe ser positivo")

        # Usar theta_A y theta_B si se dan, o delta_T
        if theta_A is not None and theta_B is not None:
            dt = abs(theta_A - theta_B)
        elif delta_T is not None:
            dt = abs(delta_T)
        else:
            raise ValueError("Debe proporcionar theta_A/theta_B o delta_T")

        diff_m2 = mA**2 - mB**2
        if abs(diff_m2) < 1e-12:
            return float('inf')
        if diff_m2 < 0:
            diff_m2 = abs(diff_m2)

        ac = (tmax / W) * np.sqrt(24 * alpha * dt / diff_m2)
        return ac

    # Fórmula clásica (fallback)
    if E is None or S is None or alpha is None or sigma_adm is None:
        raise ValueError("Parámetros insuficientes para calcular vano crítico")

    if E <= 0 or S <= 0 or alpha <= 0 or sigma_adm <= 0:
        raise ValueError("Los parámetros E, S, α y σ_adm deben ser positivos")

    if g_1 is None or g_2 is None or g_1 <= 0 or g_2 <= 0:
        raise ValueError("Las cargas específicas deben ser positivas")

    if delta_T is None:
        raise ValueError("Debe proporcionar delta_T")

    diff_g2 = g_2**2 - g_1**2

    if abs(diff_g2) < 1e-12:
        return float('inf')

    if diff_g2 < 0:
        diff_g2 = abs(diff_g2)

    numerador = 24 * E * S * alpha * abs(delta_T)
    denominador = diff_g2 * sigma_adm
    vano_critico = np.sqrt(numerador / denominador)

    return vano_critico


def verificar_canton(
    vanos: List[float],
    vano_regulador: Optional[float] = None
) -> dict:
    """
    Verifica que la configuración del cantón sea válida.

    Regla principal: vano_max ≤ 2.5 × vano_regulador
    Esta regla asegura que el comportamiento mecánico del cantón
    sea uniforme y predecible.

    Args:
        vanos: Lista de longitudes de vanos (m)
        vano_regulador: Vano regulador calculado (m), si None se calcula

    Returns:
        dict con:
        - valido: Si el cantón cumple las reglas
        - vano_regulador: Vano regulador
        - vano_maximo: Vano máximo del cantón
        - vano_minimo: Vano mínimo del cantón
        - vano_medio: Vano promedio
        - relacion_max_regulador: vano_max / vano_regulador
        - limite_relacion: 2.5
        - advertencias: Lista de advertencias
        - recomendaciones: Sugerencias si no es válido

    Example:
        >>> vanos = [280, 320, 300, 290, 450]
        >>> resultado = verificar_canton(vanos)
        >>> print(f"Válido: {resultado['valido']}")
    """
    if not vanos:
        raise ValueError("La lista de vanos no puede estar vacía")

    if any(v <= 0 for v in vanos):
        raise ValueError("Todos los vanos deben ser positivos")

    # Calcular vano regulador si no se proporciona
    if vano_regulador is None:
        vano_regulador = calcular_vano_regulador(vanos)

    # Estadísticas del cantón
    vano_max = max(vanos)
    vano_min = min(vanos)
    vano_medio = np.mean(vanos)
    vano_std = np.std(vanos)
    num_vanos = len(vanos)

    # Relación vano máximo / vano regulador
    relacion = vano_max / vano_regulador

    # Límite de relación
    limite = 2.5

    # Verificar validez
    valido = relacion <= limite

    # Generar advertencias
    advertencias = []
    recomendaciones = []

    if not valido:
        advertencias.append(
            f"El vano máximo ({vano_max:.1f} m) excede 2.5 veces el vano regulador "
            f"({vano_regulador:.1f} m). Relación: {relacion:.2f}"
        )
        recomendaciones.append(
            f"Considere dividir el cantón o reducir el vano máximo a un máximo de "
            f"{2.5 * vano_regulador:.1f} m"
        )

    # Advertencia si hay mucha variación entre vanos
    if vano_std / vano_medio > 0.3:
        advertencias.append(
            f"Alta variabilidad entre vanos (CV = {100*vano_std/vano_medio:.1f}%). "
            "Considere redistribuir las estructuras."
        )

    # Advertencia si vano mínimo es muy pequeño respecto al máximo
    if vano_max / vano_min > 3:
        advertencias.append(
            f"Gran diferencia entre vano mínimo ({vano_min:.1f} m) y máximo "
            f"({vano_max:.1f} m). Relación: {vano_max/vano_min:.1f}"
        )

    return {
        'valido': valido,
        'vano_regulador': vano_regulador,
        'vano_maximo': vano_max,
        'vano_minimo': vano_min,
        'vano_medio': vano_medio,
        'desviacion_estandar': vano_std,
        'numero_vanos': num_vanos,
        'longitud_total': sum(vanos),
        # Backward-compat: algunas partes del código/tests esperan 'relacion'
        'relacion': relacion,
        'relacion_max_regulador': relacion,
        'limite_relacion': limite,
        'advertencias': advertencias,
        'recomendaciones': recomendaciones,
        'vanos': vanos
    }


def calcular_flecha_por_vano(
    vanos: List[float],
    vano_regulador: float,
    flecha_regulador: float
) -> List[dict]:
    """
    Calcula la flecha para cada vano del cantón.

    La flecha de cada vano se calcula a partir de la flecha del
    vano regulador, asumiendo tensión constante en todo el cantón.

    Fórmula: fi = f_r × (Li / Lr)²

    Args:
        vanos: Lista de longitudes de vanos (m)
        vano_regulador: Vano regulador (m)
        flecha_regulador: Flecha del vano regulador (m)

    Returns:
        Lista de diccionarios con información de cada vano
    """
    if not vanos:
        raise ValueError("La lista de vanos no puede estar vacía")

    resultados = []

    for i, vano in enumerate(vanos):
        # Flecha proporcional al cuadrado del vano
        flecha = flecha_regulador * (vano / vano_regulador)**2

        resultados.append({
            'numero_vano': i + 1,
            'longitud': vano,
            'flecha': flecha,
            'relacion_vano_regulador': vano / vano_regulador,
            'relacion_flecha_regulador': flecha / flecha_regulador
        })

    return resultados


def optimizar_distribucion_vanos(
    longitud_total: float,
    numero_vanos: int,
    vano_minimo: float = 200,
    vano_maximo: float = 400
) -> dict:
    """
    Sugiere una distribución óptima de vanos para un cantón.

    Busca minimizar la variación entre vanos manteniendo un vano
    regulador cercano al vano medio.

    Args:
        longitud_total: Longitud total del cantón (m)
        numero_vanos: Número de vanos deseado
        vano_minimo: Longitud mínima permitida por vano (m)
        vano_maximo: Longitud máxima permitida por vano (m)

    Returns:
        dict con distribución sugerida
    """
    if longitud_total <= 0:
        raise ValueError("La longitud total debe ser positiva")
    if numero_vanos <= 0:
        raise ValueError("El número de vanos debe ser positivo")

    # Vano ideal (uniforme)
    vano_ideal = longitud_total / numero_vanos

    # Verificar si es factible
    if vano_ideal < vano_minimo:
        numero_sugerido = int(longitud_total / vano_minimo)
        return {
            'factible': False,
            'razon': f"El vano ideal ({vano_ideal:.1f} m) es menor que el mínimo permitido ({vano_minimo} m)",
            'numero_vanos_sugerido': numero_sugerido,
            'vano_ideal': vano_ideal
        }

    if vano_ideal > vano_maximo:
        numero_sugerido = int(np.ceil(longitud_total / vano_maximo))
        return {
            'factible': False,
            'razon': f"El vano ideal ({vano_ideal:.1f} m) es mayor que el máximo permitido ({vano_maximo} m)",
            'numero_vanos_sugerido': numero_sugerido,
            'vano_ideal': vano_ideal
        }

    # Distribución uniforme
    vanos_uniformes = [vano_ideal] * numero_vanos

    # Calcular vano regulador
    vano_regulador = calcular_vano_regulador(vanos_uniformes)

    return {
        'factible': True,
        'vanos': vanos_uniformes,
        'vano_regulador': vano_regulador,
        'vano_medio': vano_ideal,
        'longitud_total': sum(vanos_uniformes),
        'numero_vanos': numero_vanos,
        'variacion': 0,
        'relacion_max_regulador': 1.0
    }


def analizar_hipotesis_criticas(
    vano_regulador: float,
    conductor: dict,
    condiciones_hip_A: dict,
    condiciones_hip_B: dict
) -> dict:
    """
    Analiza qué hipótesis es crítica para el vano regulador dado.

    Args:
        vano_regulador: Vano regulador del cantón (m)
        conductor: Propiedades del conductor
        condiciones_hip_A: Condiciones de hipótesis A (viento máximo)
        condiciones_hip_B: Condiciones de hipótesis B (temperatura mínima)

    Returns:
        dict con análisis de hipótesis críticas
    """
    E = conductor.get('modulo_elasticidad_final_kgf_mm2', 7700)
    S = conductor.get('seccion_total_mm2', 100)
    alpha = conductor.get('coef_dilatacion_1_C', 0.0000193)
    carga_rotura = conductor.get('carga_rotura_kgf', 10000)

    # Tensiones admisibles
    sigma_adm_A = (carga_rotura / S) * 0.50  # 50% para viento máximo
    sigma_adm_B = (carga_rotura / S) * 0.35  # 35% para temperatura mínima

    # Cargas específicas
    g_A = condiciones_hip_A.get('carga_especifica', 0)
    g_B = condiciones_hip_B.get('carga_especifica', 0)

    # Temperaturas
    t_A = condiciones_hip_A.get('temperatura', 15)
    t_B = condiciones_hip_B.get('temperatura', 5)

    delta_T = abs(t_A - t_B)

    # Calcular vano crítico
    try:
        vano_critico = calcular_vano_critico(
            E, S, alpha, delta_T, g_B, g_A, min(sigma_adm_A, sigma_adm_B)
        )
    except (ValueError, ZeroDivisionError):
        vano_critico = float('inf')

    # Determinar hipótesis crítica
    if vano_regulador < vano_critico:
        hipotesis_critica = "B"
        descripcion = "Temperatura mínima gobierna el diseño"
    else:
        hipotesis_critica = "A"
        descripcion = "Viento máximo gobierna el diseño"

    return {
        'vano_regulador': vano_regulador,
        'vano_critico': vano_critico,
        'hipotesis_critica': hipotesis_critica,
        'descripcion': descripcion,
        'tension_admisible_A': sigma_adm_A,
        'tension_admisible_B': sigma_adm_B,
        'carga_especifica_A': g_A,
        'carga_especifica_B': g_B,
        'delta_temperatura': delta_T
    }
