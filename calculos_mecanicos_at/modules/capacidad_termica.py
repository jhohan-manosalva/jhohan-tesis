"""
Módulo de cálculo de capacidad térmica según IEEE 738.

Este módulo implementa los cálculos de ampacidad (capacidad de corriente)
de conductores eléctricos según el estándar IEEE 738-2023.

El balance térmico del conductor es:
    q_c + q_r = q_s + I² × R(Tc)

Donde:
- q_c: Pérdidas por convección (W/m)
- q_r: Pérdidas por radiación (W/m)
- q_s: Ganancia por radiación solar (W/m)
- I²R: Calentamiento resistivo (W/m)

Referencias:
    - IEEE Std 738-2023
    - IEC 61597
"""

import numpy as np
from typing import Optional


# Constantes físicas
STEFAN_BOLTZMANN = 5.67e-8  # W/(m²·K⁴)


def calcular_propiedades_aire(temperatura_film: float, altitud_msnm: float = 0) -> dict:
    """
    Calcula las propiedades termodinámicas del aire.

    La temperatura de film es el promedio entre la temperatura
    del conductor y la temperatura ambiente.

    Args:
        temperatura_film: Temperatura de film (°C)
        altitud_msnm: Altitud sobre el nivel del mar (m)

    Returns:
        dict con propiedades del aire:
        - densidad: kg/m³
        - viscosidad_dinamica: Pa·s
        - viscosidad_cinematica: m²/s
        - conductividad_termica: W/(m·K)
    """
    # Temperatura en Kelvin
    T_f = temperatura_film + 273.15

    # Densidad del aire (modelo de atmósfera estándar)
    rho_0 = 1.225  # kg/m³ a nivel del mar
    T_0 = 288.15  # K
    densidad = rho_0 * (T_0 / (T_0 + 0.0065 * altitud_msnm)) ** 5.2561

    # Corregir por temperatura
    densidad = densidad * (288.15 / T_f)

    # Viscosidad dinámica (fórmula de Sutherland)
    mu_0 = 1.716e-5  # Pa·s a 273 K
    S = 110.4  # Constante de Sutherland
    viscosidad_dinamica = mu_0 * (T_f / 273.15) ** 1.5 * (273.15 + S) / (T_f + S)

    # Viscosidad cinemática
    viscosidad_cinematica = viscosidad_dinamica / densidad

    # Conductividad térmica del aire
    # Aproximación: k_f ≈ 0.0243 + 0.0000728 × T_f (para T en °C)
    conductividad_termica = 0.0243 + 0.0000728 * temperatura_film

    return {
        'densidad': densidad,
        'viscosidad_dinamica': viscosidad_dinamica,
        'viscosidad_cinematica': viscosidad_cinematica,
        'conductividad_termica': conductividad_termica,
        'temperatura_film': temperatura_film
    }


def calcular_numero_reynolds(
    velocidad_viento: float,
    diametro_conductor: float,
    propiedades_aire: dict
) -> float:
    """
    Calcula el número de Reynolds.

    N_Re = (D × V × ρ) / μ = (D × V) / ν

    Args:
        velocidad_viento: Velocidad del viento (m/s)
        diametro_conductor: Diámetro del conductor (mm)
        propiedades_aire: Diccionario con propiedades del aire

    Returns:
        Número de Reynolds (adimensional)
    """
    D = diametro_conductor / 1000  # Convertir a metros
    nu = propiedades_aire['viscosidad_cinematica']

    if velocidad_viento <= 0:
        return 0

    N_Re = (D * velocidad_viento) / nu

    return N_Re


def calcular_factor_angulo_viento(angulo_viento: float) -> float:
    """
    Calcula el factor de corrección por ángulo del viento.

    El ángulo es respecto a la perpendicular del conductor.
    - 90°: Viento perpendicular (máxima convección)
    - 0°: Viento paralelo (mínima convección)

    Args:
        angulo_viento: Ángulo del viento respecto al conductor (grados)

    Returns:
        Factor de corrección K_angle
    """
    # Convertir a radianes
    phi = np.radians(angulo_viento)

    # Fórmula IEEE 738
    K_angle = 1.194 - np.cos(phi) + 0.194 * np.cos(2 * phi) + 0.368 * np.sin(2 * phi)

    return K_angle


