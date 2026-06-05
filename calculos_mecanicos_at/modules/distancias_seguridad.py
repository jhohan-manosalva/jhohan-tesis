"""
Módulo de verificación de distancias de seguridad según RETIE.

Este módulo implementa las verificaciones de distancias mínimas de seguridad
para líneas de transmisión según el RETIE (Resolución 40117 de 2024).

Las distancias de seguridad dependen de:
- Nivel de tensión de la línea
- Tipo de cruce (terreno, edificaciones, carreteras, etc.)
- Altitud sobre el nivel del mar

Referencias:
    - RETIE Resolución 40117 de 2024, Artículo 13, Tabla 13.2
    - NTC 2050
"""

import json
from typing import Optional
from pathlib import Path


# Tabla de distancias mínimas según RETIE (metros)
DISTANCIAS_RETIE = {
    34.5: {
        'terreno_transitable': 5.0,
        'terreno_no_transitable': 4.5,
        'edificaciones': 3.7,
        'carreteras': 6.1,
        'ferrocarriles': 7.0,
        'lineas_bt': 2.0,
        'lineas_comunicaciones': 2.0,
        'aguas_navegables': 8.5,
        'aguas_no_navegables': 5.0
    },
    57.5: {
        'terreno_transitable': 5.0,
        'terreno_no_transitable': 4.5,
        'edificaciones': 3.7,
        'carreteras': 6.1,
        'ferrocarriles': 7.0,
        'lineas_bt': 2.0,
        'lineas_comunicaciones': 2.0,
        'aguas_navegables': 8.5,
        'aguas_no_navegables': 5.0
    },
    115: {
        'terreno_transitable': 5.5,
        'terreno_no_transitable': 5.0,
        'edificaciones': 4.0,
        'carreteras': 6.7,
        'ferrocarriles': 7.5,
        'lineas_bt': 2.5,
        'lineas_comunicaciones': 2.5,
        'aguas_navegables': 9.0,
        'aguas_no_navegables': 5.5
    },
    230: {
        'terreno_transitable': 6.5,
        'terreno_no_transitable': 6.0,
        'edificaciones': 4.5,
        'carreteras': 8.5,
        'ferrocarriles': 9.0,
        'lineas_bt': 3.5,
        'lineas_comunicaciones': 3.5,
        'aguas_navegables': 10.5,
        'aguas_no_navegables': 6.5
    },
    500: {
        'terreno_transitable': 9.0,
        'terreno_no_transitable': 8.5,
        'edificaciones': 6.5,
        'carreteras': 11.5,
        'ferrocarriles': 12.5,
        'lineas_bt': 5.5,
        'lineas_comunicaciones': 5.5,
        'aguas_navegables': 14.0,
        'aguas_no_navegables': 9.0
    }
}

# Alias para tipos de cruce
ALIAS_CRUCES = {
    'terreno': 'terreno_transitable',
    'edificacion': 'edificaciones',
    'edificios': 'edificaciones',
    'carretera': 'carreteras',
    'via': 'carreteras',
    'ferrocarril': 'ferrocarriles',
    'tren': 'ferrocarriles',
    'bt': 'lineas_bt',
    'baja_tension': 'lineas_bt',
    'comunicaciones': 'lineas_comunicaciones',
    'aguas': 'aguas_navegables',
    'rio': 'aguas_navegables',
    'lago': 'aguas_no_navegables'
}


def obtener_nivel_tension_base(nivel_tension_kv: float) -> float:
    """
    Obtiene el nivel de tensión base para la tabla RETIE.

    Args:
        nivel_tension_kv: Nivel de tensión de la línea (kV)

    Returns:
        Nivel de tensión base más cercano de la tabla
    """
    niveles = sorted(DISTANCIAS_RETIE.keys())

    for nivel in niveles:
        if nivel_tension_kv <= nivel:
            return nivel

    return max(niveles)


