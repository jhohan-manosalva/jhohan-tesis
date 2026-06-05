"""
Módulos de cálculo para líneas de transmisión eléctrica de alta tensión.

Este paquete contiene los módulos de cálculo mecánico según normativa RETIE,
IEEE 738 e IEC 60826 para el diseño de líneas de transmisión de 34.5 kV a 500 kV.

Módulos disponibles:
- ecuacion_estado: Ecuación cúbica de cambio de estado
- catenaria: Cálculos de catenaria y parábola
- cargas_mecanicas: Cargas de viento, peso, resultante
- vano_regulador: Cálculo de vano regulador y crítico
- hipotesis_calculo: Las 4 hipótesis de diseño RETIE
- distancias_seguridad: Verificación distancias según RETIE
- capacidad_termica: Cálculo ampacity según IEEE 738
- validaciones: Validaciones contra normativa
"""

from .ecuacion_estado import resolver_ecuacion_estado
from .catenaria import (
    calcular_flecha_parabolica,
    calcular_flecha_catenaria,
    calcular_longitud_conductor,
    comparar_metodos,
    calcular_curva_catenaria
)
from .cargas_mecanicas import (
    calcular_fuerza_viento,
    calcular_factor_carga,
    calcular_cargas_hipotesis,
    calcular_peso_resultante,
    calcular_carga_especifica,
    calcular_cargas_completas
)
from .vano_regulador import (
    calcular_vano_regulador,
    calcular_vano_critico,
    verificar_canton
)
from .hipotesis_calculo import (
    TipoHipotesis,
    ResultadoHipotesis,
    calcular_hipotesis_A,
    calcular_hipotesis_B,
    calcular_hipotesis_C,
    calcular_hipotesis_D,
    analizar_todas_hipotesis
)
from .distancias_seguridad import (
    obtener_distancia_minima,
    verificar_distancia_seguridad,
    calcular_altura_minima_soporte
)
from .capacidad_termica import (
    calcular_ampacity,
    calcular_temperatura_conductor
)
from .validaciones import (
    validar_tension_maxima,
    validar_distancia_seguridad as validar_distancia,
    validar_canton as validar_configuracion_canton
)

__version__ = "1.0.0"
__author__ = "Jhohan Felipe Manosalva Sierra"