def calcular_perdidas_conveccion_forzada(
    temperatura_conductor: float,
    temperatura_ambiente: float,
    velocidad_viento: float,
    diametro_conductor: float,
    altitud_msnm: float = 0,
    angulo_viento: float = 90
) -> float:
    """
    Calcula las pérdidas por convección forzada.

    Fórmula IEEE 738:
    q_c = K_angle × [1.01 + 1.35 × N_Re^0.52] × k_f × (Tc - Ta)

    Args:
        temperatura_conductor: Temperatura del conductor (°C)
        temperatura_ambiente: Temperatura ambiente (°C)
        velocidad_viento: Velocidad del viento (m/s)
        diametro_conductor: Diámetro del conductor (mm)
        altitud_msnm: Altitud sobre el nivel del mar (m)
        angulo_viento: Ángulo del viento respecto al conductor (grados)

    Returns:
        Pérdidas por convección en W/m
    """
    if velocidad_viento <= 0.5:
        # Convección natural para vientos muy bajos
        return calcular_perdidas_conveccion_natural(
            temperatura_conductor, temperatura_ambiente,
            diametro_conductor, altitud_msnm
        )

    # Temperatura de film
    T_film = (temperatura_conductor + temperatura_ambiente) / 2

    # Propiedades del aire
    props = calcular_propiedades_aire(T_film, altitud_msnm)

    # Número de Reynolds
    N_Re = calcular_numero_reynolds(velocidad_viento, diametro_conductor, props)

    # Factor de ángulo
    K_angle = calcular_factor_angulo_viento(angulo_viento)

    # Conductividad térmica
    k_f = props['conductividad_termica']

    # Diferencia de temperatura
    delta_T = temperatura_conductor - temperatura_ambiente

    # Diámetro en metros
    D = diametro_conductor / 1000

    # Pérdidas por convección forzada (IEEE 738, Ecuación 3a)
    if N_Re > 0:
        q_c1 = K_angle * (1.01 + 1.35 * N_Re**0.52) * k_f * delta_T
        # Fórmula alternativa para alto Reynolds (Ecuación 3b)
        q_c2 = K_angle * 0.754 * N_Re**0.6 * k_f * delta_T
        q_c = max(q_c1, q_c2)
    else:
        q_c = 0

    return q_c


def calcular_perdidas_conveccion_natural(
    temperatura_conductor: float,
    temperatura_ambiente: float,
    diametro_conductor: float,
    altitud_msnm: float = 0
) -> float:
    """
    Calcula las pérdidas por convección natural (sin viento).

    Args:
        temperatura_conductor: Temperatura del conductor (°C)
        temperatura_ambiente: Temperatura ambiente (°C)
        diametro_conductor: Diámetro del conductor (mm)
        altitud_msnm: Altitud sobre el nivel del mar (m)

    Returns:
        Pérdidas por convección natural en W/m
    """
    # Diferencia de temperatura
    delta_T = temperatura_conductor - temperatura_ambiente

    if delta_T <= 0:
        return 0

    # Densidad del aire
    rho_0 = 1.225
    rho = rho_0 * ((288.15) / (288.15 + 0.0065 * altitud_msnm)) ** 5.2561

    # Diámetro en metros
    D = diametro_conductor / 1000

    # Fórmula simplificada IEEE 738 para convección natural
    q_cn = 3.645 * rho**0.5 * D**0.75 * delta_T**1.25

    return q_cn


def calcular_perdidas_radiacion(
    temperatura_conductor: float,
    temperatura_ambiente: float,
    diametro_conductor: float,
    emisividad: float = 0.5
) -> float:
    """
    Calcula las pérdidas por radiación térmica.

    Fórmula: q_r = π × D × ε × σ × (Tc⁴ - Ta⁴)

    Args:
        temperatura_conductor: Temperatura del conductor (°C)
        temperatura_ambiente: Temperatura ambiente (°C)
        diametro_conductor: Diámetro del conductor (mm)
        emisividad: Emisividad del conductor (0.23-0.91, típico 0.5)

    Returns:
        Pérdidas por radiación en W/m
    """
    # Temperaturas en Kelvin
    T_c = temperatura_conductor + 273.15
    T_a = temperatura_ambiente + 273.15

    # Diámetro en metros
    D = diametro_conductor / 1000

    # Pérdidas por radiación
    q_r = np.pi * D * emisividad * STEFAN_BOLTZMANN * (T_c**4 - T_a**4)

    return q_r


def calcular_ganancia_solar(
    diametro_conductor: float,
    absortividad: float = 0.5,
    radiacion_solar: float = 1000,
    angulo_solar: float = 90
) -> float:
    """
    Calcula la ganancia de calor por radiación solar.

    Fórmula: q_s = α × Q_se × sin(θ) × A'

    Args:
        diametro_conductor: Diámetro del conductor (mm)
        absortividad: Absortividad solar del conductor (0.23-0.91, típico 0.5)
        radiacion_solar: Radiación solar total (W/m²)
        angulo_solar: Ángulo de elevación solar (grados)

    Returns:
        Ganancia solar en W/m
    """
    # Diámetro en metros
    D = diametro_conductor / 1000

    # Área proyectada por unidad de longitud
    A_proj = D  # m²/m

    # Factor de ángulo solar
    theta = np.radians(angulo_solar)

    # Ganancia solar
    q_s = absortividad * radiacion_solar * np.sin(theta) * A_proj

    return q_s