def calcular_factor_altitud(
    altitud_msnm: float,
    nivel_tension_kv: float
) -> float:
    """
    Calcula el factor de corrección por altitud.

    Para tensiones > 57.5 kV y altitudes > 1,000 msnm:
    Factor = 1 + 0.03 × [(altitud - 1000) / 300]

    Args:
        altitud_msnm: Altitud sobre el nivel del mar (m)
        nivel_tension_kv: Nivel de tensión de la línea (kV)

    Returns:
        Factor de corrección (≥ 1.0)
    """
    # Solo aplica para tensiones mayores a 57.5 kV
    if nivel_tension_kv <= 57.5:
        return 1.0

    # Solo aplica para altitudes mayores a 1000 msnm
    if altitud_msnm <= 1000:
        return 1.0

    factor = 1 + 0.03 * ((altitud_msnm - 1000) / 300)

    return factor


def obtener_distancia_minima(
    nivel_tension_kv: float,
    tipo_cruce: str,
    altitud_msnm: float = 0
) -> float:
    """
    Obtiene la distancia mínima de seguridad según RETIE.

    Aplica corrección por altitud cuando corresponde.

    Args:
        nivel_tension_kv: Nivel de tensión de la línea (kV)
        tipo_cruce: Tipo de cruce:
            - "terreno_transitable" o "terreno"
            - "terreno_no_transitable"
            - "edificaciones" o "edificacion"
            - "carreteras" o "carretera"
            - "ferrocarriles" o "ferrocarril"
            - "lineas_bt" o "bt"
            - "lineas_comunicaciones" o "comunicaciones"
            - "aguas_navegables" o "rio"
            - "aguas_no_navegables" o "lago"
        altitud_msnm: Altitud sobre el nivel del mar (m)

    Returns:
        Distancia mínima de seguridad en metros

    Raises:
        ValueError: Si el tipo de cruce no es válido

    Example:
        >>> distancia = obtener_distancia_minima(
        ...     nivel_tension_kv=115,
        ...     tipo_cruce="terreno",
        ...     altitud_msnm=2600
        ... )
        >>> print(f"Distancia mínima: {distancia:.2f} m")
    """
    # Normalizar tipo de cruce
    tipo_normalizado = tipo_cruce.lower().strip()

    # Buscar en alias
    if tipo_normalizado in ALIAS_CRUCES:
        tipo_normalizado = ALIAS_CRUCES[tipo_normalizado]

    # Obtener nivel de tensión base
    nivel_base = obtener_nivel_tension_base(nivel_tension_kv)

    # Verificar que el tipo de cruce existe
    if nivel_base not in DISTANCIAS_RETIE:
        raise ValueError(f"Nivel de tensión {nivel_tension_kv} kV no encontrado en tablas RETIE")

    distancias = DISTANCIAS_RETIE[nivel_base]

    if tipo_normalizado not in distancias:
        tipos_validos = list(distancias.keys())
        raise ValueError(
            f"Tipo de cruce '{tipo_cruce}' no válido. "
            f"Tipos válidos: {tipos_validos}"
        )

    # Obtener distancia base
    distancia_base = distancias[tipo_normalizado]

    # Aplicar factor de corrección por altitud
    factor = calcular_factor_altitud(altitud_msnm, nivel_tension_kv)
    distancia_corregida = distancia_base * factor

    return distancia_corregida


