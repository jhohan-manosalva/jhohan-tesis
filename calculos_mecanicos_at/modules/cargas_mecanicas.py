"""
Módulo de cálculo de cargas mecánicas para conductores eléctricos.

Implementa las fórmulas de cargas mecánicas usadas en el diseño de
líneas de transmisión según la metodología de clase:

- Fuerza de viento: Fv = 0.0042 × V² × d / 1000
- Peso resultante: W' = √(W² + Fv²)
- Factor de carga: m = W'/W = √(1 + (Fv/W)²)
- Carga específica: w = W/S, g = w × m

Referencias:
    - CREG 025/1995 - Código de Redes
    - RETIE Resolución 40117 de 2024
"""

import numpy as np
from typing import Optional


def calcular_densidad_aire(altitud_msnm: float) -> float:
    """
    Calcula la densidad del aire en función de la altitud (modelo ISA).

    Fórmula: ρ = 1.225 × (1 - 2.2558e-5 × h)^4.256

    Args:
        altitud_msnm: Altitud sobre el nivel del mar en metros

    Returns:
        Densidad del aire en kg/m³
    """
    return 1.225 * (1 - 2.2558e-5 * altitud_msnm) ** 4.256


def calcular_fuerza_viento(velocidad_kmh: float, diametro_mm: float) -> float:
    """
    Calcula la fuerza de viento sobre el conductor.

    Fórmula empírica: Fv = 0.0042 × V² × d / 1000

    Args:
        velocidad_kmh: Velocidad del viento en km/h
        diametro_mm: Diámetro del conductor en mm

    Returns:
        Fuerza de viento en kg/m
    """
    if velocidad_kmh < 0:
        raise ValueError("La velocidad del viento no puede ser negativa")
    if diametro_mm <= 0:
        raise ValueError("El diámetro del conductor debe ser positivo")

    return 0.0042 * velocidad_kmh**2 * diametro_mm / 1000


def calcular_factor_carga(peso_conductor_kg_m: float, fuerza_viento_kg_m: float) -> float:
    """
    Calcula el factor de carga (m) del conductor.

    Fórmula: m = √(1 + (Fv/W)²) = W'/W

    donde W' = √(W² + Fv²) es el peso resultante.

    Args:
        peso_conductor_kg_m: Peso propio del conductor en kg/m
        fuerza_viento_kg_m: Fuerza de viento en kg/m

    Returns:
        Factor de carga m (≥ 1)
    """
    if peso_conductor_kg_m <= 0:
        raise ValueError("El peso del conductor debe ser positivo")
    if fuerza_viento_kg_m < 0:
        raise ValueError("La fuerza de viento no puede ser negativa")

    return np.sqrt(1 + (fuerza_viento_kg_m / peso_conductor_kg_m)**2)


def calcular_peso_resultante(
    peso_conductor: float,
    carga_viento: float,
    carga_hielo: float = 0
) -> float:
    """
    Calcula el peso resultante (carga combinada) sobre el conductor.

    Fórmula sin hielo: W' = √(W² + Fv²)
    Fórmula con hielo: W' = √((W + Wh)² + Fv²)

    Args:
        peso_conductor: Peso propio del conductor (kg/m)
        carga_viento: Carga de viento (kg/m)
        carga_hielo: Carga de hielo (kg/m), default 0

    Returns:
        Peso resultante en kg/m
    """
    if peso_conductor < 0:
        raise ValueError("El peso del conductor no puede ser negativo")
    if carga_viento < 0:
        raise ValueError("La carga de viento no puede ser negativa")

    peso_vertical = peso_conductor + carga_hielo
    return np.sqrt(peso_vertical**2 + carga_viento**2)


def calcular_angulo_resultante(
    peso_conductor: float,
    carga_viento: float,
    carga_hielo: float = 0
) -> float:
    """
    Calcula el ángulo de la carga resultante respecto a la vertical.

    Fórmula: i = arctan(Fv / W)

    Args:
        peso_conductor: Peso propio del conductor (kg/m)
        carga_viento: Carga de viento (kg/m)
        carga_hielo: Carga de hielo (kg/m)

    Returns:
        Ángulo en grados respecto a la vertical
    """
    peso_vertical = peso_conductor + carga_hielo

    if peso_vertical == 0:
        return 90.0 if carga_viento > 0 else 0.0

    return np.degrees(np.arctan(carga_viento / peso_vertical))


def calcular_carga_especifica(
    peso_resultante: float,
    seccion_conductor: float
) -> float:
    """
    Calcula la carga específica del conductor.

    Fórmula: g = W' / S  [kg/m/mm²]

    Args:
        peso_resultante: Peso resultante (kg/m)
        seccion_conductor: Sección transversal del conductor (mm²)

    Returns:
        Carga específica en kg/m/mm²
    """
    if peso_resultante < 0:
        raise ValueError("El peso resultante no puede ser negativo")
    if seccion_conductor <= 0:
        raise ValueError("La sección del conductor debe ser positiva")

    return peso_resultante / seccion_conductor


