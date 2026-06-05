"""
Módulo de conversión de unidades.

Proporciona funciones para convertir entre las diferentes unidades
utilizadas en cálculos de líneas de transmisión.
"""


# Conversiones de longitud
def m_a_km(metros: float) -> float:
    """Convierte metros a kilómetros."""
    return metros / 1000


def km_a_m(kilometros: float) -> float:
    """Convierte kilómetros a metros."""
    return kilometros * 1000


def mm_a_m(milimetros: float) -> float:
    """Convierte milímetros a metros."""
    return milimetros / 1000


def m_a_mm(metros: float) -> float:
    """Convierte metros a milímetros."""
    return metros * 1000


def pulgadas_a_mm(pulgadas: float) -> float:
    """Convierte pulgadas a milímetros."""
    return pulgadas * 25.4


def mm_a_pulgadas(milimetros: float) -> float:
    """Convierte milímetros a pulgadas."""
    return milimetros / 25.4


def pies_a_m(pies: float) -> float:
    """Convierte pies a metros."""
    return pies * 0.3048


def m_a_pies(metros: float) -> float:
    """Convierte metros a pies."""
    return metros / 0.3048


# Conversiones de velocidad
def kmh_a_ms(km_por_hora: float) -> float:
    """Convierte kilómetros por hora a metros por segundo."""
    return km_por_hora / 3.6


def ms_a_kmh(metros_por_segundo: float) -> float:
    """Convierte metros por segundo a kilómetros por hora."""
    return metros_por_segundo * 3.6


def nudos_a_ms(nudos: float) -> float:
    """Convierte nudos a metros por segundo."""
    return nudos * 0.5144


def ms_a_nudos(metros_por_segundo: float) -> float:
    """Convierte metros por segundo a nudos."""
    return metros_por_segundo / 0.5144


def mph_a_ms(millas_por_hora: float) -> float:
    """Convierte millas por hora a metros por segundo."""
    return millas_por_hora * 0.44704


def ms_a_mph(metros_por_segundo: float) -> float:
    """Convierte metros por segundo a millas por hora."""
    return metros_por_segundo / 0.44704


# Conversiones de fuerza/tensión
def kgf_a_N(kilogramos_fuerza: float) -> float:
    """Convierte kilogramos fuerza a Newtons."""
    return kilogramos_fuerza * 9.80665


def N_a_kgf(newtons: float) -> float:
    """Convierte Newtons a kilogramos fuerza."""
    return newtons / 9.80665


def kgf_a_daN(kilogramos_fuerza: float) -> float:
    """Convierte kilogramos fuerza a decanewtons."""
    return kilogramos_fuerza * 0.980665


def daN_a_kgf(decanewtons: float) -> float:
    """Convierte decanewtons a kilogramos fuerza."""
    return decanewtons / 0.980665


def kgf_a_lbf(kilogramos_fuerza: float) -> float:
    """Convierte kilogramos fuerza a libras fuerza."""
    return kilogramos_fuerza * 2.20462


def lbf_a_kgf(libras_fuerza: float) -> float:
    """Convierte libras fuerza a kilogramos fuerza."""
    return libras_fuerza / 2.20462


def kgf_a_kN(kilogramos_fuerza: float) -> float:
    """Convierte kilogramos fuerza a kilonewtons."""
    return kilogramos_fuerza * 0.00980665


def kN_a_kgf(kilonewtons: float) -> float:
    """Convierte kilonewtons a kilogramos fuerza."""
    return kilonewtons / 0.00980665


# Conversiones de tensión unitaria
def kgf_mm2_a_MPa(kgf_por_mm2: float) -> float:
    """Convierte kgf/mm² a MPa."""
    return kgf_por_mm2 * 9.80665


def MPa_a_kgf_mm2(megapascales: float) -> float:
    """Convierte MPa a kgf/mm²."""
    return megapascales / 9.80665


def kgf_mm2_a_psi(kgf_por_mm2: float) -> float:
    """Convierte kgf/mm² a psi."""
    return kgf_por_mm2 * 1422.33


def psi_a_kgf_mm2(psi: float) -> float:
    """Convierte psi a kgf/mm²."""
    return psi / 1422.33


# Conversiones de temperatura
def celsius_a_fahrenheit(celsius: float) -> float:
    """Convierte grados Celsius a Fahrenheit."""
    return (celsius * 9/5) + 32