def verificar_distancia_seguridad(
    flecha_maxima: float,
    altura_soporte: float,
    altura_punto_critico: float,
    nivel_tension_kv: float,
    tipo_cruce: str,
    altitud_msnm: float = 0
) -> dict:
    """
    Verifica si se cumple la distancia de seguridad según RETIE.

    La distancia disponible se calcula como:
    distancia_disponible = altura_soporte - flecha_maxima - altura_punto_critico

    Args:
        flecha_maxima: Flecha máxima del conductor (m)
        altura_soporte: Altura del punto de sujeción del conductor (m)
        altura_punto_critico: Altura del obstáculo sobre el terreno (m)
        nivel_tension_kv: Nivel de tensión de la línea (kV)
        tipo_cruce: Tipo de cruce según RETIE
        altitud_msnm: Altitud sobre el nivel del mar (m)

    Returns:
        dict con:
        - distancia_disponible: Distancia vertical disponible (m)
        - distancia_requerida: Distancia mínima según RETIE (m)
        - cumple: Si cumple o no la normativa
        - margen: Diferencia entre disponible y requerida (m)
        - margen_porcentual: Margen en porcentaje
        - factor_altitud: Factor de corrección aplicado
        - observaciones: Lista de observaciones

    Example:
        >>> resultado = verificar_distancia_seguridad(
        ...     flecha_maxima=8.5,
        ...     altura_soporte=20,
        ...     altura_punto_critico=0,
        ...     nivel_tension_kv=115,
        ...     tipo_cruce="terreno"
        ... )
        >>> print(f"Cumple: {resultado['cumple']}")
    """
    # Validar entradas
    if flecha_maxima < 0:
        raise ValueError("La flecha máxima no puede ser negativa")
    if altura_soporte <= 0:
        raise ValueError("La altura del soporte debe ser positiva")
    if altura_punto_critico < 0:
        raise ValueError("La altura del punto crítico no puede ser negativa")

    # Calcular distancia disponible
    distancia_disponible = altura_soporte - flecha_maxima - altura_punto_critico

    # Obtener distancia requerida
    distancia_requerida = obtener_distancia_minima(
        nivel_tension_kv, tipo_cruce, altitud_msnm
    )

    # Calcular factor de altitud
    factor_altitud = calcular_factor_altitud(altitud_msnm, nivel_tension_kv)

    # Verificar cumplimiento
    cumple = distancia_disponible >= distancia_requerida

    # Calcular margen
    margen = distancia_disponible - distancia_requerida
    margen_porcentual = (margen / distancia_requerida) * 100 if distancia_requerida > 0 else 0

    # Generar observaciones
    observaciones = []

    if not cumple:
        observaciones.append(
            f"INCUMPLIMIENTO RETIE: La distancia al {tipo_cruce} es "
            f"{distancia_disponible:.2f} m, menor que el mínimo requerido de "
            f"{distancia_requerida:.2f} m según Tabla 13.2 del RETIE."
        )
        observaciones.append(
            f"Se requiere aumentar la altura del soporte en al menos {abs(margen):.2f} m"
        )
    else:
        if margen_porcentual < 10:
            observaciones.append(
                f"Advertencia: Margen de seguridad bajo ({margen_porcentual:.1f}%)"
            )

    if factor_altitud > 1:
        observaciones.append(
            f"Se aplicó factor de corrección por altitud: {factor_altitud:.3f}"
        )

    return {
        'distancia_disponible': distancia_disponible,
        'distancia_requerida': distancia_requerida,
        'cumple': cumple,
        'margen': margen,
        'margen_porcentual': margen_porcentual,
        'factor_altitud': factor_altitud,
        'nivel_tension_kv': nivel_tension_kv,
        'tipo_cruce': tipo_cruce,
        'altitud_msnm': altitud_msnm,
        'altura_soporte': altura_soporte,
        'flecha_maxima': flecha_maxima,
        'altura_punto_critico': altura_punto_critico,
        'observaciones': observaciones
    }


def calcular_altura_minima_soporte(
    flecha_maxima: float,
    altura_punto_critico: float,
    nivel_tension_kv: float,
    tipo_cruce: str,
    altitud_msnm: float = 0,
    margen_seguridad: float = 0.5
) -> float:
    """
    Calcula la altura mínima requerida del soporte.

    Args:
        flecha_maxima: Flecha máxima del conductor (m)
        altura_punto_critico: Altura del obstáculo (m)
        nivel_tension_kv: Nivel de tensión (kV)
        tipo_cruce: Tipo de cruce según RETIE
        altitud_msnm: Altitud sobre el nivel del mar (m)
        margen_seguridad: Margen adicional de seguridad (m)

    Returns:
        Altura mínima requerida del soporte en metros

    Example:
        >>> altura = calcular_altura_minima_soporte(
        ...     flecha_maxima=8.5,
        ...     altura_punto_critico=0,
        ...     nivel_tension_kv=115,
        ...     tipo_cruce="terreno"
        ... )
        >>> print(f"Altura mínima: {altura:.2f} m")
    """
    distancia_requerida = obtener_distancia_minima(
        nivel_tension_kv, tipo_cruce, altitud_msnm
    )

    altura_minima = flecha_maxima + altura_punto_critico + distancia_requerida + margen_seguridad

    return altura_minima


