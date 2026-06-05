"""
Módulo de Ecuación de Cambio de Estado para conductores eléctricos.

Este módulo implementa la solución de la ecuación cúbica de cambio de estado
que relaciona la tensión mecánica de un conductor bajo diferentes condiciones
de temperatura y carga.

Ecuación Principal (Forma Cúbica):
    σ₂³ - σ₂² × [σ₁ - E×α×(t₂-t₁) - (E×a²×g₁²)/(24×σ₁²)] - (E×a²×g₂²)/24 = 0

Referencias:
    - RETIE Resolución 40117 de 2024
    - IEC 60826:2017
"""

import numpy as np
from scipy import optimize
from typing import Optional
import cmath


def resolver_ecuacion_estado(
    sigma_1: float,
    t_1: float,
    t_2: float,
    g_1: float,
    g_2: float,
    a: float,
    E: float,
    alpha: float,
    metodo: str = "cardano"
) -> dict:
    """
    Resuelve la ecuación cúbica de cambio de estado.

    La ecuación de cambio de estado permite calcular la tensión de un conductor
    cuando cambian las condiciones de temperatura y carga.

    Args:
        sigma_1: Tensión unitaria inicial (kg/mm² o daN/mm²)
        t_1: Temperatura inicial (°C)
        t_2: Temperatura final (°C)
        g_1: Carga específica inicial (kg/m/mm²)
        g_2: Carga específica final (kg/m/mm²)
        a: Vano o vano regulador (m)
        E: Módulo de elasticidad del conductor (kg/mm²)
        alpha: Coeficiente de dilatación térmica (1/°C)
        metodo: Método de solución - "cardano", "newton" o "brentq"

    Returns:
        dict con:
        - sigma_2: Tensión final calculada (kg/mm²)
        - flecha: Flecha correspondiente (m)
        - longitud_conductor: Longitud del conductor (m)
        - convergencia: Información del método numérico
        - parametro_A: Coeficiente A de la ecuación
        - parametro_B: Coeficiente B de la ecuación
        - metodo_usado: Método de solución utilizado

    Raises:
        ValueError: Si no se encuentra solución válida o parámetros inválidos

    Example:
        >>> resultado = resolver_ecuacion_estado(
        ...     sigma_1=8.0, t_1=20, t_2=75,
        ...     g_1=0.00404, g_2=0.00404,
        ...     a=300, E=7700, alpha=0.0000193
        ... )
        >>> print(f"Tensión final: {resultado['sigma_2']:.4f} kg/mm²")
    """
    # Validación de parámetros de entrada
    if sigma_1 <= 0:
        raise ValueError("La tensión inicial σ₁ debe ser positiva")
    if a <= 0:
        raise ValueError("El vano debe ser positivo")
    if E <= 0:
        raise ValueError("El módulo de elasticidad debe ser positivo")
    if alpha <= 0:
        raise ValueError("El coeficiente de dilatación debe ser positivo")
    if g_1 <= 0 or g_2 <= 0:
        raise ValueError("Las cargas específicas deben ser positivas")

    # Cálculo de coeficientes de la ecuación cúbica
    # σ₂³ - σ₂² × A - B = 0
    # Donde:
    # A = σ₁ - E×α×(t₂-t₁) - (E×a²×g₁²)/(24×σ₁²)
    # B = (E×a²×g₂²)/24

    delta_t = t_2 - t_1

    # Coeficiente A
    termino_termico = E * alpha * delta_t
    termino_carga_inicial = (E * a**2 * g_1**2) / (24 * sigma_1**2)
    A = sigma_1 - termino_termico - termino_carga_inicial

    # Coeficiente B
    B = (E * a**2 * g_2**2) / 24

    # Resolver según método seleccionado
    if metodo.lower() == "cardano":
        sigma_2, convergencia = _resolver_cardano(A, B)
    elif metodo.lower() == "newton":
        sigma_2, convergencia = _resolver_newton(A, B, sigma_1)
    elif metodo.lower() == "brentq":
        sigma_2, convergencia = _resolver_brentq(A, B, sigma_1)
    else:
        raise ValueError(f"Método '{metodo}' no reconocido. Use 'cardano', 'newton' o 'brentq'")

    # Validar solución
    if sigma_2 is None or sigma_2 <= 0:
        raise ValueError(
            "No se encontró solución física válida para la ecuación de estado. "
            "Verifique los parámetros de entrada."
        )

    # Calcular flecha correspondiente (aproximación parabólica)
    # f = (g × a²) / (8 × σ)
    # Donde la tensión horizontal T = σ × S, y g = w/S
    # Entonces f = (w × a²) / (8 × T) = (g × S × a²) / (8 × σ × S) = (g × a²) / (8 × σ)
    flecha = (g_2 * a**2) / (8 * sigma_2)

    # Calcular longitud del conductor (aproximación parabólica)
    # L = a × [1 + (8×f²)/(3×a²)]
    longitud_conductor = a * (1 + (8 * flecha**2) / (3 * a**2))

    return {
        'sigma_2': sigma_2,
        'flecha': flecha,
        'longitud_conductor': longitud_conductor,
        'convergencia': convergencia,
        'parametro_A': A,
        'parametro_B': B,
        'metodo_usado': metodo,
        'delta_temperatura': delta_t,
        'tension_inicial': sigma_1,
        'carga_especifica_final': g_2
    }


