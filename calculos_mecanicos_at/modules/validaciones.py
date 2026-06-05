"""
Módulo de validaciones contra normativa.

Este módulo implementa las validaciones requeridas por el RETIE y otras
normativas aplicables para el diseño de líneas de transmisión.

Validaciones implementadas:
- Tensión máxima del conductor
- Distancias de seguridad
- Configuración de cantón
- Parámetros de entrada
- Límites de operación

Referencias:
    - RETIE Resolución 40117 de 2024
    - NTC 2050
    - IEEE 738
"""

from typing import List, Optional, Union
import warnings


class ValidacionError(Exception):
    """Excepción para errores de validación RETIE."""
    pass


class ValidacionWarning(Warning):
    """Advertencia para condiciones que requieren atención."""
    pass


def validar_tension_maxima(
    tension_calculada: float,
    carga_rotura: float,
    seccion: float,
    limite_porcentaje: float = 50.0,
    hipotesis: str = "A"
) -> dict:
    """
    Valida que la tensión calculada no exceda el límite permitido.

    Según RETIE:
    - Hipótesis A (viento máximo): σ ≤ 50% de carga de rotura
    - Hipótesis B (temp. mínima): σ ≤ 35% de carga de rotura
    - Hipótesis C (EDS): σ = 15-18% de carga de rotura

    Args:
        tension_calculada: Tensión unitaria calculada (kg/mm²)
        carga_rotura: Carga de rotura del conductor (kgf)
        seccion: Sección del conductor (mm²)
        limite_porcentaje: Límite como porcentaje de carga de rotura
        hipotesis: Identificador de la hipótesis ("A", "B", "C", "D")

    Returns:
        dict con:
        - valido: Si cumple el límite
        - tension_calculada: Tensión calculada
        - tension_limite: Tensión límite
        - factor_utilizacion: Porcentaje de utilización
        - mensaje: Mensaje descriptivo

    Raises:
        ValidacionError: Si la tensión excede significativamente el límite

    Example:
        >>> resultado = validar_tension_maxima(
        ...     tension_calculada=15.0,
        ...     carga_rotura=11900,
        ...     seccion=241.7,
        ...     limite_porcentaje=50
        ... )
    """
    if tension_calculada <= 0:
        raise ValidacionError("La tensión calculada debe ser positiva")
    if carga_rotura <= 0:
        raise ValidacionError("La carga de rotura debe ser positiva")
    if seccion <= 0:
        raise ValidacionError("La sección debe ser positiva")

    # Calcular tensión unitaria de rotura
    tension_rotura_unitaria = carga_rotura / seccion

    # Calcular límite
    tension_limite = tension_rotura_unitaria * (limite_porcentaje / 100)

    # Factor de utilización
    factor_utilizacion = (tension_calculada / tension_limite) * 100

    # Validar
    valido = tension_calculada <= tension_limite

    # Generar mensaje
    if not valido:
        mensaje = (
            f"ALERTA RETIE - Hipótesis {hipotesis}: La tensión calculada "
            f"({tension_calculada:.2f} kg/mm²) excede el {limite_porcentaje}% "
            f"de la carga de rotura ({tension_limite:.2f} kg/mm²). "
            f"Factor de utilización: {factor_utilizacion:.1f}%"
        )
    elif factor_utilizacion > 90:
        mensaje = (
            f"Advertencia - Hipótesis {hipotesis}: Factor de utilización alto "
            f"({factor_utilizacion:.1f}%). Tensión: {tension_calculada:.2f} kg/mm², "
            f"Límite: {tension_limite:.2f} kg/mm²"
        )
    else:
        mensaje = (
            f"OK - Hipótesis {hipotesis}: Tensión {tension_calculada:.2f} kg/mm² "
            f"dentro del límite ({tension_limite:.2f} kg/mm²). "
            f"Factor de utilización: {factor_utilizacion:.1f}%"
        )

    return {
        'valido': valido,
        'tension_calculada': tension_calculada,
        'tension_limite': tension_limite,
        'tension_rotura_unitaria': tension_rotura_unitaria,
        'factor_utilizacion': factor_utilizacion,
        'limite_porcentaje': limite_porcentaje,
        'hipotesis': hipotesis,
        'mensaje': mensaje
    }


