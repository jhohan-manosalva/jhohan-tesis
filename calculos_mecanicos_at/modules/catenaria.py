"""
Módulo de cálculos de catenaria y parábola para conductores eléctricos.

Este módulo implementa los cálculos de flecha, longitud y perfil de conductores
utilizando tanto la ecuación exacta de catenaria como la aproximación parabólica.

La ecuación de catenaria es:
    y(x) = c × [cosh(x/c) - 1]
    Donde c = H/w (parámetro catenario)

La aproximación parabólica (válida para f/a < 5%):
    f = (w × a²) / (8 × H)

Referencias:
    - IEC 60826:2017
    - IEEE Std 524-2016
"""

import numpy as np
from typing import Tuple, Optional


def calcular_flecha_parabolica(
    peso_unitario: float,
    vano: float,
    tension_horizontal: float
) -> float:
    """
    Calcula la flecha máxima usando la aproximación parabólica.

    Esta aproximación es válida cuando la relación flecha/vano es menor al 5%.
    Es la más utilizada en cálculos de ingeniería por su simplicidad.

    Fórmula: f = (w × a²) / (8 × H)

    Args:
        peso_unitario: Peso por unidad de longitud del conductor (kg/m)
        vano: Longitud del vano (m)
        tension_horizontal: Tensión horizontal del conductor (kg)

    Returns:
        Flecha máxima en metros

    Raises:
        ValueError: Si algún parámetro es no positivo

    Example:
        >>> flecha = calcular_flecha_parabolica(
        ...     peso_unitario=0.975,
        ...     vano=300,
        ...     tension_horizontal=2000
        ... )
        >>> print(f"Flecha: {flecha:.2f} m")
    """
    if peso_unitario <= 0:
        raise ValueError("El peso unitario debe ser positivo")
    if vano <= 0:
        raise ValueError("El vano debe ser positivo")
    if tension_horizontal <= 0:
        raise ValueError("La tensión horizontal debe ser positiva")

    flecha = (peso_unitario * vano**2) / (8 * tension_horizontal)

    return flecha


def calcular_flecha_catenaria(
    peso_unitario: float,
    vano: float,
    tension_horizontal: float
) -> float:
    """
    Calcula la flecha máxima usando la ecuación exacta de catenaria.

    Utiliza la ecuación: f = c × [cosh(a/(2×c)) - 1]
    Donde c = H/w (parámetro catenario)

    Args:
        peso_unitario: Peso por unidad de longitud del conductor (kg/m)
        vano: Longitud del vano (m)
        tension_horizontal: Tensión horizontal del conductor (kg)

    Returns:
        Flecha máxima en metros

    Raises:
        ValueError: Si algún parámetro es no positivo

    Example:
        >>> flecha = calcular_flecha_catenaria(
        ...     peso_unitario=0.975,
        ...     vano=300,
        ...     tension_horizontal=2000
        ... )
        >>> print(f"Flecha: {flecha:.2f} m")
    """
    if peso_unitario <= 0:
        raise ValueError("El peso unitario debe ser positivo")
    if vano <= 0:
        raise ValueError("El vano debe ser positivo")
    if tension_horizontal <= 0:
        raise ValueError("La tensión horizontal debe ser positiva")

    # Parámetro catenario
    c = tension_horizontal / peso_unitario

    # Flecha según catenaria exacta
    flecha = c * (np.cosh(vano / (2 * c)) - 1)

    return flecha


