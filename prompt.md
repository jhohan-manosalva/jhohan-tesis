# PROMPT TÉCNICO PARA DESARROLLO DE SOFTWARE DE CÁLCULOS MECÁNICOS EN LÍNEAS DE ALTA TENSIÓN

## CONTEXTO DEL PROYECTO

Eres un desarrollador experto en Python y Streamlit. Tu tarea es desarrollar un software educativo completo para realizar cálculos mecánicos en líneas de transmisión eléctrica de alta tensión (34.5 kV a 500 kV) para el programa de Tecnología en Electricidad Industrial de las Unidades Tecnológicas de Santander (UTS), Colombia.

Este software debe cumplir estrictamente con la normativa colombiana vigente, principalmente el **RETIE (Resolución 40117 de 2024)** y las **Normas Técnicas Colombianas (NTC)** aplicables, además de incorporar estándares internacionales **IEEE 738** e **IEC 60826** adoptados en Colombia.

---

## ESPECIFICACIONES TÉCNICAS GENERALES

### Stack Tecnológico Obligatorio
- **Lenguaje**: Python 3.10+
- **Framework de interfaz**: Streamlit (última versión estable)
- **Librerías numéricas**: NumPy, SciPy
- **Visualización**: Matplotlib, Plotly
- **Generación de reportes**: ReportLab o FPDF para exportar PDF
- **Manejo de datos**: Pandas
- **Persistencia**: JSON o SQLite para guardar configuraciones y casos

### Estructura del Proyecto
```
calculos_mecanicos_at/
├── app.py                          # Punto de entrada principal Streamlit
├── requirements.txt                # Dependencias del proyecto
├── config/
│   ├── conductores.json           # Base de datos de conductores ACSR/AAAC/AAC
│   ├── zonas_climaticas.json      # Parámetros climáticos por zona colombiana
│   └── normativa.json             # Factores de seguridad y límites RETIE
├── modules/
│   ├── __init__.py
│   ├── ecuacion_estado.py         # Ecuación cúbica de cambio de estado
│   ├── catenaria.py               # Cálculos de catenaria y parábola
│   ├── cargas_mecanicas.py        # Cargas de viento, peso, resultante
│   ├── vano_regulador.py          # Cálculo de vano regulador y crítico
│   ├── hipotesis_calculo.py       # Las 4 hipótesis de diseño RETIE
│   ├── distancias_seguridad.py    # Verificación distancias según RETIE
│   ├── capacidad_termica.py       # Cálculo ampacity según IEEE 738
│   └── validaciones.py            # Validaciones contra normativa
├── utils/
│   ├── __init__.py
│   ├── conversiones.py            # Conversión de unidades
│   ├── exportar_pdf.py            # Generación de reportes
│   └── graficas.py                # Funciones de visualización
├── pages/
│   ├── 01_📊_Datos_Conductor.py
│   ├── 02_🌡️_Condiciones_Ambientales.py
│   ├── 03_📐_Calculo_Mecanico.py
│   ├── 04_📈_Analisis_Hipotesis.py
│   ├── 05_✅_Verificacion_RETIE.py
│   └── 06_📄_Generar_Reporte.py
├── assets/
│   ├── logo_uts.png
│   └── estilos.css
├── tests/
│   └── test_calculos.py           # Tests unitarios
└── docs/
    └── manual_usuario.md          # Documentación de uso
```

---

## MÓDULOS DE CÁLCULO - ESPECIFICACIONES DETALLADAS

### MÓDULO 1: Ecuación de Cambio de Estado (`ecuacion_estado.py`)

#### Fundamento Teórico
La ecuación de cambio de estado relaciona la tensión mecánica de un conductor bajo diferentes condiciones de temperatura y carga. Es la herramienta fundamental para predecir el comportamiento del conductor.

#### Ecuación Principal (Forma Cúbica)
```
σ₂³ - σ₂² × [σ₁ - E×α×(t₂-t₁) + (E×a²×g₁²)/(24×σ₁²)] - (E×a²×g₂²)/24 = 0
```

**Donde:**
- `σ₁` = Tensión unitaria inicial (kg/mm² o daN/mm²)
- `σ₂` = Tensión unitaria final (incógnita)
- `E` = Módulo de elasticidad del conductor (kg/mm²)
- `α` = Coeficiente de dilatación térmica (1/°C)
- `t₁` = Temperatura inicial (°C)
- `t₂` = Temperatura final (°C)
- `a` = Vano o vano regulador (m)
- `g₁` = Carga específica inicial (kg/m/mm²)
- `g₂` = Carga específica final (kg/m/mm²)

#### Implementación Requerida
```python
def resolver_ecuacion_estado(
    sigma_1: float,      # Tensión inicial (kg/mm²)
    t_1: float,          # Temperatura inicial (°C)
    t_2: float,          # Temperatura final (°C)
    g_1: float,          # Carga específica inicial (kg/m/mm²)
    g_2: float,          # Carga específica final (kg/m/mm²)
    a: float,            # Vano regulador (m)
    E: float,            # Módulo de elasticidad (kg/mm²)
    alpha: float,        # Coef. dilatación térmica (1/°C)
    metodo: str = "cardano"  # "cardano", "newton", "brentq"
) -> dict:
    """
    Resuelve la ecuación cúbica de cambio de estado.
    
    Returns:
        dict con:
        - sigma_2: Tensión final calculada
        - flecha: Flecha correspondiente
        - longitud_conductor: Longitud del conductor
        - convergencia: Información del método numérico
    """
```