def fahrenheit_a_celsius(fahrenheit: float) -> float:
    """Convierte grados Fahrenheit a Celsius."""
    return (fahrenheit - 32) * 5/9


def celsius_a_kelvin(celsius: float) -> float:
    """Convierte grados Celsius a Kelvin."""
    return celsius + 273.15


def kelvin_a_celsius(kelvin: float) -> float:
    """Convierte Kelvin a grados Celsius."""
    return kelvin - 273.15


# Conversiones de área
def mm2_a_m2(milimetros_cuadrados: float) -> float:
    """Convierte mm² a m²."""
    return milimetros_cuadrados * 1e-6


def m2_a_mm2(metros_cuadrados: float) -> float:
    """Convierte m² a mm²."""
    return metros_cuadrados * 1e6


def kcmil_a_mm2(kcmil: float) -> float:
    """Convierte kcmil (MCM) a mm²."""
    return kcmil * 0.5067


def mm2_a_kcmil(mm2: float) -> float:
    """Convierte mm² a kcmil (MCM)."""
    return mm2 / 0.5067


def awg_a_mm2(awg: int) -> float:
    """
    Convierte AWG a mm² (aproximado).

    Fórmula: d(mm) = 0.127 × 92^((36-AWG)/39)
    Área = π × (d/2)²
    """
    import math
    diametro_mm = 0.127 * (92 ** ((36 - awg) / 39))
    area_mm2 = math.pi * (diametro_mm / 2) ** 2
    return area_mm2


# Conversiones de resistencia
def ohm_km_a_ohm_m(ohm_por_km: float) -> float:
    """Convierte Ω/km a Ω/m."""
    return ohm_por_km / 1000


def ohm_m_a_ohm_km(ohm_por_m: float) -> float:
    """Convierte Ω/m a Ω/km."""
    return ohm_por_m * 1000


def ohm_mi_a_ohm_km(ohm_por_milla: float) -> float:
    """Convierte Ω/milla a Ω/km."""
    return ohm_por_milla / 1.60934


def ohm_km_a_ohm_mi(ohm_por_km: float) -> float:
    """Convierte Ω/km a Ω/milla."""
    return ohm_por_km * 1.60934


# Conversiones de peso/masa
def kg_a_lb(kilogramos: float) -> float:
    """Convierte kilogramos a libras."""
    return kilogramos * 2.20462


def lb_a_kg(libras: float) -> float:
    """Convierte libras a kilogramos."""
    return libras / 2.20462


def kg_km_a_lb_ft(kg_por_km: float) -> float:
    """Convierte kg/km a lb/ft."""
    return kg_por_km * 0.000672


def lb_ft_a_kg_km(lb_por_ft: float) -> float:
    """Convierte lb/ft a kg/km."""
    return lb_por_ft / 0.000672


# Conversiones de presión
def Pa_a_kgf_m2(pascales: float) -> float:
    """Convierte Pascales a kgf/m²."""
    return pascales / 9.80665


def kgf_m2_a_Pa(kgf_por_m2: float) -> float:
    """Convierte kgf/m² a Pascales."""
    return kgf_por_m2 * 9.80665


def bar_a_Pa(bar: float) -> float:
    """Convierte bar a Pascales."""
    return bar * 100000


def Pa_a_bar(pascales: float) -> float:
    """Convierte Pascales a bar."""
    return pascales / 100000


# Funciones de formato
def formatear_tension(valor: float, unidad: str = "kg/mm²") -> str:
    """Formatea un valor de tensión con su unidad."""
    return f"{valor:.3f} {unidad}"


def formatear_flecha(valor: float) -> str:
    """Formatea un valor de flecha en metros."""
    return f"{valor:.2f} m"


def formatear_longitud(valor: float, unidad: str = "m") -> str:
    """Formatea un valor de longitud."""
    return f"{valor:.2f} {unidad}"


def formatear_temperatura(valor: float, unidad: str = "°C") -> str:
    """Formatea un valor de temperatura."""
    return f"{valor:.1f} {unidad}"


def formatear_porcentaje(valor: float) -> str:
    """Formatea un valor como porcentaje."""
    return f"{valor:.1f}%"


def formatear_corriente(valor: float) -> str:
    """Formatea un valor de corriente en amperios."""
    return f"{valor:.1f} A"