def calcular_longitud_conductor(
    vano: float,
    flecha: float,
    metodo: str = "parabolica"
) -> float:
    """
    Calcula la longitud real del conductor en el vano.

    La longitud del conductor es mayor que el vano horizontal debido
    a la curvatura de la catenaria.

    Args:
        vano: Longitud horizontal del vano (m)
        flecha: Flecha máxima (m)
        metodo: "parabolica" o "catenaria"

    Returns:
        Longitud del conductor en metros

    Raises:
        ValueError: Si los parámetros son inválidos

    Example:
        >>> L = calcular_longitud_conductor(vano=300, flecha=8.5)
        >>> print(f"Longitud: {L:.2f} m")
    """
    if vano <= 0:
        raise ValueError("El vano debe ser positivo")
    if flecha < 0:
        raise ValueError("La flecha no puede ser negativa")

    if metodo.lower() == "parabolica":
        # Aproximación parabólica: L = a × [1 + (8×f²)/(3×a²)]
        longitud = vano * (1 + (8 * flecha**2) / (3 * vano**2))

    elif metodo.lower() == "catenaria":
        # Para catenaria exacta necesitamos el parámetro c
        # Relación aproximada: f ≈ a²/(8c) para vanos pequeños
        # Por tanto: c ≈ a²/(8f)
        if flecha > 0:
            c = vano**2 / (8 * flecha)
            # Longitud catenaria: L = 2×c × sinh(a/(2×c))
            longitud = 2 * c * np.sinh(vano / (2 * c))
        else:
            longitud = vano
    else:
        raise ValueError(f"Método '{metodo}' no reconocido. Use 'parabolica' o 'catenaria'")

    return longitud


def calcular_longitud_catenaria_exacta(
    peso_unitario: float,
    vano: float,
    tension_horizontal: float
) -> float:
    """
    Calcula la longitud exacta del conductor usando parámetros directos.

    Fórmula: L = 2×c × sinh(a/(2×c))

    Args:
        peso_unitario: Peso por unidad de longitud (kg/m)
        vano: Longitud del vano (m)
        tension_horizontal: Tensión horizontal (kg)

    Returns:
        Longitud del conductor en metros
    """
    if peso_unitario <= 0 or vano <= 0 or tension_horizontal <= 0:
        raise ValueError("Todos los parámetros deben ser positivos")

    c = tension_horizontal / peso_unitario
    longitud = 2 * c * np.sinh(vano / (2 * c))

    return longitud


def comparar_metodos(
    peso_unitario: float,
    vano: float,
    tension_horizontal: float
) -> dict:
    """
    Compara los resultados entre el método parabólico y la catenaria exacta.

    Útil para determinar cuándo la aproximación parabólica es válida.
    La regla general es que la aproximación es válida si f/a < 5%.

    Args:
        peso_unitario: Peso por unidad de longitud (kg/m)
        vano: Longitud del vano (m)
        tension_horizontal: Tensión horizontal (kg)

    Returns:
        dict con:
        - flecha_parabolica: Flecha por método parabólico (m)
        - flecha_catenaria: Flecha por método catenaria (m)
        - diferencia_flecha: Diferencia absoluta (m)
        - diferencia_porcentual: Diferencia porcentual (%)
        - longitud_parabolica: Longitud por método parabólico (m)
        - longitud_catenaria: Longitud por método catenaria (m)
        - relacion_flecha_vano: f/a (%)
        - aproximacion_valida: Si f/a < 5%

    Example:
        >>> comp = comparar_metodos(0.975, 300, 2000)
        >>> print(f"Diferencia: {comp['diferencia_porcentual']:.3f}%")
    """
    # Calcular flechas
    flecha_par = calcular_flecha_parabolica(peso_unitario, vano, tension_horizontal)
    flecha_cat = calcular_flecha_catenaria(peso_unitario, vano, tension_horizontal)

    # Calcular longitudes
    longitud_par = calcular_longitud_conductor(vano, flecha_par, "parabolica")
    longitud_cat = calcular_longitud_catenaria_exacta(peso_unitario, vano, tension_horizontal)

    # Diferencias
    dif_flecha = abs(flecha_par - flecha_cat)
    dif_porcentual = (dif_flecha / flecha_cat) * 100 if flecha_cat > 0 else 0

    dif_longitud = abs(longitud_par - longitud_cat)
    dif_longitud_porcentual = (dif_longitud / longitud_cat) * 100 if longitud_cat > 0 else 0

    # Relación flecha/vano
    relacion_f_a = (flecha_cat / vano) * 100

    return {
        'flecha_parabolica': flecha_par,
        'flecha_catenaria': flecha_cat,
        'diferencia_flecha': dif_flecha,
        'diferencia_porcentual_flecha': dif_porcentual,
        'longitud_parabolica': longitud_par,
        'longitud_catenaria': longitud_cat,
        'diferencia_longitud': dif_longitud,
        'diferencia_porcentual_longitud': dif_longitud_porcentual,
        'relacion_flecha_vano': relacion_f_a,
        'aproximacion_valida': relacion_f_a < 5,
        'parametro_catenario': tension_horizontal / peso_unitario,
        'recomendacion': "Usar aproximación parabólica" if relacion_f_a < 5
                        else "Usar catenaria exacta para mayor precisión"
    }