#### Métodos de Solución a Implementar
1. **Método de Cardano**: Solución analítica de la ecuación cúbica
2. **Método de Newton-Raphson**: Iterativo con convergencia cuadrática
3. **Método de Brent**: Combinación de bisección y secante (scipy.optimize.brentq)

#### Validaciones Obligatorias
- `σ₂` debe ser positiva
- `σ₂` ≤ 50% de la carga de rotura del conductor
- Si `σ₂` < 0 o imaginaria → Error con mensaje explicativo

---

### MÓDULO 2: Cálculos de Catenaria y Parábola (`catenaria.py`)

#### Ecuación de la Catenaria
```
y(x) = c × [cosh(x/c) - 1]

Donde: c = H/w (parámetro catenario)
       H = Tensión horizontal (kg)
       w = Peso unitario (kg/m)
```

#### Flecha Máxima - Catenaria Exacta
```
f = c × [cosh(a/(2×c)) - 1]
```

#### Aproximación Parabólica (válida para f/a < 5%)
```
f = (w × a²) / (8 × H)

Donde:
- f = Flecha máxima (m)
- w = Peso unitario resultante (kg/m)
- a = Longitud del vano (m)
- H = Tensión horizontal = T × cos(θ) ≈ T para ángulos pequeños
```

#### Longitud del Conductor
```
# Aproximación parabólica
L = a × [1 + (8×f²)/(3×a²)]

# Catenaria exacta
L = 2×c × sinh(a/(2×c))
```

#### Funciones a Implementar
```python
def calcular_flecha_parabolica(
    peso_unitario: float,  # kg/m
    vano: float,           # m
    tension_horizontal: float  # kg
) -> float:
    """Calcula flecha usando aproximación parabólica."""

def calcular_flecha_catenaria(
    peso_unitario: float,
    vano: float,
    tension_horizontal: float
) -> float:
    """Calcula flecha usando ecuación exacta de catenaria."""

def calcular_longitud_conductor(
    vano: float,
    flecha: float,
    metodo: str = "parabolica"
) -> float:
    """Calcula longitud real del conductor en el vano."""

def comparar_metodos(
    peso_unitario: float,
    vano: float,
    tension: float
) -> dict:
    """Compara resultados entre método parabólico y catenaria."""

def calcular_curva_catenaria(
    vano: float,
    flecha: float,
    puntos: int = 100
) -> tuple:
    """Retorna arrays (x, y) para graficar la catenaria."""
```

---

### MÓDULO 3: Cargas Mecánicas (`cargas_mecanicas.py`)

#### Peso Propio del Conductor
```
w_c = peso_lineal  # Dato del fabricante (kg/m)
```

#### Carga de Viento sobre el Conductor (RETIE/IEC)
```
p_v = (ρ × V² × Cd × d) / (2 × 1000)  [daN/m o kg/m]

Donde:
- ρ = Densidad del aire (kg/m³)
    ρ = 1.225 × (288.15 / (288.15 + 0.0065×h)) ^ 5.2561
    h = Altura sobre nivel del mar (m)
- V = Velocidad del viento (m/s)
- Cd = Coeficiente de arrastre = 1.0 para conductores cilíndricos
- d = Diámetro del conductor (m)
```

#### Carga de Hielo (cuando aplique)
```
w_h = π × ρ_hielo × e × (d + e) × g / 1000  [kg/m]

Donde:
- ρ_hielo = 900 kg/m³ (densidad del hielo)
- e = Espesor de manguito de hielo (m)
- d = Diámetro del conductor (m)
- g = 9.81 m/s²
```
**Nota**: En Colombia generalmente no se considera carga de hielo excepto en páramos sobre 3,500 msnm.

#### Peso Resultante (Carga Combinada)
```
w_r = √(w_c² + p_v²)  # Sin hielo

w_r = √((w_c + w_h)² + p_v²)  # Con hielo
```

#### Carga Específica (por unidad de sección)
```
g = w / S  [kg/m/mm²]

Donde S = Sección transversal del conductor (mm²)
```

#### Funciones a Implementar
```python
def calcular_densidad_aire(altitud_msnm: float) -> float:
    """Calcula densidad del aire según altitud."""

def calcular_carga_viento(
    velocidad_viento: float,  # m/s
    diametro_conductor: float,  # mm
    altitud_msnm: float = 0,
    coef_arrastre: float = 1.0
) -> float:
    """Calcula carga de viento en kg/m."""

def calcular_carga_hielo(
    diametro_conductor: float,  # mm
    espesor_hielo: float  # mm
) -> float:
    """Calcula carga de hielo en kg/m."""

def calcular_peso_resultante(
    peso_conductor: float,
    carga_viento: float,
    carga_hielo: float = 0
) -> float:
    """Calcula peso resultante combinado."""

def calcular_carga_especifica(
    peso_resultante: float,
    seccion_conductor: float  # mm²
) -> float:
    """Calcula carga específica g."""
```

---

### MÓDULO 4: Vano Regulador y Vano Crítico (`vano_regulador.py`)

#### Vano Regulador (Ruling Span)
El vano regulador es un vano ficticio que representa el comportamiento mecánico de un cantón completo:

```
Lr = √(Σ(Li³) / Σ(Li))

Donde Li = Longitud de cada vano individual del cantón
```

#### Vano Crítico
Determina qué hipótesis de cálculo gobierna el diseño:

