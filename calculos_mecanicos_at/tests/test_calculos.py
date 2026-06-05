"""
Tests unitarios para los módulos de cálculo.

Ejecutar con: pytest tests/test_calculos.py -v
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.ecuacion_estado import resolver_ecuacion_estado, verificar_ecuacion
from modules.catenaria import (
    calcular_flecha_parabolica, calcular_flecha_catenaria,
    calcular_longitud_conductor, comparar_metodos
)
from modules.cargas_mecanicas import (
    calcular_fuerza_viento, calcular_factor_carga,
    calcular_peso_resultante, calcular_carga_especifica,
    calcular_cargas_hipotesis
)
from modules.vano_regulador import calcular_vano_regulador, verificar_canton
from modules.distancias_seguridad import (
    obtener_distancia_minima, calcular_factor_altitud
)


class TestEcuacionEstado:
    """Tests para el módulo de ecuación de cambio de estado."""

    def test_caso_basico_hawk(self):
        """Test con conductor Hawk, caso típico de transmisión."""
        # Conductor Hawk: E=7700 kgf/mm², α=1.93e-5 1/°C
        resultado = resolver_ecuacion_estado(
            sigma_1=8.0,      # kg/mm² (tensión EDS inicial)
            t_1=20,           # °C
            t_2=75,           # °C (temperatura máxima)
            g_1=0.00404,      # kg/m/mm² (solo peso propio)
            g_2=0.00404,      # kg/m/mm² (solo peso propio)
            a=300,            # m (vano regulador)
            E=7700,           # kg/mm²
            alpha=0.0000193   # 1/°C
        )

        # La tensión debe disminuir al aumentar temperatura
        assert resultado['sigma_2'] < 8.0, "La tensión debe disminuir con aumento de temperatura"
        # La tensión debe ser positiva
        assert resultado['sigma_2'] > 0, "La tensión debe ser positiva"
        # La flecha debe aumentar
        assert resultado['flecha'] > 0, "La flecha debe ser positiva"

    def test_tension_aumenta_con_viento(self):
        """La tensión debe aumentar cuando hay carga de viento."""
        # Sin viento
        resultado_sin_viento = resolver_ecuacion_estado(
            sigma_1=8.0, t_1=20, t_2=15,
            g_1=0.00404, g_2=0.00404,
            a=300, E=7700, alpha=0.0000193
        )

        # Con viento (mayor carga específica)
        resultado_con_viento = resolver_ecuacion_estado(
            sigma_1=8.0, t_1=20, t_2=15,
            g_1=0.00404, g_2=0.007,  # Mayor carga por viento
            a=300, E=7700, alpha=0.0000193
        )

        assert resultado_con_viento['sigma_2'] > resultado_sin_viento['sigma_2'], \
            "La tensión debe aumentar con carga de viento"

    def test_tension_aumenta_con_temperatura_baja(self):
        """La tensión debe aumentar cuando baja la temperatura."""
        resultado = resolver_ecuacion_estado(
            sigma_1=8.0, t_1=20, t_2=5,  # Baja de 20°C a 5°C
            g_1=0.00404, g_2=0.00404,
            a=300, E=7700, alpha=0.0000193
        )

        assert resultado['sigma_2'] > 8.0, \
            "La tensión debe aumentar cuando baja la temperatura"

    def test_metodos_dan_resultados_similares(self):
        """Los tres métodos deben dar resultados similares."""
        params = {
            'sigma_1': 8.0, 't_1': 20, 't_2': 50,
            'g_1': 0.00404, 'g_2': 0.00404,
            'a': 300, 'E': 7700, 'alpha': 0.0000193
        }

        resultado_cardano = resolver_ecuacion_estado(**params, metodo='cardano')
        resultado_newton = resolver_ecuacion_estado(**params, metodo='newton')
        resultado_brentq = resolver_ecuacion_estado(**params, metodo='brentq')

        # Tolerancia del 1%
        tolerancia = 0.01

        assert abs(resultado_cardano['sigma_2'] - resultado_newton['sigma_2']) / resultado_cardano['sigma_2'] < tolerancia
        assert abs(resultado_cardano['sigma_2'] - resultado_brentq['sigma_2']) / resultado_cardano['sigma_2'] < tolerancia

    def test_verificacion_ecuacion(self):
        """Verifica que la solución satisface la ecuación original."""
        resultado = resolver_ecuacion_estado(
            sigma_1=8.0, t_1=20, t_2=75,
            g_1=0.00404, g_2=0.00404,
            a=300, E=7700, alpha=0.0000193
        )

        verificacion = verificar_ecuacion(
            resultado['sigma_2'],
            resultado['parametro_A'],
            resultado['parametro_B']
        )

        assert verificacion['verificacion_ok'], \
            f"La solución no satisface la ecuación. Residuo: {verificacion['residuo']}"

    def test_parametros_invalidos(self):
        """Debe lanzar error con parámetros inválidos."""
        with pytest.raises(ValueError):
            resolver_ecuacion_estado(
                sigma_1=-8.0,  # Tensión negativa
                t_1=20, t_2=75,
                g_1=0.00404, g_2=0.00404,
                a=300, E=7700, alpha=0.0000193
            )

        with pytest.raises(ValueError):
            resolver_ecuacion_estado(
                sigma_1=8.0, t_1=20, t_2=75,
                g_1=0.00404, g_2=0.00404,
                a=-300,  # Vano negativo
                E=7700, alpha=0.0000193
            )


class TestCatenaria:
    """Tests para cálculos de flecha."""

    def test_flecha_parabolica_basica(self):
        """Test básico de flecha parabólica."""
        flecha = calcular_flecha_parabolica(
            peso_unitario=0.975,  # kg/m
            vano=200,             # m
            tension_horizontal=2000  # kg
        )

        assert flecha > 0, "La flecha debe ser positiva"
        # Verificar orden de magnitud (flecha típica 2-15m para estos parámetros)
        assert 1 < flecha < 20, f"Flecha fuera de rango esperado: {flecha}"

    def test_flecha_parabolica_vs_catenaria(self):
        """Para vanos cortos, parábola y catenaria deben ser similares."""
        flecha_par = calcular_flecha_parabolica(
            peso_unitario=0.975,
            vano=200,
            tension_horizontal=2000
        )
        flecha_cat = calcular_flecha_catenaria(
            peso_unitario=0.975,
            vano=200,
            tension_horizontal=2000
        )

        # Diferencia menor al 1% para vanos de 200m
        diferencia_porcentual = abs(flecha_par - flecha_cat) / flecha_cat
        assert diferencia_porcentual < 0.01, \
            f"Diferencia {diferencia_porcentual*100:.2f}% mayor al 1%"

    def test_flecha_aumenta_con_vano(self):
        """La flecha debe aumentar con el cuadrado del vano."""
        flecha_200 = calcular_flecha_parabolica(0.975, 200, 2000)
        flecha_400 = calcular_flecha_parabolica(0.975, 400, 2000)

        # flecha_400 ≈ 4 × flecha_200 (por el cuadrado del vano)
        ratio = flecha_400 / flecha_200
        assert 3.5 < ratio < 4.5, f"Ratio de flechas inesperado: {ratio}"

    def test_flecha_disminuye_con_tension(self):
        """La flecha debe disminuir al aumentar la tensión."""
        flecha_baja = calcular_flecha_parabolica(0.975, 300, 1500)
        flecha_alta = calcular_flecha_parabolica(0.975, 300, 3000)

        assert flecha_alta < flecha_baja, \
            "La flecha debe disminuir con mayor tensión"

    def test_longitud_conductor_mayor_que_vano(self):
        """La longitud del conductor debe ser mayor que el vano."""
        vano = 300
        flecha = 8.5

        longitud = calcular_longitud_conductor(vano, flecha, "parabolica")

        assert longitud > vano, "La longitud debe ser mayor que el vano"
        # La diferencia típica es pequeña (< 5%)
        exceso = (longitud - vano) / vano
        assert exceso < 0.05, f"Exceso de longitud muy alto: {exceso*100:.2f}%"

    def test_comparar_metodos(self):
        """Test de la función de comparación de métodos."""
        comp = comparar_metodos(
            peso_unitario=0.975,
            vano=200,
            tension_horizontal=2000
        )

        assert 'flecha_parabolica' in comp
        assert 'flecha_catenaria' in comp
        assert 'relacion_flecha_vano' in comp
        assert 'aproximacion_valida' in comp

        # Para relación f/a < 5%, la aproximación debe ser válida
        if comp['relacion_flecha_vano'] < 5:
            assert comp['aproximacion_valida']


class TestCargasViento:
    """Tests para cálculos de carga de viento (fórmula simplificada)."""

    def test_fuerza_viento_formula(self):
        """Test de Fv = 0.0042 × V² × d / 1000."""
        # Ejemplo de clase: V=110 km/h, d=11.354 mm → Fv ≈ 0.5770
        fv = calcular_fuerza_viento(110, 11.354)
        assert abs(fv - 0.5770) < 0.001, f"Fv incorrecto: {fv}"

    def test_fuerza_viento_sin_viento(self):
        """Sin viento, la fuerza debe ser 0."""
        fv = calcular_fuerza_viento(0, 21.79)
        assert fv == 0, f"Fv debe ser 0 sin viento: {fv}"

    def test_fuerza_viento_proporcional_cuadrado(self):
        """Fv proporcional a V²."""
        fv_50 = calcular_fuerza_viento(50, 21.79)
        fv_100 = calcular_fuerza_viento(100, 21.79)
        ratio = fv_100 / fv_50
        assert abs(ratio - 4.0) < 0.01, f"Ratio V² incorrecto: {ratio}"

    def test_factor_carga_sin_viento(self):
        """Sin viento, m debe ser 1."""
        m = calcular_factor_carga(0.975, 0)
        assert abs(m - 1.0) < 0.001, f"m sin viento debe ser 1: {m}"

    def test_factor_carga_con_viento(self):
        """m = √(1 + (Fv/W)²) > 1."""
        m = calcular_factor_carga(0.2725, 0.5770)
        assert m > 1.0, f"m con viento debe ser > 1: {m}"
        # Ejemplo clase: m ≈ 2.3417
        assert abs(m - 2.3417) < 0.01, f"m incorrecto: {m}"

    def test_cargas_hipotesis_completas(self):
        """Test del cálculo completo de cargas por hipótesis."""
        conductor = {
            'diametro_mm': 11.354,
            'peso_kg_km': 272.5,
            'seccion_total_mm2': 78.645,
        }
        cargas = calcular_cargas_hipotesis(conductor, 110)

        assert cargas['fuerza_viento'] > 0
        assert cargas['factor_carga'] > 1
        assert cargas['peso_resultante'] > cargas['peso_conductor']
        assert cargas['carga_especifica'] > 0

    def test_peso_resultante(self):
        """Test de cálculo de peso resultante."""
        peso_cond = 0.975  # kg/m
        carga_viento = 0.85  # kg/m

        peso_res = calcular_peso_resultante(peso_cond, carga_viento)

        # Peso resultante = √(0.975² + 0.85²) ≈ 1.29 kg/m
        esperado = np.sqrt(peso_cond**2 + carga_viento**2)
        assert abs(peso_res - esperado) < 0.01

    def test_carga_especifica(self):
        """Test de cálculo de carga específica."""
        peso_res = 1.3  # kg/m
        seccion = 241.7  # mm²

        g = calcular_carga_especifica(peso_res, seccion)

        esperado = peso_res / seccion
        assert abs(g - esperado) < 1e-8


class TestVanoRegulador:
    """Tests para cálculos de vano regulador."""

    def test_vano_regulador_uniforme(self):
        """Para vanos iguales, el regulador debe ser igual al vano."""
        vanos = [300, 300, 300, 300]
        vano_reg = calcular_vano_regulador(vanos)

        assert abs(vano_reg - 300) < 0.01, \
            f"Vano regulador incorrecto para vanos uniformes: {vano_reg}"

    def test_vano_regulador_formula(self):
        """Test de la fórmula del vano regulador."""
        vanos = [280, 320, 300, 290, 310]

        # Fórmula: Lr = √(Σ(Li³) / Σ(Li))
        suma_cubos = sum(v**3 for v in vanos)
        suma_vanos = sum(vanos)
        esperado = np.sqrt(suma_cubos / suma_vanos)

        vano_reg = calcular_vano_regulador(vanos)

        assert abs(vano_reg - esperado) < 0.01

    def test_verificar_canton_valido(self):
        """Test de verificación de cantón válido."""
        vanos = [280, 320, 300, 290, 310]
        resultado = verificar_canton(vanos)

        assert resultado['valido'], "El cantón debería ser válido"
        assert resultado['relacion'] < 2.5, "Relación debe ser menor a 2.5"

    def test_verificar_canton_invalido(self):
        """Test de verificación de cantón inválido."""
        vanos = [100, 100, 100, 500]  # Vano muy largo
        resultado = verificar_canton(vanos)

        # El vano máximo (500) puede exceder 2.5 × vano regulador
        # dependiendo de los valores
        assert len(resultado['advertencias']) > 0 or not resultado['valido']


class TestDistanciasSeguridad:
    """Tests para distancias de seguridad RETIE."""

    def test_distancia_115kv_terreno(self):
        """Test de distancia mínima para 115kV a terreno."""
        distancia = obtener_distancia_minima(
            nivel_tension_kv=115,
            tipo_cruce="terreno",
            altitud_msnm=0
        )

        # Según RETIE: 5.5 m para 115 kV
        assert abs(distancia - 5.5) < 0.1, \
            f"Distancia incorrecta para 115kV: {distancia}"

    def test_distancia_230kv_carreteras(self):
        """Test de distancia mínima para 230kV a carreteras."""
        distancia = obtener_distancia_minima(
            nivel_tension_kv=230,
            tipo_cruce="carreteras",
            altitud_msnm=0
        )

        # Según RETIE: 8.5 m para 230 kV
        assert abs(distancia - 8.5) < 0.1

    def test_factor_altitud_bajo_1000m(self):
        """No debe haber corrección para altitudes menores a 1000m."""
        factor = calcular_factor_altitud(500, 115)
        assert factor == 1.0

    def test_factor_altitud_bogota(self):
        """Factor de corrección para Bogotá (2600m)."""
        factor = calcular_factor_altitud(2600, 115)

        # Factor = 1 + 0.03 × ((2600 - 1000) / 300) = 1.16
        esperado = 1 + 0.03 * ((2600 - 1000) / 300)
        assert abs(factor - esperado) < 0.01

    def test_factor_altitud_no_aplica_bt(self):
        """No aplica corrección para tensiones bajas."""
        factor = calcular_factor_altitud(2600, 34.5)
        assert factor == 1.0, "No debe haber corrección para 34.5 kV"


class TestIntegracion:
    """Tests de integración entre módulos."""

    def test_flujo_completo_calculo(self):
        """Test del flujo completo de cálculo."""
        # Datos del conductor Hawk
        conductor = {
            'seccion_total_mm2': 241.7,
            'peso_kg_km': 975,
            'diametro_mm': 21.79,
            'carga_rotura_kgf': 11900,
            'modulo_elasticidad_final_kgf_mm2': 7700,
            'coef_dilatacion_1_C': 0.0000193
        }

        # Vanos
        vanos = [280, 320, 300]
        vano_regulador = calcular_vano_regulador(vanos)

        # Cargas
        peso_conductor = conductor['peso_kg_km'] / 1000
        seccion = conductor['seccion_total_mm2']
        g_peso = peso_conductor / seccion

        # Tensión EDS (18% de rotura)
        tension_rotura = conductor['carga_rotura_kgf'] / seccion
        tension_eds = tension_rotura * 0.18

        # Calcular para temperatura máxima
        resultado = resolver_ecuacion_estado(
            sigma_1=tension_eds,
            t_1=20,
            t_2=75,
            g_1=g_peso,
            g_2=g_peso,
            a=vano_regulador,
            E=conductor['modulo_elasticidad_final_kgf_mm2'],
            alpha=conductor['coef_dilatacion_1_C']
        )

        # Verificaciones
        assert resultado['sigma_2'] > 0
        assert resultado['flecha'] > 0
        assert resultado['longitud_conductor'] > vano_regulador

        # Verificar distancia de seguridad
        flecha_max = resultado['flecha']
        altura_soporte = 20
        distancia_requerida = obtener_distancia_minima(115, "terreno", 0)
        distancia_disponible = altura_soporte - flecha_max

        assert distancia_disponible > distancia_requerida, \
            "Distancia de seguridad no cumple"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