def calcular_curva_catenaria(
    vano: float,
    flecha: float,
    puntos: int = 100,
    altura_soporte: float = 0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Genera los puntos (x, y) para graficar la curva de la catenaria.

    El origen se coloca en el punto más bajo de la catenaria.
    Los soportes están en x = -vano/2 y x = +vano/2.

    Args:
        vano: Longitud del vano (m)
        flecha: Flecha máxima (m)
        puntos: Número de puntos para la curva
        altura_soporte: Altura de los soportes sobre el punto de referencia (m)

    Returns:
        tuple: (array_x, array_y) coordenadas de la curva

    Example:
        >>> x, y = calcular_curva_catenaria(300, 8.5)
        >>> import matplotlib.pyplot as plt
        >>> plt.plot(x, y)
        >>> plt.show()
    """
    if vano <= 0:
        raise ValueError("El vano debe ser positivo")
    if flecha < 0:
        raise ValueError("La flecha no puede ser negativa")
    if puntos < 2:
        raise ValueError("Se requieren al menos 2 puntos")

    # Estimar parámetro catenario c a partir de flecha y vano
    # f = c × [cosh(a/(2c)) - 1]
    # Para flecha pequeña: f ≈ a²/(8c), entonces c ≈ a²/(8f)
    if flecha > 0:
        c = vano**2 / (8 * flecha)

        # Generar puntos x
        x = np.linspace(-vano/2, vano/2, puntos)

        # Calcular y según catenaria: y = c × [cosh(x/c) - 1]
        # Invertimos para que el conductor "cuelgue" hacia abajo
        y_catenaria = c * (np.cosh(x / c) - 1)

        # Ajustar para que los soportes estén a altura_soporte
        # y el punto más bajo esté en y = altura_soporte - flecha
        y = altura_soporte - y_catenaria
    else:
        # Sin flecha = línea recta
        x = np.linspace(-vano/2, vano/2, puntos)
        y = np.full_like(x, altura_soporte)

    return x, y


def calcular_curva_parabolica(
    vano: float,
    flecha: float,
    puntos: int = 100,
    altura_soporte: float = 0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Genera los puntos (x, y) para graficar la parábola.

    Ecuación: y = (4f/a²) × x² con origen en el vértice

    Args:
        vano: Longitud del vano (m)
        flecha: Flecha máxima (m)
        puntos: Número de puntos para la curva
        altura_soporte: Altura de los soportes (m)

    Returns:
        tuple: (array_x, array_y) coordenadas de la curva
    """
    if vano <= 0:
        raise ValueError("El vano debe ser positivo")
    if flecha < 0:
        raise ValueError("La flecha no puede ser negativa")

    x = np.linspace(-vano/2, vano/2, puntos)

    if flecha > 0:
        # Parábola con vértice en el punto más bajo
        # y = (4f/a²) × x²
        coef = 4 * flecha / vano**2
        y_parabola = coef * x**2
        y = altura_soporte - flecha + y_parabola
    else:
        y = np.full_like(x, altura_soporte)

    return x, y


def calcular_flecha_vano_inclinado(
    peso_unitario: float,
    vano_horizontal: float,
    desnivel: float,
    tension_horizontal: float,
    metodo: str = "parabolica"
) -> dict:
    """
    Calcula la flecha en un vano con soportes a diferente altura.

    En vanos inclinados, el punto de flecha máxima no está en el centro
    del vano sino desplazado hacia el soporte más bajo.

    Args:
        peso_unitario: Peso unitario del conductor (kg/m)
        vano_horizontal: Distancia horizontal entre soportes (m)
        desnivel: Diferencia de altura entre soportes (m), positivo si el
                  soporte derecho es más alto
        tension_horizontal: Tensión horizontal del conductor (kg)
        metodo: "parabolica" o "catenaria"

    Returns:
        dict con:
        - flecha_maxima: Flecha máxima (m)
        - posicion_flecha: Distancia horizontal desde soporte izquierdo (m)
        - flecha_centro: Flecha en el centro del vano (m)
    """
    if vano_horizontal <= 0:
        raise ValueError("El vano horizontal debe ser positivo")
    if tension_horizontal <= 0:
        raise ValueError("La tensión horizontal debe ser positiva")

    a = vano_horizontal
    h = desnivel
    w = peso_unitario
    H = tension_horizontal

    # Parámetro catenario
    c = H / w

    # Posición del punto más bajo (desde soporte izquierdo)
    # x_min = a/2 - (h×H)/(w×a) para parábola
    x_min = a/2 - (h * H) / (w * a)

    # Asegurar que x_min esté dentro del vano
    if x_min < 0:
        x_min = 0
    elif x_min > a:
        x_min = a

    if metodo.lower() == "parabolica":
        # Flecha máxima (perpendicular a la línea de soportes)
        flecha_max = (w * x_min * (a - x_min)) / (2 * H)

        # Flecha en el centro del vano
        flecha_centro = (w * a**2) / (8 * H) - (h**2 * H) / (2 * w * a**2)
    else:
        # Catenaria para vano inclinado (aproximación)
        flecha_max = c * (np.cosh((a - 2*x_min) / (2*c)) - 1)
        flecha_centro = c * (np.cosh(a / (2*c)) - 1) * np.sqrt(1 - (h/a)**2)

    return {
        'flecha_maxima': abs(flecha_max),
        'posicion_flecha_desde_izquierda': x_min,
        'posicion_flecha_desde_centro': x_min - a/2,
        'flecha_centro': abs(flecha_centro),
        'desnivel': h,
        'vano_horizontal': a,
        'metodo': metodo
    }


def calcular_tension_dado_flecha(
    peso_unitario: float,
    vano: float,
    flecha_deseada: float,
    metodo: str = "parabolica"
) -> float:
    """
    Calcula la tensión horizontal necesaria para obtener una flecha dada.

    Útil para el diseño inverso: partir de una flecha máxima permisible
    y determinar la tensión requerida.

    Args:
        peso_unitario: Peso unitario del conductor (kg/m)
        vano: Longitud del vano (m)
        flecha_deseada: Flecha máxima deseada (m)
        metodo: "parabolica" o "catenaria"

    Returns:
        Tensión horizontal requerida (kg)
    """
    if peso_unitario <= 0:
        raise ValueError("El peso unitario debe ser positivo")
    if vano <= 0:
        raise ValueError("El vano debe ser positivo")
    if flecha_deseada <= 0:
        raise ValueError("La flecha deseada debe ser positiva")

    if metodo.lower() == "parabolica":
        # De f = (w × a²) / (8 × H), despejamos H
        tension = (peso_unitario * vano**2) / (8 * flecha_deseada)
    else:
        # Para catenaria, resolver iterativamente
        from scipy import optimize

        def objetivo(H):
            c = H / peso_unitario
            f_calc = c * (np.cosh(vano / (2*c)) - 1)
            return f_calc - flecha_deseada

        # Estimar valor inicial con parábola
        H_inicial = (peso_unitario * vano**2) / (8 * flecha_deseada)

        try:
            tension = optimize.brentq(objetivo, H_inicial * 0.5, H_inicial * 2)
        except ValueError:
            # Fallback a aproximación parabólica
            tension = H_inicial

    return tension