def calcular_resistencia_ac(
    resistencia_dc_20C: float,
    temperatura_conductor: float,
    coef_temperatura: float = 0.00403
) -> float:
    """
    Calcula la resistencia AC a la temperatura del conductor.

    Args:
        resistencia_dc_20C: Resistencia DC a 20°C (Ω/km)
        temperatura_conductor: Temperatura del conductor (°C)
        coef_temperatura: Coeficiente de temperatura (1/°C)

    Returns:
        Resistencia AC a la temperatura del conductor (Ω/m)
    """
    # Corregir por temperatura
    R_dc_T = resistencia_dc_20C * (1 + coef_temperatura * (temperatura_conductor - 20))

    # Factor de efecto skin (aproximación para conductores ACSR)
    # Para frecuencia 60 Hz, el factor típico es 1.02-1.05
    factor_skin = 1.03

    # Resistencia AC
    R_ac = R_dc_T * factor_skin

    # Convertir de Ω/km a Ω/m
    R_ac_m = R_ac / 1000

    return R_ac_m


def calcular_ampacity(
    diametro_conductor: float,
    resistencia_ac: float,
    temperatura_conductor: float,
    temperatura_ambiente: float,
    velocidad_viento: float,
    altitud_msnm: float,
    angulo_viento: float = 90,
    emisividad: float = 0.5,
    absortividad: float = 0.5,
    radiacion_solar: float = 1000
) -> dict:
    """
    Calcula la capacidad de corriente (ampacity) según IEEE 738.

    Balance térmico: q_c + q_r = q_s + I² × R(Tc)
    Despejando: I_max = √[(q_c + q_r - q_s) / R(Tc)]

    Args:
        diametro_conductor: Diámetro del conductor (mm)
        resistencia_ac: Resistencia AC a temperatura de referencia (Ω/km)
        temperatura_conductor: Temperatura máxima del conductor (°C)
        temperatura_ambiente: Temperatura ambiente (°C)
        velocidad_viento: Velocidad del viento (m/s)
        altitud_msnm: Altitud sobre el nivel del mar (m)
        angulo_viento: Ángulo del viento respecto al conductor (grados)
        emisividad: Emisividad del conductor (0-1)
        absortividad: Absortividad solar del conductor (0-1)
        radiacion_solar: Radiación solar (W/m²)

    Returns:
        dict con:
        - ampacity: Corriente máxima (A)
        - perdidas_conveccion: W/m
        - perdidas_radiacion: W/m
        - ganancia_solar: W/m
        - resistencia_ac: Ω/m a temperatura del conductor
        - balance_termico: W/m disponible para I²R

    Example:
        >>> resultado = calcular_ampacity(
        ...     diametro_conductor=21.79,
        ...     resistencia_ac=0.1198,
        ...     temperatura_conductor=75,
        ...     temperatura_ambiente=35,
        ...     velocidad_viento=0.6,
        ...     altitud_msnm=1000
        ... )
        >>> print(f"Ampacity: {resultado['ampacity']:.1f} A")
    """
    # Calcular resistencia a temperatura del conductor
    R_ac = calcular_resistencia_ac(resistencia_ac, temperatura_conductor)

    # Calcular pérdidas por convección
    if velocidad_viento > 0.5:
        q_c = calcular_perdidas_conveccion_forzada(
            temperatura_conductor, temperatura_ambiente,
            velocidad_viento, diametro_conductor,
            altitud_msnm, angulo_viento
        )
    else:
        q_c = calcular_perdidas_conveccion_natural(
            temperatura_conductor, temperatura_ambiente,
            diametro_conductor, altitud_msnm
        )

    # Calcular pérdidas por radiación
    q_r = calcular_perdidas_radiacion(
        temperatura_conductor, temperatura_ambiente,
        diametro_conductor, emisividad
    )

    # Calcular ganancia solar
    q_s = calcular_ganancia_solar(
        diametro_conductor, absortividad, radiacion_solar
    )

    # Balance térmico disponible para calentamiento resistivo
    balance = q_c + q_r - q_s

    # Calcular ampacity
    if balance > 0 and R_ac > 0:
        ampacity = np.sqrt(balance / R_ac)
    else:
        ampacity = 0

    return {
        'ampacity': ampacity,
        'perdidas_conveccion': q_c,
        'perdidas_radiacion': q_r,
        'ganancia_solar': q_s,
        'resistencia_ac_ohm_m': R_ac,
        'balance_termico': balance,
        'temperatura_conductor': temperatura_conductor,
        'temperatura_ambiente': temperatura_ambiente,
        'velocidad_viento': velocidad_viento
    }