def _resolver_cardano(A: float, B: float) -> tuple:
    """
    Resuelve la ecuación cúbica usando el método de Cardano.

    Ecuación: σ³ - A×σ² - B = 0

    Transformación a forma deprimida: x³ + px + q = 0
    Sustituyendo σ = x + A/3

    Args:
        A: Coeficiente del término cuadrático
        B: Término independiente

    Returns:
        tuple: (solución_real_positiva, info_convergencia)
    """
    # Transformar a forma deprimida x³ + px + q = 0
    # σ = x + A/3
    # p = -A²/3
    # q = -2A³/27 - B

    p = -A**2 / 3
    q = -(2 * A**3) / 27 - B

    # Discriminante de Cardano
    discriminante = (q/2)**2 + (p/3)**3

    info = {
        'metodo': 'Cardano',
        'discriminante': discriminante,
        'p': p,
        'q': q,
        'iteraciones': 0,
        'tipo_solucion': None
    }

    if discriminante > 0:
        # Una raíz real y dos complejas conjugadas
        info['tipo_solucion'] = 'Una raíz real'
        sqrt_disc = np.sqrt(discriminante)
        u = np.cbrt(-q/2 + sqrt_disc)
        v = np.cbrt(-q/2 - sqrt_disc)
        x = u + v
        sigma = x + A/3

    elif discriminante == 0:
        # Raíces reales múltiples
        info['tipo_solucion'] = 'Raíces múltiples'
        if q == 0:
            x1 = 0
            sigma = x1 + A/3
        else:
            u = np.cbrt(-q/2)
            x1 = 2*u
            x2 = -u
            # Tomar la raíz que da sigma positivo
            sigmas = [x1 + A/3, x2 + A/3]
            sigma = max([s for s in sigmas if s > 0], default=None)
    else:
        # Tres raíces reales distintas (caso casus irreducibilis)
        info['tipo_solucion'] = 'Tres raíces reales'
        # Usar forma trigonométrica
        r = np.sqrt(-p**3 / 27)
        theta = np.arccos(-q / (2 * r))

        # Las tres raíces
        x1 = 2 * np.cbrt(r) * np.cos(theta / 3)
        x2 = 2 * np.cbrt(r) * np.cos((theta + 2*np.pi) / 3)
        x3 = 2 * np.cbrt(r) * np.cos((theta + 4*np.pi) / 3)

        sigmas = [x1 + A/3, x2 + A/3, x3 + A/3]
        info['todas_raices'] = sigmas

        # Seleccionar la raíz real positiva más pequeña (físicamente significativa)
        raices_positivas = [s for s in sigmas if s > 0]
        if raices_positivas:
            sigma = min(raices_positivas)
        else:
            sigma = None

    return sigma, info


def _resolver_newton(A: float, B: float, sigma_inicial: float) -> tuple:
    """
    Resuelve la ecuación cúbica usando Newton-Raphson.

    Args:
        A: Coeficiente del término cuadrático
        B: Término independiente
        sigma_inicial: Valor inicial para iteración

    Returns:
        tuple: (solución, info_convergencia)
    """
    def f(sigma):
        return sigma**3 - A * sigma**2 - B

    def df(sigma):
        return 3 * sigma**2 - 2 * A * sigma

    sigma = sigma_inicial
    tolerancia = 1e-10
    max_iter = 100

    info = {
        'metodo': 'Newton-Raphson',
        'iteraciones': 0,
        'tolerancia': tolerancia,
        'convergencia': False,
        'historial': []
    }

    for i in range(max_iter):
        f_val = f(sigma)
        df_val = df(sigma)

        info['historial'].append({
            'iteracion': i,
            'sigma': sigma,
            'f(sigma)': f_val,
            'error': abs(f_val)
        })

        if abs(f_val) < tolerancia:
            info['iteraciones'] = i + 1
            info['convergencia'] = True
            break

        if abs(df_val) < 1e-15:
            # Derivada muy pequeña, ajustar punto inicial
            sigma = sigma * 1.1
            continue

        sigma_new = sigma - f_val / df_val

        # Asegurar que sigma sea positivo
        if sigma_new <= 0:
            sigma_new = sigma / 2

        sigma = sigma_new
        info['iteraciones'] = i + 1

    return sigma, info


