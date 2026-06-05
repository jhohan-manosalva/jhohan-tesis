# Software de Cálculos Mecánicos para Líneas de Alta Tensión

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-Educational-green.svg)]()

Software educativo para realizar cálculos mecánicos en líneas de transmisión eléctrica de alta tensión (34.5 kV a 500 kV), desarrollado como Trabajo de Grado para el programa de Tecnología en Electricidad Industrial de las Unidades Tecnológicas de Santander (UTS), Colombia.

## Características

- **Ecuación de Cambio de Estado**: Solución de la ecuación cúbica mediante métodos de Cardano, Newton-Raphson y Brent
- **Cálculos de Catenaria**: Métodos parabólico y de catenaria exacta
- **Cargas Mecánicas**: Viento, peso propio, hielo (para alta montaña)
- **Hipótesis de Cálculo RETIE**: Las 4 hipótesis obligatorias (A, B, C, D)
- **Verificación de Distancias**: Según Tabla 13.2 del RETIE con corrección por altitud
- **Capacidad Térmica**: Cálculo de ampacity según IEEE 738
- **Generación de Reportes**: Exportación a PDF profesional

## Normativa Aplicable

- RETIE Resolución 40117 de 2024
- NTC 2050 (Código Eléctrico Colombiano)
- IEEE 738-2023 (Capacidad Térmica)
- IEC 60826:2017 (Diseño Mecánico)

## Requisitos del Sistema

- Python 3.10 o superior
- Sistema operativo: Windows, macOS o Linux

## Instalación

1. **Clonar o descargar el repositorio**

```bash
cd calculos_mecanicos_at
```

2. **Crear un entorno virtual (recomendado)**

```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En Linux/macOS
source venv/bin/activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

## Uso

### Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá en su navegador web en `http://localhost:8501`

### Flujo de trabajo

1. **Datos del Conductor**: Seleccione el tipo y calibre del conductor
2. **Condiciones Ambientales**: Configure la zona climática y parámetros de diseño
3. **Cálculo Mecánico**: Ingrese los vanos y ejecute los cálculos
4. **Análisis de Hipótesis**: Evalúe las 4 hipótesis RETIE
5. **Verificación RETIE**: Compruebe las distancias de seguridad
6. **Generar Reporte**: Exporte los resultados en PDF

## Estructura del Proyecto

```
calculos_mecanicos_at/
├── app.py                          # Aplicación principal Streamlit
├── requirements.txt                # Dependencias
├── README.md                       # Este archivo
├── config/
│   ├── conductores.json           # Base de datos de conductores
│   ├── zonas_climaticas.json      # Zonas climáticas de Colombia
│   └── normativa.json             # Parámetros RETIE
├── modules/
│   ├── ecuacion_estado.py         # Ecuación cúbica de cambio de estado
│   ├── catenaria.py               # Cálculos de catenaria y parábola
│   ├── cargas_mecanicas.py        # Cargas de viento, peso, resultante
│   ├── vano_regulador.py          # Vano regulador y crítico
│   ├── hipotesis_calculo.py       # Las 4 hipótesis RETIE
│   ├── distancias_seguridad.py    # Verificación distancias RETIE
│   ├── capacidad_termica.py       # Ampacity IEEE 738
│   └── validaciones.py            # Validaciones normativas
├── utils/
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
│   └── estilos.css                # Estilos personalizados
├── tests/
│   └── test_calculos.py           # Tests unitarios
└── docs/
    └── manual_usuario.md          # Manual de usuario
```

## Conductores Incluidos

La base de datos incluye conductores:

- **ACSR** (Aluminium Conductor Steel Reinforced): Sparrow, Raven, Penguin, Partridge, Linnet, Hawk, Dove, Drake, Cardinal, Bittern, Bluebird, etc.
- **AAAC** (All Aluminium Alloy Conductor): Azusa, Butte, Canton, Darien, Elgin
- **AAC** (All Aluminium Conductor): Poppy, Dahlia, Tulip

## Zonas Climáticas de Colombia

- Costa Caribe General
- La Guajira
- Valles Interandinos
- Altiplano Cundiboyacense
- Antioquia y Eje Cafetero
- Santanderes
- Orinoquía - Llanos
- Amazonía
- Pacífico
- San Andrés y Providencia

## Tests

Ejecutar los tests unitarios:

```bash
pytest tests/test_calculos.py -v
```

## Ejemplos de Uso

### Ecuación de Estado

```python
from modules.ecuacion_estado import resolver_ecuacion_estado

resultado = resolver_ecuacion_estado(
    sigma_1=8.0,      # Tensión inicial (kg/mm²)
    t_1=20,           # Temperatura inicial (°C)
    t_2=75,           # Temperatura final (°C)
    g_1=0.00404,      # Carga específica inicial
    g_2=0.00404,      # Carga específica final
    a=300,            # Vano regulador (m)
    E=7700,           # Módulo de elasticidad
    alpha=0.0000193   # Coef. dilatación
)

print(f"Tensión final: {resultado['sigma_2']:.4f} kg/mm²")
print(f"Flecha: {resultado['flecha']:.2f} m")
```

### Verificación de Distancias

```python
from modules.distancias_seguridad import verificar_distancia_seguridad

resultado = verificar_distancia_seguridad(
    flecha_maxima=8.5,
    altura_soporte=20,
    altura_punto_critico=0,
    nivel_tension_kv=115,
    tipo_cruce="terreno",
    altitud_msnm=1000
)

print(f"Cumple RETIE: {resultado['cumple']}")
```

## Aviso Importante

⚠️ **Este software es de carácter EDUCATIVO** y está diseñado para fines académicos. Los resultados deben ser verificados por un profesional calificado antes de su aplicación en proyectos reales.

## Autor

**Jhohan Felipe Manosalva Sierra**
- Programa: Tecnología en Electricidad Industrial
- Universidad: Unidades Tecnológicas de Santander (UTS)
- Director: Ing. MPE Fabio Alfonso González
- Año: 2025

## Licencia

Este software es de uso educativo. Todos los derechos reservados.

## Referencias

1. RETIE - Resolución 40117 de 2024, Ministerio de Minas y Energía de Colombia
2. NTC 2050: Código Eléctrico Colombiano
3. IEEE Std 738-2023: Standard for Calculating the Current-Temperature Relationship of Bare Overhead Conductors
4. IEC 60826:2017: Design criteria of overhead transmission lines
5. CREG 025 de 1995: Código de Redes