```
a_c = √[(24 × E × S × α × ΔT) / ((g₂² - g₁²) × σ_adm)]

Donde:
- E = Módulo de elasticidad
- S = Sección del conductor
- α = Coeficiente de dilatación
- ΔT = Diferencia de temperatura entre hipótesis
- g₁, g₂ = Cargas específicas de las hipótesis comparadas
- σ_adm = Tensión admisible
```

#### Funciones a Implementar
```python
def calcular_vano_regulador(vanos: list[float]) -> float:
    """
    Calcula el vano regulador de un cantón.
    
    Args:
        vanos: Lista de longitudes de vanos en metros
    
    Returns:
        Vano regulador en metros
    """

def calcular_vano_critico(
    E: float,              # Módulo elasticidad (kg/mm²)
    S: float,              # Sección (mm²)
    alpha: float,          # Coef. dilatación (1/°C)
    delta_T: float,        # Diferencia temperatura (°C)
    g_1: float,            # Carga específica hipótesis 1
    g_2: float,            # Carga específica hipótesis 2
    sigma_adm: float       # Tensión admisible (kg/mm²)
) -> float:
    """Calcula el vano crítico."""

def verificar_canton(
    vanos: list[float],
    vano_regulador: float
) -> dict:
    """
    Verifica que el cantón sea válido.
    
    Regla: vano_max ≤ 2.5 × vano_regulador
    """
```

---

### MÓDULO 5: Hipótesis de Cálculo RETIE (`hipotesis_calculo.py`)

#### Las 4 Hipótesis Obligatorias según Normativa Colombiana

##### HIPÓTESIS A: Viento Máximo
- **Temperatura**: Mínima coincidente con viento máximo (típicamente 15°C)
- **Viento**: Velocidad máxima de diseño según zona
- **Límite de tensión**: σ ≤ 50% de la carga de rotura
- **Propósito**: Determinar cargas máximas sobre estructuras

##### HIPÓTESIS B: Temperatura Mínima
- **Temperatura**: Mínima absoluta de la zona (5°C a 18°C según ubicación)
- **Viento**: Sin viento (0 m/s)
- **Límite de tensión**: σ ≤ 33-35% de la carga de rotura
- **Propósito**: Verificar tensión máxima por contracción térmica

##### HIPÓTESIS C: Condición EDS (Every Day Stress)
- **Temperatura**: Media anual (típicamente 20°C)
- **Viento**: Sin viento
- **Límite de tensión**: σ = 15-18% de la carga de rotura
- **Propósito**: Tensión de operación diaria, prevención de fatiga

##### HIPÓTESIS D: Flecha Máxima (Temperatura Máxima)
- **Temperatura**: Máxima del conductor en operación (75°C normal, 100°C emergencia)
- **Viento**: Sin viento
- **Propósito**: Verificar distancias de seguridad al terreno

#### Implementación Requerida
```python
from dataclasses import dataclass
from enum import Enum

class TipoHipotesis(Enum):
    VIENTO_MAXIMO = "A"
    TEMPERATURA_MINIMA = "B"
    EDS = "C"
    FLECHA_MAXIMA = "D"

@dataclass
class ResultadoHipotesis:
    tipo: TipoHipotesis
    temperatura: float
    velocidad_viento: float
    carga_viento: float
    peso_resultante: float
    carga_especifica: float
    tension_calculada: float
    tension_limite: float
    flecha: float
    cumple_limite: bool
    factor_utilizacion: float  # tension_calculada / tension_limite

def calcular_hipotesis_A(
    conductor: dict,
    vano_regulador: float,
    condiciones_iniciales: dict,
    zona_climatica: dict
) -> ResultadoHipotesis:
    """Calcula hipótesis de viento máximo."""

def calcular_hipotesis_B(
    conductor: dict,
    vano_regulador: float,
    condiciones_iniciales: dict,
    zona_climatica: dict
) -> ResultadoHipotesis:
    """Calcula hipótesis de temperatura mínima."""

def calcular_hipotesis_C(
    conductor: dict,
    vano_regulador: float,
    tension_eds_porcentaje: float = 18.0
) -> ResultadoHipotesis:
    """Calcula condición EDS."""

def calcular_hipotesis_D(
    conductor: dict,
    vano_regulador: float,
    condiciones_iniciales: dict,
    temperatura_operacion: float = 75.0
) -> ResultadoHipotesis:
    """Calcula hipótesis de flecha máxima."""

def analizar_todas_hipotesis(
    conductor: dict,
    vano_regulador: float,
    zona_climatica: dict,
    tension_eds: float = 18.0
) -> dict[TipoHipotesis, ResultadoHipotesis]:
    """Ejecuta análisis completo de las 4 hipótesis."""
```

---

### MÓDULO 6: Distancias de Seguridad RETIE (`distancias_seguridad.py`)

#### Tabla de Distancias Mínimas según RETIE (Artículo 13, Tabla 13.2)

| Nivel de Tensión | Al terreno (m) | A edificaciones (m) | Cruce carreteras (m) |
|-----------------|----------------|---------------------|---------------------|
| 34.5 kV         | 5.0            | 3.7                 | 6.1                 |
| 57.5 kV         | 5.0            | 3.7                 | 6.1                 |
| 115 kV          | 5.5            | 4.0                 | 6.7                 |
| 230 kV          | 6.5            | 4.5                 | 8.5                 |
| 500 kV          | 9.0            | 6.5                 | 11.5                |

#### Factor de Corrección por Altitud
```
Para tensiones > 57.5 kV y altitudes > 1,000 msnm:
Factor = 1 + 0.03 × [(altitud - 1000) / 300]

Distancia_corregida = Distancia_base × Factor
```