def _resolver_brentq(A: float, B: float, sigma_inicial: float) -> tuple:
    """
    Resuelve la ecuación cúbica usando el método de Brent.

    Args:
        A: Coeficiente del término cuadrático
        B: Término independiente
        sigma_inicial: Valor de referencia para establecer intervalo

    Returns:
        tuple: (solución, info_convergencia)
    """
    def f(sigma):
        return sigma**3 - A * sigma**2 - B

    # Establecer intervalo de búsqueda
    # La solución física está típicamente entre 0 y 2*sigma_inicial
    a = 0.001
    b = max(3 * sigma_inicial, 50)

    info = {
        'metodo': 'Brent',
        'intervalo_inicial': (a, b),
        'convergencia': False
    }

    # Verificar que hay cambio de signo en el intervalo
    fa, fb = f(a), f(b)

    if fa * fb > 0:
        # Buscar un intervalo válido
        for mult in [5, 10, 20, 50]:
            b = mult * sigma_inicial
            fb = f(b)
            if fa * fb <= 0:
                break

        if fa * fb > 0:
            # Si aún no hay cambio de signo, usar Newton como fallback
            return _resolver_newton(A, B, sigma_inicial)

    try:
        sigma, result = optimize.brentq(f, a, b, full_output=True)
        info['convergencia'] = result.converged
        info['iteraciones'] = result.iterations
        info['llamadas_funcion'] = result.function_calls
    except ValueError as e:
        info['error'] = str(e)
        # Fallback a Newton
        return _resolver_newton(A, B, sigma_inicial)

    return sigma, info


def calcular_tabla_tensiones(
    conductor: dict,
    vano_regulador: float,
    temperaturas: list,
    tension_inicial: float,
    temperatura_inicial: float,
    carga_especifica_inicial: float,
    carga_especifica_final: float = None,
    metodo: str = "cardano"
) -> list:
    """
    Calcula una tabla de tensiones para diferentes temperaturas.

    Útil para generar curvas de tensión-temperatura del conductor.

    Args:
        conductor: Diccionario con propiedades del conductor
        vano_regulador: Vano regulador en metros
        temperaturas: Lista de temperaturas a evaluar (°C)
        tension_inicial: Tensión inicial de referencia (kg/mm²)
        temperatura_inicial: Temperatura de la condición inicial (°C)
        carga_especifica_inicial: Carga específica inicial (kg/m/mm²)
        carga_especifica_final: Carga específica final (si None, usa la inicial)
        metodo: Método de solución

    Returns:
        Lista de diccionarios con resultados para cada temperatura
    """
    if carga_especifica_final is None:
        carga_especifica_final = carga_especifica_inicial

    E = conductor.get('modulo_elasticidad_final_kgf_mm2', 7700)
    alpha = conductor.get('coef_dilatacion_1_C', 0.0000193)

    resultados = []

    for t in temperaturas:
        try:
            resultado = resolver_ecuacion_estado(
                sigma_1=tension_inicial,
                t_1=temperatura_inicial,
                t_2=t,
                g_1=carga_especifica_inicial,
                g_2=carga_especifica_final,
                a=vano_regulador,
                E=E,
                alpha=alpha,
                metodo=metodo
            )
            resultados.append({
                'temperatura': t,
                'tension': resultado['sigma_2'],
                'flecha': resultado['flecha'],
                'longitud': resultado['longitud_conductor'],
                'valido': True
            })
        except ValueError as e:
            resultados.append({
                'temperatura': t,
                'tension': None,
                'flecha': None,
                'longitud': None,
                'valido': False,
                'error': str(e)
            })

    return resultados


def verificar_ecuacion(sigma_2: float, A: float, B: float) -> dict:
    """
    Verifica que la solución satisface la ecuación original.

    Args:
        sigma_2: Solución calculada
        A: Coeficiente A de la ecuación
        B: Coeficiente B de la ecuación

    Returns:
        dict con información de verificación
    """
    # σ³ - A×σ² - B = 0
    residuo = sigma_2**3 - A * sigma_2**2 - B

    return {
        'residuo': residuo,
        'residuo_relativo': abs(residuo) / B if B != 0 else abs(residuo),
        'verificacion_ok': abs(residuo) < 1e-6,
        'ecuacion': f"σ³ - {A:.6f}×σ² - {B:.6f} = 0",
        'solucion': sigma_2
    }