def calcular_temperatura_conductor(
    corriente: float,
    diametro_conductor: float,
    resistencia_ac: float,
    temperatura_ambiente: float,
    velocidad_viento: float,
    altitud_msnm: float,
    angulo_viento: float = 90,
    emisividad: float = 0.5,
    absortividad: float = 0.5,
    radiacion_solar: float = 1000,
    tolerancia: float = 0.1,
    max_iter: int = 100
) -> float:
    """
    Calcula la temperatura del conductor para una corriente dada.

    Utiliza un método iterativo para resolver el balance térmico.

    Args:
        corriente: Corriente por el conductor (A)
        diametro_conductor: Diámetro del conductor (mm)
        resistencia_ac: Resistencia AC a 20°C (Ω/km)
        temperatura_ambiente: Temperatura ambiente (°C)
        velocidad_viento: Velocidad del viento (m/s)
        altitud_msnm: Altitud sobre el nivel del mar (m)
        angulo_viento: Ángulo del viento (grados)
        emisividad: Emisividad del conductor
        absortividad: Absortividad solar
        radiacion_solar: Radiación solar (W/m²)
        tolerancia: Tolerancia de convergencia (°C)
        max_iter: Número máximo de iteraciones

    Returns:
        Temperatura del conductor en °C
    """
    # Estimación inicial
    T_c = temperatura_ambiente + 40

    for i in range(max_iter):
        # Calcular resistencia a temperatura actual
        R_ac = calcular_resistencia_ac(resistencia_ac, T_c)

        # Calor generado por efecto Joule
        q_joule = corriente**2 * R_ac

        # Pérdidas por convección
        if velocidad_viento > 0.5:
            q_c = calcular_perdidas_conveccion_forzada(
                T_c, temperatura_ambiente, velocidad_viento,
                diametro_conductor, altitud_msnm, angulo_viento
            )
        else:
            q_c = calcular_perdidas_conveccion_natural(
                T_c, temperatura_ambiente, diametro_conductor, altitud_msnm
            )

        # Pérdidas por radiación
        q_r = calcular_perdidas_radiacion(
            T_c, temperatura_ambiente, diametro_conductor, emisividad
        )

        # Ganancia solar
        q_s = calcular_ganancia_solar(
            diametro_conductor, absortividad, radiacion_solar
        )

        # Balance térmico
        # q_c + q_r = q_s + q_joule
        # Si q_c + q_r > q_s + q_joule: bajar temperatura
        # Si q_c + q_r < q_s + q_joule: subir temperatura
        desequilibrio = q_s + q_joule - q_c - q_r

        # Ajustar temperatura
        # El coeficiente de ajuste depende de la sensibilidad térmica
        factor_ajuste = 0.5
        T_c_new = T_c + factor_ajuste * desequilibrio / (q_c / (T_c - temperatura_ambiente + 1))

        # Verificar convergencia
        if abs(T_c_new - T_c) < tolerancia:
            return T_c_new

        T_c = T_c_new

        # Limitar temperatura
        T_c = max(temperatura_ambiente, min(T_c, 300))

    return T_c


def calcular_tabla_ampacity(
    conductor: dict,
    temperaturas_conductor: list = None,
    temperaturas_ambiente: list = None,
    velocidades_viento: list = None,
    altitud_msnm: float = 0
) -> list:
    """
    Genera una tabla de ampacity para diferentes condiciones.

    Args:
        conductor: Diccionario con propiedades del conductor
        temperaturas_conductor: Lista de temperaturas del conductor (°C)
        temperaturas_ambiente: Lista de temperaturas ambiente (°C)
        velocidades_viento: Lista de velocidades de viento (m/s)
        altitud_msnm: Altitud sobre el nivel del mar (m)

    Returns:
        Lista de diccionarios con resultados
    """
    if temperaturas_conductor is None:
        temperaturas_conductor = [50, 75, 100]

    if temperaturas_ambiente is None:
        temperaturas_ambiente = [25, 35]

    if velocidades_viento is None:
        velocidades_viento = [0.6, 1.0, 2.0]

    diametro = conductor.get('diametro_mm', 20)
    resistencia = conductor.get('resistencia_dc_20C_ohm_km', 0.1)

    resultados = []

    for T_c in temperaturas_conductor:
        for T_a in temperaturas_ambiente:
            if T_c <= T_a:
                continue
            for v in velocidades_viento:
                resultado = calcular_ampacity(
                    diametro_conductor=diametro,
                    resistencia_ac=resistencia,
                    temperatura_conductor=T_c,
                    temperatura_ambiente=T_a,
                    velocidad_viento=v,
                    altitud_msnm=altitud_msnm
                )

                resultados.append({
                    'T_conductor': T_c,
                    'T_ambiente': T_a,
                    'velocidad_viento': v,
                    'ampacity': resultado['ampacity']
                })

    return resultados
