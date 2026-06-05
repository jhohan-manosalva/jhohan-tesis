"""
Módulo de hipótesis de cálculo según CREG 025/1995 y RETIE.

Implementa las 4 hipótesis de cálculo para líneas de transmisión:

- Hipótesis A: Viento Máximo (temp. coincidente, viento máx.)
- Hipótesis B: Temperatura Mínima (temp. mín., viento reducido)
- Hipótesis C: Condición EDS (operación diaria, FS=5)
- Hipótesis D: Flecha Máxima (temp. máx., sin viento)

Metodología según ejemplo de clase:
1. Calcular Fv para cada hipótesis: Fv = 0.0042 × V² × d / 1000
2. Calcular factor de carga: m = √(1 + (Fv/W)²)
3. Condición inicial: Hip C con FS = 5 → tc = tR / 5
4. Ecuación de estado C→A, C→B, C→D
5. Verificar FS para cada hipótesis

Factores de seguridad (CREG 025/1995):
- Hip A, B, D: 2 ≤ FS ≤ 3 (mínimo FS ≥ 2)
- Hip C (EDS): FS ≥ 5

Referencias:
    - CREG 025/1995 - Código de Redes
    - RETIE Resolución 40117 de 2024
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List
import numpy as np

from .ecuacion_estado import resolver_ecuacion_estado
from .cargas_mecanicas import (
    calcular_cargas_hipotesis,
    calcular_carga_especifica,
    calcular_peso_resultante
)
from .catenaria import calcular_flecha_parabolica


class TipoHipotesis(Enum):
    """Tipos de hipótesis de cálculo."""
    VIENTO_MAXIMO = "A"
    TEMPERATURA_MINIMA = "B"
    EDS = "C"
    FLECHA_MAXIMA = "D"


@dataclass
class ResultadoHipotesis:
    """Resultado del cálculo de una hipótesis."""
    tipo: TipoHipotesis
    nombre: str
    temperatura: float          # °C
    velocidad_viento_kmh: float # km/h
    fuerza_viento: float        # kg/m (Fv)
    factor_carga: float         # m = W'/W
    peso_resultante: float      # kg/m (W')
    carga_especifica: float     # kg/m/mm² (g = W'/S)
    tension_calculada: float    # kg/mm² (t₂ o tc)
    tension_total: float        # kgf (t × S)
    factor_seguridad: float     # FS = tR / t
    fs_minimo: float            # FS mínimo requerido
    flecha: float               # m
    cumple_limite: bool
    factor_utilizacion: float
    observaciones: List[str] = field(default_factory=list)

    # Aliases para compatibilidad con código existente
    @property
    def carga_viento(self):
        return self.fuerza_viento

    @property
    def velocidad_viento(self):
        return self.velocidad_viento_kmh / 3.6

    @property
    def tension_limite(self):
        """Tensión máxima admisible = tR / FS_mínimo."""
        # tR = t × FS, so tR = tension_calculada * factor_seguridad
        tR = self.tension_calculada * self.factor_seguridad
        return tR / self.fs_minimo if self.fs_minimo > 0 else tR

    @property
    def porcentaje_limite(self):
        return (1 / self.fs_minimo) * 100 if self.fs_minimo > 0 else 0

    @property
    def cumple(self):
        return self.cumple_limite


def analizar_todas_hipotesis(
    conductor: dict,
    vano_regulador: float,
    zona_climatica: dict,
    tension_eds: float = 18.0,
    temperatura_operacion: float = 75.0,
    altitud_msnm: float = 0,
    # Parámetros por hipótesis (si se proporcionan, sobreescriben zona_climatica)
    params_hipotesis: dict = None
) -> Dict[TipoHipotesis, ResultadoHipotesis]:
    """
    Ejecuta el análisis completo de las 4 hipótesis.

    Metodología:
    1. Definir condiciones de cada hipótesis (temp, viento)
    2. Calcular Fv y m para cada una
    3. Hipótesis C es la referencia: tc = carga_rotura_unitaria / FS_C
    4. Usar ecuación de estado desde C hacia A, B, D
    5. Calcular FS y verificar cumplimiento

    Args:
        conductor: Propiedades del conductor
        vano_regulador: Vano regulador (m)
        zona_climatica: Parámetros climáticos de la zona
        tension_eds: Porcentaje EDS (no usado directamente, se usa FS=5)
        temperatura_operacion: Temperatura máxima del conductor (°C)
        altitud_msnm: Altitud (no usada en fórmula simplificada)
        params_hipotesis: Dict con parámetros por hipótesis {
            'A': {'temperatura': °C, 'viento_kmh': km/h, 'fs_min': float},
            'B': {...}, 'C': {...}, 'D': {...}
        }

    Returns:
        Dict con ResultadoHipotesis para cada tipo
    """
    # Propiedades del conductor
    seccion = conductor.get('seccion_total_mm2', 100)
    peso_kg_km = conductor.get('peso_kg_km', 1000)
    carga_rotura = conductor.get('carga_rotura_kgf', 10000)
    E = conductor.get('modulo_elasticidad_final_kgf_mm2', 7700)
    alpha = conductor.get('coef_dilatacion_1_C', 0.0000193)
    diametro = conductor.get('diametro_mm', 20)

    peso_conductor = peso_kg_km / 1000  # kg/m
    tension_rotura_unitaria = carga_rotura / seccion  # kg/mm²

    # Definir condiciones de cada hipótesis
    if params_hipotesis:
        hip_params = params_hipotesis
    else:
        # Valores por defecto basados en zona climática
        # (adaptados al formato del ejemplo)
        v_max = zona_climatica.get('velocidad_viento_diseno_km_h',
                                    zona_climatica.get('velocidad_viento_diseno_m_s', 25) * 3.6)
        t_min = zona_climatica.get('temperatura_minima_C', 15)
        t_med = zona_climatica.get('temperatura_media_C', 20)

        hip_params = {
            'A': {
                'temperatura': t_min + 5,  # Temp coincidente con viento máximo
                'viento_kmh': v_max,
                'fs_min': 3
            },
            'B': {
                'temperatura': t_min,
                'viento_kmh': v_max * 0.15,  # Viento reducido (~15%)
                'fs_min': 2
            },
            'C': {
                'temperatura': t_med,
                'viento_kmh': v_max * 0.1,  # Viento mínimo (~10%)
                'fs_min': 5
            },
            'D': {
                'temperatura': temperatura_operacion,
                'viento_kmh': 0,
                'fs_min': 2
            }
        }

    # Calcular cargas para cada hipótesis
    cargas = {}
    for hip_key in ['A', 'B', 'C', 'D']:
        v_kmh = hip_params[hip_key]['viento_kmh']
        cargas[hip_key] = calcular_cargas_hipotesis(conductor, v_kmh)

    # --- Hipótesis C: Condición de referencia ---
    fs_c = hip_params['C']['fs_min']  # Típicamente 5
    tc = tension_rotura_unitaria / fs_c  # Tensión unitaria EDS (kg/mm²)
    temp_c = hip_params['C']['temperatura']
    g_c = cargas['C']['carga_especifica']

    # Calcular flecha para C
    tension_total_c = tc * seccion
    flecha_c = calcular_flecha_parabolica(
        peso_unitario=cargas['C']['peso_resultante'],
        vano=vano_regulador,
        tension_horizontal=tension_total_c
    )

    resultado_C = ResultadoHipotesis(
        tipo=TipoHipotesis.EDS,
        nombre="Hipótesis C - Condición EDS",
        temperatura=temp_c,
        velocidad_viento_kmh=hip_params['C']['viento_kmh'],
        fuerza_viento=cargas['C']['fuerza_viento'],
        factor_carga=cargas['C']['factor_carga'],
        peso_resultante=cargas['C']['peso_resultante'],
        carga_especifica=g_c,
        tension_calculada=tc,
        tension_total=tension_total_c,
        factor_seguridad=fs_c,
        fs_minimo=fs_c,
        flecha=flecha_c,
        cumple_limite=True,
        factor_utilizacion=1 / fs_c,
        observaciones=[
            f"Condición de referencia EDS con FS = {fs_c}",
            f"tc = tR/FS = {tension_rotura_unitaria:.4f}/{fs_c} = {tc:.4f} kg/mm²"
        ]
    )

    # --- Calcular Hipótesis A, B, D usando ecuación de estado desde C ---
    resultados_otros = {}
    for hip_key, tipo, nombre in [
        ('A', TipoHipotesis.VIENTO_MAXIMO, "Hipótesis A - Viento Máximo"),
        ('B', TipoHipotesis.TEMPERATURA_MINIMA, "Hipótesis B - Temperatura Mínima"),
        ('D', TipoHipotesis.FLECHA_MAXIMA, "Hipótesis D - Flecha Máxima"),
    ]:
        temp_hip = hip_params[hip_key]['temperatura']
        g_hip = cargas[hip_key]['carga_especifica']
        fs_min_hip = hip_params[hip_key]['fs_min']

        # Resolver ecuación de estado: C → hip_key
        resultado_ec = resolver_ecuacion_estado(
            sigma_1=tc,           # Tensión inicial (condición C)
            t_1=temp_c,           # Temperatura inicial (condición C)
            t_2=temp_hip,         # Temperatura final (hipótesis destino)
            g_1=g_c,              # Carga específica inicial (condición C)
            g_2=g_hip,            # Carga específica final (hipótesis destino)
            a=vano_regulador,
            E=E,
            alpha=alpha
        )

        t_hip = resultado_ec['sigma_2']
        flecha_hip = resultado_ec['flecha']
        tension_total_hip = t_hip * seccion

        # Factor de seguridad: FS = tR_unitaria / t_hip
        fs_hip = tension_rotura_unitaria / t_hip

        # Verificar cumplimiento
        cumple = fs_hip >= fs_min_hip

        observaciones = []
        if not cumple:
            observaciones.append(
                f"ALERTA: FS = {fs_hip:.2f} < {fs_min_hip} (no cumple)"
            )
        else:
            observaciones.append(
                f"FS = {fs_hip:.2f} >= {fs_min_hip} (cumple)"
            )

        resultados_otros[tipo] = ResultadoHipotesis(
            tipo=tipo,
            nombre=nombre,
            temperatura=temp_hip,
            velocidad_viento_kmh=hip_params[hip_key]['viento_kmh'],
            fuerza_viento=cargas[hip_key]['fuerza_viento'],
            factor_carga=cargas[hip_key]['factor_carga'],
            peso_resultante=cargas[hip_key]['peso_resultante'],
            carga_especifica=g_hip,
            tension_calculada=t_hip,
            tension_total=tension_total_hip,
            factor_seguridad=fs_hip,
            fs_minimo=fs_min_hip,
            flecha=flecha_hip,
            cumple_limite=cumple,
            factor_utilizacion=t_hip / tension_rotura_unitaria,
            observaciones=observaciones
        )

    return {
        TipoHipotesis.VIENTO_MAXIMO: resultados_otros[TipoHipotesis.VIENTO_MAXIMO],
        TipoHipotesis.TEMPERATURA_MINIMA: resultados_otros[TipoHipotesis.TEMPERATURA_MINIMA],
        TipoHipotesis.EDS: resultado_C,
        TipoHipotesis.FLECHA_MAXIMA: resultados_otros[TipoHipotesis.FLECHA_MAXIMA],
    }


def obtener_resumen_hipotesis(
    resultados: Dict[TipoHipotesis, ResultadoHipotesis]
) -> dict:
    """
    Genera un resumen del análisis de todas las hipótesis.
    """
    hipotesis_critica = max(
        resultados.values(),
        key=lambda r: r.factor_utilizacion
    )

    flecha_maxima = max(r.flecha for r in resultados.values())
    todas_cumplen = all(r.cumple_limite for r in resultados.values())

    todas_observaciones = []
    for r in resultados.values():
        todas_observaciones.extend(r.observaciones)

    return {
        'hipotesis_critica': hipotesis_critica.tipo.value,
        'nombre_hipotesis_critica': hipotesis_critica.nombre,
        'factor_utilizacion_maximo': hipotesis_critica.factor_utilizacion,
        'flecha_maxima': flecha_maxima,
        'todas_cumplen': todas_cumplen,
        'observaciones': todas_observaciones,
        'tension_maxima': max(r.tension_calculada for r in resultados.values()),
        'tension_minima': min(r.tension_calculada for r in resultados.values()),
    }


def generar_tabla_comparativa(
    resultados: Dict[TipoHipotesis, ResultadoHipotesis]
) -> list:
    """
    Genera una tabla comparativa de las hipótesis.
    """
    tabla = []

    for tipo, resultado in resultados.items():
        tabla.append({
            'Hipótesis': resultado.nombre,
            'Temp (°C)': resultado.temperatura,
            'Viento (km/h)': round(resultado.velocidad_viento_kmh, 1),
            'Fv (kg/m)': round(resultado.fuerza_viento, 4),
            'm': round(resultado.factor_carga, 4),
            'Tensión (kg/mm²)': round(resultado.tension_calculada, 4),
            'Tensión Total (kgf)': round(resultado.tension_total, 1),
            'FS': round(resultado.factor_seguridad, 2),
            'FS mín': resultado.fs_minimo,
            'Flecha (m)': round(resultado.flecha, 3),
            'Cumple': '✓' if resultado.cumple_limite else '✗'
        })

    return tabla


# Funciones de compatibilidad para imports existentes
def calcular_hipotesis_A(conductor, vano_regulador, condiciones_iniciales, zona_climatica, altitud_msnm=0):
    """Compatibilidad: calcula solo hipótesis A."""
    resultados = analizar_todas_hipotesis(conductor, vano_regulador, zona_climatica, altitud_msnm=altitud_msnm)
    return resultados[TipoHipotesis.VIENTO_MAXIMO]

def calcular_hipotesis_B(conductor, vano_regulador, condiciones_iniciales, zona_climatica, altitud_msnm=0):
    """Compatibilidad: calcula solo hipótesis B."""
    resultados = analizar_todas_hipotesis(conductor, vano_regulador, zona_climatica, altitud_msnm=altitud_msnm)
    return resultados[TipoHipotesis.TEMPERATURA_MINIMA]

def calcular_hipotesis_C(conductor, vano_regulador, tension_eds_porcentaje=18.0, temperatura_media=20.0):
    """Compatibilidad: calcula solo hipótesis C."""
    zona = {'temperatura_media_C': temperatura_media}
    resultados = analizar_todas_hipotesis(conductor, vano_regulador, zona, tension_eds=tension_eds_porcentaje)
    return resultados[TipoHipotesis.EDS]

def calcular_hipotesis_D(conductor, vano_regulador, condiciones_iniciales, temperatura_operacion=75.0, altitud_msnm=0):
    """Compatibilidad: calcula solo hipótesis D."""
    zona = {'temperatura_media_C': 20}
    resultados = analizar_todas_hipotesis(conductor, vano_regulador, zona, temperatura_operacion=temperatura_operacion)
    return resultados[TipoHipotesis.FLECHA_MAXIMA]