#### Funciones a Implementar
```python
def obtener_distancia_minima(
    nivel_tension_kv: float,
    tipo_cruce: str,  # "terreno", "edificacion", "carretera", "ferrocarril", "linea_bt", "linea_at"
    altitud_msnm: float = 0
) -> float:
    """
    Obtiene la distancia mínima de seguridad según RETIE.
    Aplica corrección por altitud si corresponde.
    """

def verificar_distancia_seguridad(
    flecha_maxima: float,
    altura_soporte: float,
    altura_punto_critico: float,
    nivel_tension_kv: float,
    tipo_cruce: str,
    altitud_msnm: float = 0
) -> dict:
    """
    Verifica si se cumple la distancia de seguridad.
    
    Returns:
        dict con:
        - distancia_disponible: altura_soporte - flecha_maxima - altura_punto_critico
        - distancia_requerida: distancia mínima RETIE
        - cumple: bool
        - margen: distancia_disponible - distancia_requerida
    """

def calcular_altura_minima_soporte(
    flecha_maxima: float,
    altura_punto_critico: float,
    nivel_tension_kv: float,
    tipo_cruce: str,
    altitud_msnm: float = 0,
    margen_seguridad: float = 0.5  # metros adicionales
) -> float:
    """Calcula la altura mínima requerida del soporte."""
```

---

### MÓDULO 7: Capacidad Térmica IEEE 738 (`capacidad_termica.py`)

#### Balance Térmico del Conductor
```
q_c + q_r = q_s + I² × R(Tc)

Donde:
- q_c = Pérdidas por convección (W/m)
- q_r = Pérdidas por radiación (W/m)
- q_s = Ganancia por radiación solar (W/m)
- I²R = Calentamiento resistivo (W/m)
```

#### Corriente Máxima (Ampacity)
```
I_max = √[(q_c + q_r - q_s) / R(Tc)]
```

#### Pérdidas por Convección (Convección Forzada)
```
q_c = K_angle × [1.01 + 1.35 × N_Re^0.52] × k_f × (Tc - Ta)

Donde:
- K_angle = Factor de ángulo de incidencia del viento
- N_Re = Número de Reynolds = (D × V_w × ρ_f) / μ_f
- k_f = Conductividad térmica del aire
- Tc = Temperatura del conductor
- Ta = Temperatura ambiente
```

#### Funciones a Implementar
```python
def calcular_ampacity(
    diametro_conductor: float,      # mm
    resistencia_ac: float,          # Ω/km a temperatura de referencia
    temperatura_conductor: float,   # °C
    temperatura_ambiente: float,    # °C
    velocidad_viento: float,        # m/s
    altitud_msnm: float,
    angulo_viento: float = 90,      # grados respecto al conductor
    emisividad: float = 0.5,
    absortividad: float = 0.5,
    radiacion_solar: float = 1000   # W/m²
) -> dict:
    """
    Calcula la capacidad de corriente según IEEE 738.
    
    Returns:
        dict con:
        - ampacity: Corriente máxima (A)
        - perdidas_conveccion: W/m
        - perdidas_radiacion: W/m
        - ganancia_solar: W/m
    """

def calcular_temperatura_conductor(
    corriente: float,               # A
    diametro_conductor: float,      # mm
    resistencia_ac: float,          # Ω/km
    temperatura_ambiente: float,    # °C
    velocidad_viento: float,        # m/s
    altitud_msnm: float
) -> float:
    """Calcula temperatura del conductor para una corriente dada."""
```

---

## BASE DE DATOS DE CONDUCTORES (`config/conductores.json`)