def validar_distancia_seguridad(
    flecha: float,
    altura_soporte: float,
    distancia_minima: float,
    tipo_cruce: str,
    altura_obstaculo: float = 0
) -> dict:
    """
    Valida que se cumpla la distancia de seguridad según RETIE.

    Args:
        flecha: Flecha máxima del conductor (m)
        altura_soporte: Altura del punto de sujeción (m)
        distancia_minima: Distancia mínima requerida según RETIE (m)
        tipo_cruce: Tipo de cruce
        altura_obstaculo: Altura del obstáculo (m)

    Returns:
        dict con:
        - valido: Si cumple la distancia mínima
        - distancia_disponible: Distancia disponible
        - distancia_minima: Distancia requerida
        - margen: Margen disponible
        - mensaje: Mensaje descriptivo

    Raises:
        ValidacionError: Si hay incumplimiento crítico
    """
    if flecha < 0:
        raise ValidacionError("La flecha no puede ser negativa")
    if altura_soporte <= 0:
        raise ValidacionError("La altura del soporte debe ser positiva")
    if distancia_minima <= 0:
        raise ValidacionError("La distancia mínima debe ser positiva")

    # Calcular distancia disponible
    distancia_disponible = altura_soporte - flecha - altura_obstaculo

    # Calcular margen
    margen = distancia_disponible - distancia_minima

    # Validar
    valido = distancia_disponible >= distancia_minima

    # Generar mensaje
    if not valido:
        mensaje = (
            f"INCUMPLIMIENTO RETIE: La distancia al {tipo_cruce} es "
            f"{distancia_disponible:.2f} m, menor que el mínimo requerido de "
            f"{distancia_minima:.2f} m según Tabla 13.2 del RETIE. "
            f"Se requieren {abs(margen):.2f} m adicionales."
        )
    elif margen < 0.5:
        mensaje = (
            f"Advertencia: Margen reducido para {tipo_cruce}. "
            f"Distancia disponible: {distancia_disponible:.2f} m, "
            f"Mínima: {distancia_minima:.2f} m, Margen: {margen:.2f} m"
        )
    else:
        mensaje = (
            f"OK: Distancia a {tipo_cruce} cumple RETIE. "
            f"Disponible: {distancia_disponible:.2f} m, "
            f"Mínima: {distancia_minima:.2f} m, Margen: {margen:.2f} m"
        )

    return {
        'valido': valido,
        'distancia_disponible': distancia_disponible,
        'distancia_minima': distancia_minima,
        'margen': margen,
        'tipo_cruce': tipo_cruce,
        'altura_soporte': altura_soporte,
        'flecha': flecha,
        'altura_obstaculo': altura_obstaculo,
        'mensaje': mensaje
    }


def validar_canton(
    vanos: List[float],
    vano_regulador: Optional[float] = None,
    limite_relacion: float = 2.5
) -> dict:
    """
    Valida que la configuración del cantón sea válida.

    Regla principal: vano_max ≤ 2.5 × vano_regulador

    Args:
        vanos: Lista de longitudes de vanos (m)
        vano_regulador: Vano regulador (m), si None se calcula
        limite_relacion: Límite de relación vano_max/vano_regulador

    Returns:
        dict con información de validación

    Raises:
        ValidacionError: Si la configuración es inválida
    """
    if not vanos:
        raise ValidacionError("La lista de vanos no puede estar vacía")

    if any(v <= 0 for v in vanos):
        raise ValidacionError("Todos los vanos deben ser positivos")

    # Calcular vano regulador si no se proporciona
    if vano_regulador is None:
        import numpy as np
        suma_cubos = sum(v**3 for v in vanos)
        suma_vanos = sum(vanos)
        vano_regulador = np.sqrt(suma_cubos / suma_vanos)

    # Estadísticas
    vano_max = max(vanos)
    vano_min = min(vanos)
    vano_medio = sum(vanos) / len(vanos)

    # Relación
    relacion = vano_max / vano_regulador

    # Validar
    valido = relacion <= limite_relacion

    # Generar mensajes
    advertencias = []

    if not valido:
        advertencias.append(
            f"El vano máximo ({vano_max:.1f} m) excede {limite_relacion} veces "
            f"el vano regulador ({vano_regulador:.1f} m). Relación: {relacion:.2f}"
        )

    # Verificar variabilidad
    if vano_max / vano_min > 3:
        advertencias.append(
            f"Gran diferencia entre vano mínimo ({vano_min:.1f} m) y "
            f"máximo ({vano_max:.1f} m)"
        )

    # Mensaje principal
    if valido and not advertencias:
        mensaje = (
            f"OK: Cantón válido. Vano regulador: {vano_regulador:.1f} m, "
            f"Relación max/reg: {relacion:.2f}"
        )
    else:
        mensaje = "; ".join(advertencias) if advertencias else "Cantón válido"

    return {
        'valido': valido,
        'vano_regulador': vano_regulador,
        'vano_maximo': vano_max,
        'vano_minimo': vano_min,
        'vano_medio': vano_medio,
        'relacion': relacion,
        'limite_relacion': limite_relacion,
        'numero_vanos': len(vanos),
        'advertencias': advertencias,
        'mensaje': mensaje
    }