def obtener_tabla_distancias(nivel_tension_kv: float, altitud_msnm: float = 0) -> dict:
    """
    Obtiene la tabla completa de distancias para un nivel de tensión.

    Args:
        nivel_tension_kv: Nivel de tensión de la línea (kV)
        altitud_msnm: Altitud sobre el nivel del mar (m)

    Returns:
        Diccionario con todas las distancias corregidas por altitud
    """
    nivel_base = obtener_nivel_tension_base(nivel_tension_kv)
    factor = calcular_factor_altitud(altitud_msnm, nivel_tension_kv)

    distancias_base = DISTANCIAS_RETIE[nivel_base]

    distancias_corregidas = {}
    for tipo, distancia in distancias_base.items():
        distancias_corregidas[tipo] = {
            'distancia_base': distancia,
            'factor_altitud': factor,
            'distancia_corregida': distancia * factor
        }

    return {
        'nivel_tension_kv': nivel_tension_kv,
        'nivel_tension_base': nivel_base,
        'altitud_msnm': altitud_msnm,
        'factor_altitud': factor,
        'distancias': distancias_corregidas
    }


def verificar_multiples_cruces(
    flecha_maxima: float,
    altura_soporte: float,
    nivel_tension_kv: float,
    cruces: list,
    altitud_msnm: float = 0
) -> dict:
    """
    Verifica distancias de seguridad para múltiples cruces en un vano.

    Args:
        flecha_maxima: Flecha máxima del conductor (m)
        altura_soporte: Altura del punto de sujeción (m)
        nivel_tension_kv: Nivel de tensión (kV)
        cruces: Lista de diccionarios con 'tipo' y 'altura' de cada cruce
        altitud_msnm: Altitud sobre el nivel del mar (m)

    Returns:
        dict con resultados de cada verificación y resumen
    """
    resultados = []
    todos_cumplen = True

    for cruce in cruces:
        tipo = cruce.get('tipo', 'terreno')
        altura = cruce.get('altura', 0)

        resultado = verificar_distancia_seguridad(
            flecha_maxima=flecha_maxima,
            altura_soporte=altura_soporte,
            altura_punto_critico=altura,
            nivel_tension_kv=nivel_tension_kv,
            tipo_cruce=tipo,
            altitud_msnm=altitud_msnm
        )

        resultados.append(resultado)

        if not resultado['cumple']:
            todos_cumplen = False

    # Encontrar el cruce más crítico
    cruce_critico = min(resultados, key=lambda r: r['margen'])

    return {
        'resultados_individuales': resultados,
        'todos_cumplen': todos_cumplen,
        'cruce_critico': cruce_critico,
        'numero_cruces': len(cruces)
    }


def listar_tipos_cruce() -> list:
    """
    Lista todos los tipos de cruce disponibles.

    Returns:
        Lista de tipos de cruce válidos
    """
    nivel_ejemplo = list(DISTANCIAS_RETIE.keys())[0]
    tipos = list(DISTANCIAS_RETIE[nivel_ejemplo].keys())

    # Agregar alias
    for alias in ALIAS_CRUCES.keys():
        if alias not in tipos:
            tipos.append(f"{alias} (alias)")

    return tipos


def listar_niveles_tension() -> list:
    """
    Lista todos los niveles de tensión disponibles en las tablas.

    Returns:
        Lista de niveles de tensión en kV
    """
    return sorted(DISTANCIAS_RETIE.keys())