### Estructura del JSON
```json
{
  "ACSR": {
    "Sparrow": {
      "codigo_bird": "Sparrow",
      "calibre_awg_kcmil": "2 AWG",
      "seccion_total_mm2": 21.15,
      "seccion_aluminio_mm2": 13.30,
      "seccion_acero_mm2": 7.85,
      "diametro_mm": 6.35,
      "peso_kg_km": 97.0,
      "carga_rotura_kgf": 2850,
      "modulo_elasticidad_final_kgf_mm2": 7700,
      "modulo_elasticidad_inicial_kgf_mm2": 8100,
      "coef_dilatacion_1_C": 0.0000193,
      "resistencia_dc_20C_ohm_km": 1.365,
      "resistencia_ac_75C_ohm_km": 1.755,
      "ampacidad_75C_A": 180,
      "aplicacion_tipica": "Distribución rural 13.2kV"
    },
    "Penguin": {
      "codigo_bird": "Penguin",
      "calibre_awg_kcmil": "4/0 AWG",
      "seccion_total_mm2": 125.1,
      "seccion_aluminio_mm2": 107.2,
      "seccion_acero_mm2": 17.9,
      "diametro_mm": 14.31,
      "peso_kg_km": 433,
      "carga_rotura_kgf": 5180,
      "modulo_elasticidad_final_kgf_mm2": 7400,
      "modulo_elasticidad_inicial_kgf_mm2": 7800,
      "coef_dilatacion_1_C": 0.0000193,
      "resistencia_dc_20C_ohm_km": 0.2712,
      "resistencia_ac_75C_ohm_km": 0.3494,
      "ampacidad_75C_A": 340,
      "aplicacion_tipica": "Subtransmisión 34.5kV"
    },
    "Partridge": {
      "codigo_bird": "Partridge",
      "calibre_awg_kcmil": "266.8 kcmil",
      "seccion_total_mm2": 135.2,
      "seccion_aluminio_mm2": 135.2,
      "seccion_acero_mm2": 22.0,
      "diametro_mm": 16.28,
      "peso_kg_km": 546,
      "carga_rotura_kgf": 6400,
      "modulo_elasticidad_final_kgf_mm2": 7600,
      "modulo_elasticidad_inicial_kgf_mm2": 8000,
      "coef_dilatacion_1_C": 0.0000193,
      "resistencia_dc_20C_ohm_km": 0.2141,
      "resistencia_ac_75C_ohm_km": 0.2760,
      "ampacidad_75C_A": 400,
      "aplicacion_tipica": "Transmisión 115kV"
    },
    "Linnet": {
      "codigo_bird": "Linnet",
      "calibre_awg_kcmil": "336.4 kcmil",
      "seccion_total_mm2": 170.5,
      "seccion_aluminio_mm2": 170.5,
      "seccion_acero_mm2": 22.0,
      "diametro_mm": 18.31,
      "peso_kg_km": 621,
      "carga_rotura_kgf": 7500,
      "modulo_elasticidad_final_kgf_mm2": 7200,
      "modulo_elasticidad_inicial_kgf_mm2": 7600,
      "coef_dilatacion_1_C": 0.0000193,
      "resistencia_dc_20C_ohm_km": 0.1699,
      "resistencia_ac_75C_ohm_km": 0.2190,
      "ampacidad_75C_A": 460,
      "aplicacion_tipica": "Transmisión 115kV"
    },
    "Hawk": {
      "codigo_bird": "Hawk",
      "calibre_awg_kcmil": "477 kcmil",
      "seccion_total_mm2": 241.7,
      "seccion_aluminio_mm2": 241.7,
      "seccion_acero_mm2": 39.5,
      "diametro_mm": 21.79,
      "peso_kg_km": 975,
      "carga_rotura_kgf": 11900,
      "modulo_elasticidad_final_kgf_mm2": 7700,
      "modulo_elasticidad_inicial_kgf_mm2": 8100,
      "coef_dilatacion_1_C": 0.0000193,
      "resistencia_dc_20C_ohm_km": 0.1198,
      "resistencia_ac_75C_ohm_km": 0.1546,
      "ampacidad_75C_A": 570,
      "aplicacion_tipica": "Transmisión 115-230kV"
    },
    "Drake": {
      "codigo_bird": "Drake",
      "calibre_awg_kcmil": "795 kcmil",
      "seccion_total_mm2": 403.0,
      "seccion_aluminio_mm2": 403.0,
      "seccion_acero_mm2": 65.6,
      "diametro_mm": 28.14,
      "peso_kg_km": 1628,
      "carga_rotura_kgf": 14400,
      "modulo_elasticidad_final_kgf_mm2": 7700,
      "modulo_elasticidad_inicial_kgf_mm2": 8100,
      "coef_dilatacion_1_C": 0.0000193,
      "resistencia_dc_20C_ohm_km": 0.0718,
      "resistencia_ac_75C_ohm_km": 0.0928,
      "ampacidad_75C_A": 750,
      "aplicacion_tipica": "Transmisión 230-500kV"
    },
    "Bluebird": {
      "codigo_bird": "Bluebird",
      "calibre_awg_kcmil": "2156 kcmil",
      "seccion_total_mm2": 1092.0,
      "seccion_aluminio_mm2": 1092.0,
      "seccion_acero_mm2": 178.0,
      "diametro_mm": 46.33,
      "peso_kg_km": 4410,
      "carga_rotura_kgf": 35200,
      "modulo_elasticidad_final_kgf_mm2": 7700,
      "modulo_elasticidad_inicial_kgf_mm2": 8100,
      "coef_dilatacion_1_C": 0.0000193,
      "resistencia_dc_20C_ohm_km": 0.0265,
      "resistencia_ac_75C_ohm_km": 0.0343,
      "ampacidad_75C_A": 1200,
      "aplicacion_tipica": "Transmisión 500kV (haz)"
    }
  }
}
```

---

## ZONAS CLIMÁTICAS COLOMBIA (`config/zonas_climaticas.json`)