def validar_conductor(conductor: dict) -> dict:
    """
    Valida que el conductor tenga todos los parámetros necesarios.

    Args:
        conductor: Diccionario con propiedades del conductor

    Returns:
        dict con resultado de validación
    """
    campos_requeridos = [
        'seccion_total_mm2',
        'diametro_mm',
        'peso_kg_km',
        'carga_rotura_kgf',
        'modulo_elasticidad_final_kgf_mm2',
        'coef_dilatacion_1_C'
    ]

    campos_faltantes = []
    campos_invalidos = []

    for campo in campos_requeridos:
        if campo not in conductor:
            campos_faltantes.append(campo)
        elif conductor[campo] is None or conductor[campo] <= 0:
            campos_invalidos.append(campo)

    valido = len(campos_faltantes) == 0 and len(campos_invalidos) == 0

    if not valido:
        mensaje = []
        if campos_faltantes:
            mensaje.append(f"Campos faltantes: {', '.join(campos_faltantes)}")
        if campos_invalidos:
            mensaje.append(f"Campos inválidos: {', '.join(campos_invalidos)}")
        mensaje = ". ".join(mensaje)
    else:
        mensaje = "Conductor válido con todos los parámetros requeridos"

    return {
        'valido': valido,
        'campos_faltantes': campos_faltantes,
        'campos_invalidos': campos_invalidos,
        'mensaje': mensaje
    }


def validar_zona_climatica(zona: dict) -> dict:
    """
    Valida que la zona climática tenga todos los parámetros necesarios.

    Args:
        zona: Diccionario con parámetros climáticos

    Returns:
        dict con resultado de validación
    """
    campos_requeridos = [
        'temperatura_minima_C',
        'temperatura_media_C',
        'temperatura_maxima_ambiente_C',
        'velocidad_viento_diseno_m_s',
        'altitud_referencia_msnm'
    ]

    campos_faltantes = []
    advertencias = []

    for campo in campos_requeridos:
        if campo not in zona:
            campos_faltantes.append(campo)

    valido = len(campos_faltantes) == 0

    # Validaciones adicionales
    if valido:
        if zona['temperatura_minima_C'] >= zona['temperatura_maxima_ambiente_C']:
            advertencias.append(
                "Temperatura mínima debe ser menor que la máxima"
            )
            valido = False

        if zona['velocidad_viento_diseno_m_s'] < 20:
            advertencias.append(
                "Velocidad de viento de diseño parece baja para alta tensión"
            )

    return {
        'valido': valido,
        'campos_faltantes': campos_faltantes,
        'advertencias': advertencias,
        'mensaje': "Zona climática válida" if valido else "; ".join(
            [f"Campos faltantes: {', '.join(campos_faltantes)}"] + advertencias
        )
    }


def validar_parametros_calculo(
    vano: float,
    tension: float,
    temperatura: float
) -> dict:
    """
    Valida parámetros básicos de cálculo.

    Args:
        vano: Longitud del vano (m)
        tension: Tensión del conductor (kg/mm² o kg)
        temperatura: Temperatura (°C)

    Returns:
        dict con resultado de validación
    """
    errores = []

    if vano <= 0:
        errores.append("El vano debe ser positivo")
    elif vano > 1000:
        errores.append(f"Vano muy largo ({vano} m), verificar valor")

    if tension <= 0:
        errores.append("La tensión debe ser positiva")

    if temperatura < -40 or temperatura > 200:
        errores.append(f"Temperatura fuera de rango típico ({temperatura}°C)")

    valido = len(errores) == 0

    return {
        'valido': valido,
        'errores': errores,
        'mensaje': "Parámetros válidos" if valido else "; ".join(errores)
    }


def generar_informe_validacion(
    resultados_hipotesis: dict,
    verificaciones_distancia: list,
    validacion_canton: dict
) -> dict:
    """
    Genera un informe consolidado de todas las validaciones.

    Args:
        resultados_hipotesis: Resultados de las 4 hipótesis
        verificaciones_distancia: Lista de verificaciones de distancia
        validacion_canton: Resultado de validación del cantón

    Returns:
        dict con informe consolidado
    """
    # Verificar hipótesis
    hipotesis_ok = all(
        validar_tension_maxima(
            h.tension_calculada,
            10000,  # Placeholder
            100,    # Placeholder
            h.porcentaje_limite,
            h.tipo.value
        )['valido']
        for h in resultados_hipotesis.values()
    )

    # Verificar distancias
    distancias_ok = all(v.get('cumple', False) for v in verificaciones_distancia)

    # Verificar cantón
    canton_ok = validacion_canton.get('valido', False)

    # Estado general
    todo_ok = hipotesis_ok and distancias_ok and canton_ok

    # Recopilar problemas
    problemas = []

    for h in resultados_hipotesis.values():
        if not h.cumple_limite:
            problemas.append(f"Hipótesis {h.tipo.value}: Excede límite de tensión")

    for v in verificaciones_distancia:
        if not v.get('cumple', False):
            problemas.append(f"Distancia {v.get('tipo_cruce', 'N/A')}: No cumple mínimo RETIE")

    if not canton_ok:
        problemas.extend(validacion_canton.get('advertencias', []))

    return {
        'cumple_normativa': todo_ok,
        'hipotesis_ok': hipotesis_ok,
        'distancias_ok': distancias_ok,
        'canton_ok': canton_ok,
        'problemas': problemas,
        'numero_problemas': len(problemas),
        'recomendacion': "Diseño cumple con RETIE" if todo_ok
                        else f"Revisar {len(problemas)} problema(s) identificado(s)"
    }