def calcular_cargas_hipotesis(
    conductor: dict,
    velocidad_viento_kmh: float
) -> dict:
    """
    Calcula las cargas mecánicas para una hipótesis de cálculo.

    Usa la fórmula empírica: Fv = 0.0042 × V² × d / 1000
    y calcula el factor de carga m = √(1 + (Fv/W)²).

    Args:
        conductor: Diccionario con propiedades del conductor
        velocidad_viento_kmh: Velocidad del viento en km/h

    Returns:
        dict con:
        - peso_conductor: Peso del conductor (kg/m)
        - fuerza_viento: Fuerza de viento Fv (kg/m)
        - peso_resultante: Peso resultante W' (kg/m)
        - factor_carga: Factor de carga m
        - carga_especifica: Carga específica g = W'/S (kg/m/mm²)
        - carga_especifica_peso: Carga esp. solo peso w = W/S (kg/m/mm²)
        - angulo_resultante: Ángulo respecto a vertical (grados)
    """
    diametro = conductor.get('diametro_mm', 0)
    peso_kg_km = conductor.get('peso_kg_km', 0)
    seccion = conductor.get('seccion_total_mm2', 0)

    peso_conductor = peso_kg_km / 1000  # kg/m

    # Fuerza de viento: Fv = 0.0042 × V² × d / 1000
    fv = calcular_fuerza_viento(velocidad_viento_kmh, diametro)

    # Peso resultante: W' = √(W² + Fv²)
    peso_resultante = calcular_peso_resultante(peso_conductor, fv)

    # Factor de carga: m = W'/W
    if peso_conductor > 0:
        factor_carga = calcular_factor_carga(peso_conductor, fv)
    else:
        factor_carga = 1.0

    # Carga específica: g = W'/S = w × m
    carga_especifica = calcular_carga_especifica(peso_resultante, seccion)

    # Carga específica solo peso propio: w = W/S
    carga_especifica_peso = calcular_carga_especifica(peso_conductor, seccion)

    # Ángulo resultante
    angulo = calcular_angulo_resultante(peso_conductor, fv)

    return {
        'peso_conductor': peso_conductor,
        'fuerza_viento': fv,
        'peso_resultante': peso_resultante,
        'factor_carga': factor_carga,
        'carga_especifica': carga_especifica,
        'carga_especifica_peso': carga_especifica_peso,
        'angulo_resultante_grados': angulo,
        'velocidad_viento_kmh': velocidad_viento_kmh,
        'diametro_conductor': diametro,
        'seccion_conductor': seccion
    }


# Funciones de compatibilidad (usadas por otros módulos)
def calcular_cargas_completas(
    conductor: dict,
    velocidad_viento: float,
    altitud_msnm: float = 0,
    espesor_hielo: float = 0,
    coef_arrastre: float = 1.0
) -> dict:
    """
    Calcula todas las cargas mecánicas para un conductor.
    Convierte velocidad de m/s a km/h y usa la fórmula simplificada.

    Args:
        conductor: Diccionario con propiedades del conductor
        velocidad_viento: Velocidad del viento (m/s)
        altitud_msnm: Altitud (no usada en fórmula simplificada)
        espesor_hielo: Espesor de hielo (mm)
        coef_arrastre: Coeficiente de arrastre (no usado en fórmula simplificada)

    Returns:
        dict con todas las cargas calculadas
    """
    velocidad_kmh = velocidad_viento * 3.6
    resultado = calcular_cargas_hipotesis(conductor, velocidad_kmh)

    # Mapear a la interfaz antigua para compatibilidad
    return {
        'peso_conductor': resultado['peso_conductor'],
        'carga_viento': resultado['fuerza_viento'],
        'carga_viento_con_hielo': resultado['fuerza_viento'],
        'carga_hielo': 0,
        'peso_resultante': resultado['peso_resultante'],
        'angulo_resultante_grados': resultado['angulo_resultante_grados'],
        'carga_especifica': resultado['carga_especifica'],
        'carga_especifica_peso_propio': resultado['carga_especifica_peso'],
        'factor_carga': resultado['factor_carga'],
        'densidad_aire': 1.225,
        'presion_viento_Pa': 0,
        'diametro_conductor': resultado['diametro_conductor'],
        'diametro_efectivo': resultado['diametro_conductor'],
        'seccion_conductor': resultado['seccion_conductor'],
        'velocidad_viento': velocidad_viento,
        'velocidad_viento_kmh': velocidad_kmh,
        'altitud': altitud_msnm,
        'espesor_hielo': espesor_hielo,
        'coef_arrastre': coef_arrastre
    }


def velocidad_kmh_a_ms(velocidad_kmh: float) -> float:
    """Convierte velocidad de km/h a m/s."""
    return velocidad_kmh / 3.6


def velocidad_ms_a_kmh(velocidad_ms: float) -> float:
    """Convierte velocidad de m/s a km/h."""
    return velocidad_ms * 3.6