```json
{
  "zonas": {
    "costa_caribe_general": {
      "nombre": "Costa Caribe - General",
      "departamentos": ["Atlántico", "Bolívar", "Cesar", "Córdoba", "Magdalena", "Sucre"],
      "altitud_referencia_msnm": 50,
      "temperatura_minima_C": 22,
      "temperatura_media_C": 28,
      "temperatura_maxima_ambiente_C": 38,
      "velocidad_viento_diseno_km_h": 100,
      "velocidad_viento_diseno_m_s": 27.8,
      "humedad_relativa_media_pct": 80,
      "zona_retie": "Cálido Húmedo"
    },
    "la_guajira": {
      "nombre": "La Guajira",
      "departamentos": ["La Guajira"],
      "altitud_referencia_msnm": 20,
      "temperatura_minima_C": 24,
      "temperatura_media_C": 30,
      "temperatura_maxima_ambiente_C": 40,
      "velocidad_viento_diseno_km_h": 162,
      "velocidad_viento_diseno_m_s": 45.0,
      "humedad_relativa_media_pct": 65,
      "zona_retie": "Cálido Seco - Viento Extremo"
    },
    "valles_interandinos": {
      "nombre": "Valles Interandinos",
      "departamentos": ["Valle del Cauca", "Huila", "Tolima"],
      "altitud_referencia_msnm": 1000,
      "temperatura_minima_C": 18,
      "temperatura_media_C": 24,
      "temperatura_maxima_ambiente_C": 35,
      "velocidad_viento_diseno_km_h": 80,
      "velocidad_viento_diseno_m_s": 22.2,
      "humedad_relativa_media_pct": 70,
      "zona_retie": "Templado Seco"
    },
    "altiplano_cundiboyacense": {
      "nombre": "Altiplano Cundiboyacense",
      "departamentos": ["Cundinamarca", "Boyacá"],
      "altitud_referencia_msnm": 2600,
      "temperatura_minima_C": 5,
      "temperatura_media_C": 14,
      "temperatura_maxima_ambiente_C": 25,
      "velocidad_viento_diseno_km_h": 90,
      "velocidad_viento_diseno_m_s": 25.0,
      "humedad_relativa_media_pct": 75,
      "zona_retie": "Frío"
    },
    "antioquia_eje_cafetero": {
      "nombre": "Antioquia y Eje Cafetero",
      "departamentos": ["Antioquia", "Caldas", "Risaralda", "Quindío"],
      "altitud_referencia_msnm": 1500,
      "temperatura_minima_C": 12,
      "temperatura_media_C": 20,
      "temperatura_maxima_ambiente_C": 30,
      "velocidad_viento_diseno_km_h": 85,
      "velocidad_viento_diseno_m_s": 23.6,
      "humedad_relativa_media_pct": 78,
      "zona_retie": "Templado Húmedo"
    },
    "santanderes": {
      "nombre": "Santanderes",
      "departamentos": ["Santander", "Norte de Santander"],
      "altitud_referencia_msnm": 1000,
      "temperatura_minima_C": 12,
      "temperatura_media_C": 23,
      "temperatura_maxima_ambiente_C": 34,
      "velocidad_viento_diseno_km_h": 90,
      "velocidad_viento_diseno_m_s": 25.0,
      "humedad_relativa_media_pct": 72,
      "zona_retie": "Templado"
    },
    "orinoquia_llanos": {
      "nombre": "Orinoquía - Llanos Orientales",
      "departamentos": ["Meta", "Casanare", "Arauca", "Vichada"],
      "altitud_referencia_msnm": 300,
      "temperatura_minima_C": 20,
      "temperatura_media_C": 27,
      "temperatura_maxima_ambiente_C": 38,
      "velocidad_viento_diseno_km_h": 90,
      "velocidad_viento_diseno_m_s": 25.0,
      "humedad_relativa_media_pct": 75,
      "zona_retie": "Cálido Húmedo"
    },
    "amazonia": {
      "nombre": "Amazonía",
      "departamentos": ["Amazonas", "Caquetá", "Putumayo", "Guaviare", "Vaupés", "Guainía"],
      "altitud_referencia_msnm": 200,
      "temperatura_minima_C": 22,
      "temperatura_media_C": 26,
      "temperatura_maxima_ambiente_C": 35,
      "velocidad_viento_diseno_km_h": 70,
      "velocidad_viento_diseno_m_s": 19.4,
      "humedad_relativa_media_pct": 85,
      "zona_retie": "Cálido Húmedo"
    },
    "pacifico": {
      "nombre": "Pacífico",
      "departamentos": ["Chocó", "Cauca (costa)", "Nariño (costa)"],
      "altitud_referencia_msnm": 50,
      "temperatura_minima_C": 22,
      "temperatura_media_C": 26,
      "temperatura_maxima_ambiente_C": 34,
      "velocidad_viento_diseno_km_h": 80,
      "velocidad_viento_diseno_m_s": 22.2,
      "humedad_relativa_media_pct": 90,
      "zona_retie": "Cálido Húmedo"
    },
    "san_andres_providencia": {
      "nombre": "San Andrés y Providencia",
      "departamentos": ["San Andrés y Providencia"],
      "altitud_referencia_msnm": 10,
      "temperatura_minima_C": 25,
      "temperatura_media_C": 28,
      "temperatura_maxima_ambiente_C": 35,
      "velocidad_viento_diseno_km_h": 180,
      "velocidad_viento_diseno_m_s": 50.0,
      "humedad_relativa_media_pct": 82,
      "zona_retie": "Cálido Húmedo - Zona Huracanes"
    }
  }
}
```

---

## INTERFAZ STREAMLIT - ESPECIFICACIONES DE DISEÑO

### Página Principal (`app.py`)

```python
import streamlit as st

# Configuración de página
st.set_page_config(
    page_title="Cálculos Mecánicos AT - UTS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar con información del proyecto
with st.sidebar:
    st.image("assets/logo_uts.png", width=200)
    st.title("Cálculos Mecánicos en Alta Tensión")
    st.markdown("""
    **Trabajo de Grado**  
    Tecnología en Electricidad Industrial  
    Unidades Tecnológicas de Santander
    
    ---
    **Autor:** Jhohan Felipe Manosalva Sierra  
    **Director:** Ing. MPE Fabio Alfonso González  
    **Año:** 2025
    """)
    
    st.markdown("---")
    st.markdown("### Normativa Aplicable")
    st.markdown("""
    - RETIE Res. 40117/2024
    - NTC 2050 (Código Eléctrico)
    - IEEE 738 (Capacidad Térmica)
    - IEC 60826 (Diseño Mecánico)
    """)

# Contenido principal
st.title("🔌 Software de Cálculos Mecánicos para Líneas de Alta Tensión")
st.markdown("""
Este software permite realizar los cálculos mecánicos requeridos para el diseño 
de líneas de transmisión eléctrica de 34.5 kV a 500 kV, cumpliendo con la 
normativa colombiana vigente (RETIE) y estándares internacionales.
""")

# Tarjetas de navegación
col1, col2, col3 = st.columns(3)
with col1:
    st.info("### 📊 Datos del Conductor\nSeleccione el tipo de conductor y sus características")
with col2:
    st.info("### 🌡️ Condiciones Ambientales\nDefina la zona climática y parámetros de diseño")
with col3:
    st.info("### 📐 Cálculo Mecánico\nEjecute los cálculos de tensión, flecha y cargas")

col4, col5, col6 = st.columns(3)
with col4:
    st.success("### 📈 Análisis de Hipótesis\nEvalúe las 4 hipótesis de cálculo RETIE")
with col5:
    st.success("### ✅ Verificación RETIE\nCompruebe cumplimiento de distancias de seguridad")
with col6:
    st.success("### 📄 Generar Reporte\nExporte resultados en formato PDF")
```

### Página de Datos del Conductor (`pages/01_📊_Datos_Conductor.py`)

Debe incluir:
- Selector de tipo de conductor (ACSR, AAAC, AAC)
- Selector de calibre con nombres comerciales (código bird)
- Visualización de propiedades del conductor seleccionado
- Opción de ingresar conductor personalizado
- Tabla comparativa de conductores disponibles

### Página de Condiciones Ambientales (`pages/02_🌡️_Condiciones_Ambientales.py`)

Debe incluir:
- Mapa interactivo de Colombia para seleccionar zona (opcional con folium)
- Selector de zona climática predefinida
- Campos editables para:
  - Altitud (msnm)
  - Temperatura mínima, media, máxima
  - Velocidad de viento de diseño
- Cálculo automático de densidad del aire
- Visualización de factor de corrección por altitud

### Página de Cálculo Mecánico (`pages/03_📐_Calculo_Mecanico.py`)

Debe incluir:
- Input de vanos (individual o lista para cantón)
- Cálculo automático de vano regulador
- Selector de hipótesis inicial (EDS recomendado)
- Botón de cálculo con barra de progreso
- Resultados en formato de tarjetas:
  - Tensión del conductor (kg, kg/mm², % carga rotura)
  - Flecha (m)
  - Longitud del conductor (m)
- Gráfica de la catenaria/parábola
- Tabla de resultados por vano

### Página de Análisis de Hipótesis (`pages/04_📈_Analisis_Hipotesis.py`)

Debe incluir:
- Ejecución automática de las 4 hipótesis
- Tabla comparativa de resultados
- Gráfico de barras comparando tensiones
- Gráfico de barras comparando flechas
- Indicadores visuales de cumplimiento (✅/❌)
- Identificación de hipótesis crítica
- Análisis del vano crítico

### Página de Verificación RETIE (`pages/05_✅_Verificacion_RETIE.py`)

Debe incluir:
- Selector de nivel de tensión
- Selector de tipo de cruce
- Input de altura del soporte
- Input de altura del obstáculo
- Cálculo de distancia disponible
- Comparación con distancia requerida RETIE
- Indicador de cumplimiento con margen
- Recomendación de altura mínima de soporte

### Página de Generación de Reporte (`pages/06_📄_Generar_Reporte.py`)

Debe generar un PDF con:
- Encabezado con logo UTS
- Datos del proyecto
- Resumen de conductor seleccionado
- Condiciones ambientales de diseño
- Tabla de vanos y vano regulador
- Resultados de las 4 hipótesis con gráficos
- Verificación de distancias de seguridad
- Conclusiones y recomendaciones
- Pie de página con referencia normativa
- Botón de descarga del PDF

---

## VALIDACIONES Y MENSAJES DE ERROR

### Validaciones Obligatorias

```python
# Validación de tensión máxima
def validar_tension_maxima(tension_calculada, carga_rotura, limite_porcentaje=50):
    tension_limite = carga_rotura * limite_porcentaje / 100
    if tension_calculada > tension_limite:
        raise ValueError(
            f"⚠️ ALERTA: La tensión calculada ({tension_calculada:.2f} kg) "
            f"excede el {limite_porcentaje}% de la carga de rotura ({tension_limite:.2f} kg). "
            f"Según RETIE Art. 22, esto no es permitido."
        )

# Validación de flecha vs distancia de seguridad
def validar_distancia_seguridad(flecha, altura_soporte, distancia_minima, tipo_cruce):
    distancia_disponible = altura_soporte - flecha
    if distancia_disponible < distancia_minima:
        raise ValueError(
            f"⚠️ INCUMPLIMIENTO RETIE: La distancia al {tipo_cruce} es "
            f"{distancia_disponible:.2f} m, menor que el mínimo requerido de "
            f"{distancia_minima:.2f} m según Tabla 13.2 del RETIE."
        )

# Validación de vano regulador
def validar_canton(vanos, vano_regulador):
    vano_max = max(vanos)
    if vano_max > 2.5 * vano_regulador:
        st.warning(
            f"⚠️ El vano máximo ({vano_max} m) excede 2.5 veces el vano regulador "
            f"({vano_regulador:.2f} m). Se recomienda revisar la configuración del cantón."
        )
```

---

## TESTS UNITARIOS (`tests/test_calculos.py`)

```python
import pytest
import numpy as np
from modules.ecuacion_estado import resolver_ecuacion_estado
from modules.catenaria import calcular_flecha_parabolica, calcular_flecha_catenaria
from modules.cargas_mecanicas import calcular_carga_viento

class TestEcuacionEstado:
    """Tests para el módulo de ecuación de cambio de estado."""
    
    def test_caso_basico_hawk(self):
        """Test con conductor Hawk, caso típico de transmisión."""
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
        assert resultado['sigma_2'] < 8.0
        # La flecha debe aumentar
        assert resultado['flecha'] > 0

    def test_tension_no_excede_limite(self):
        """La tensión calculada no debe exceder el 50% de rotura."""
        resultado = resolver_ecuacion_estado(
            sigma_1=25.0,     # Alta tensión inicial
            t_1=20,
            t_2=-5,           # Temperatura muy baja
            g_1=0.00404,
            g_2=0.007,        # Con viento
            a=400,
            E=7700,
            alpha=0.0000193
        )
        # Para Hawk, carga rotura = 11900 kg, sección = 241.7 mm²
        # Tensión rotura unitaria = 11900/241.7 = 49.2 kg/mm²
        # Límite 50% = 24.6 kg/mm²
        assert resultado['sigma_2'] <= 49.2 * 0.5


class TestCatenaria:
    """Tests para cálculos de flecha."""
    
    def test_flecha_parabolica_vs_catenaria(self):
        """Para vanos cortos, parábola y catenaria deben ser similares."""
        flecha_par = calcular_flecha_parabolica(
            peso_unitario=0.975,  # kg/m
            vano=200,             # m
            tension_horizontal=2000  # kg
        )
        flecha_cat = calcular_flecha_catenaria(
            peso_unitario=0.975,
            vano=200,
            tension_horizontal=2000
        )
        # Diferencia menor al 1% para vanos de 200m
        assert abs(flecha_par - flecha_cat) / flecha_cat < 0.01


class TestCargasViento:
    """Tests para cálculos de carga de viento."""
    
    def test_carga_viento_nivel_mar(self):
        """Carga de viento a nivel del mar."""
        carga = calcular_carga_viento(
            velocidad_viento=27.8,  # m/s (100 km/h)
            diametro_conductor=21.79,  # mm (Hawk)
            altitud_msnm=0
        )
        # Valor esperado aproximado: 1.03 kg/m
        assert 0.9 < carga < 1.2
    
    def test_carga_viento_altitud(self):
        """Carga de viento debe reducirse con altitud."""
        carga_0m = calcular_carga_viento(27.8, 21.79, 0)
        carga_2600m = calcular_carga_viento(27.8, 21.79, 2600)
        # A mayor altitud, menor densidad, menor carga
        assert carga_2600m < carga_0m
```

---

## REQUISITOS DE DOCUMENTACIÓN

### Manual de Usuario (`docs/manual_usuario.md`)

El manual debe incluir:

1. **Introducción**
   - Propósito del software
   - Alcance (niveles de tensión, tipos de conductores)
   - Requisitos del sistema

2. **Instalación**
   - Requisitos previos (Python 3.10+)
   - Pasos de instalación
   - Ejecución del programa

3. **Guía de Uso**
   - Paso a paso con capturas de pantalla
   - Descripción de cada módulo
   - Ejemplos prácticos

4. **Fundamentos Teóricos**
   - Explicación de cada ecuación
   - Hipótesis de cálculo
   - Referencias normativas

5. **Casos de Ejemplo**
   - Caso 1: Línea 115 kV en zona Santanderes
   - Caso 2: Línea 230 kV en Costa Caribe
   - Caso 3: Línea 34.5 kV en zona Andina

6. **Solución de Problemas**
   - Errores comunes y soluciones
   - FAQ

7. **Referencias**
   - RETIE Resolución 40117 de 2024
   - NTC 2050
   - IEEE 738-2023
   - IEC 60826:2017

---

## ENTREGABLES ESPERADOS

1. **Código fuente completo** con estructura especificada
2. **Archivo requirements.txt** con todas las dependencias
3. **Bases de datos JSON** de conductores y zonas climáticas
4. **Tests unitarios** con cobertura mínima del 80%
5. **Manual de usuario** en formato Markdown
6. **README.md** con instrucciones de instalación y uso rápido

---

## CRITERIOS DE CALIDAD

- Código documentado con docstrings en español
- Comentarios explicativos en secciones complejas
- Manejo de excepciones con mensajes claros
- Interfaz responsive y amigable
- Tiempos de cálculo menores a 2 segundos
- Validación de entradas del usuario
- Resultados verificables contra cálculos manuales

---

## REFERENCIAS NORMATIVAS OBLIGATORIAS

1. **RETIE - Resolución 40117 de 2024**, Ministerio de Minas y Energía de Colombia
   - Artículo 13: Distancias de seguridad
   - Artículo 22: Líneas de transmisión

2. **NTC 2050**: Código Eléctrico Colombiano (basado en NFPA 70)

3. **IEEE Std 738-2023**: Standard for Calculating the Current-Temperature Relationship of Bare Overhead Conductors

4. **IEC 60826:2017**: Design criteria of overhead transmission lines

5. **CREG 025 de 1995**: Código de Redes

6. **NSR-10**: Reglamento Colombiano de Construcción Sismo Resistente (para velocidades de viento)

---

## NOTAS ADICIONALES

- El software es de carácter **educativo** y los resultados deben ser verificados por un profesional para proyectos reales.
- Incluir advertencia visible en la interfaz sobre este carácter educativo.
- Los cálculos deben poder reproducirse manualmente para fines didácticos.
- Priorizar la claridad pedagógica sobre la optimización del código.