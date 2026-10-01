# Manual de Usuario

## Software de Cálculos Mecánicos para Líneas de Alta Tensión

**Versión 1.0**
**Unidades Tecnológicas de Santander**

---

## Tabla de Contenidos

1. [Introducción](#1-introducción)
2. [Instalación](#2-instalación)
3. [Guía de Uso](#3-guía-de-uso)
4. [Fundamentos Teóricos](#4-fundamentos-teóricos)
5. [Casos de Ejemplo](#5-casos-de-ejemplo)
6. [Solución de Problemas](#6-solución-de-problemas)
7. [Referencias](#7-referencias)

---

## 1. Introducción

### 1.1 Propósito

Este software educativo permite realizar los cálculos mecánicos requeridos para el diseño de líneas de transmisión eléctrica de alta tensión, cumpliendo con la normativa colombiana vigente (RETIE) y estándares internacionales.

### 1.2 Alcance

- **Niveles de tensión**: 34.5 kV a 500 kV
- **Tipos de conductores**: ACSR, AAAC, AAC
- **Cálculos incluidos**:
  - Ecuación de cambio de estado
  - Flechas y longitudes de conductor
  - Cargas mecánicas (viento, peso, hielo)
  - Vano regulador y vano crítico
  - Hipótesis de cálculo RETIE
  - Verificación de distancias de seguridad
  - Capacidad térmica (ampacity)

### 1.3 Requisitos del Sistema

- **Sistema Operativo**: Windows 10/11, macOS 10.14+, o Linux
- **Python**: Versión 3.10 o superior
- **Memoria RAM**: Mínimo 4 GB (recomendado 8 GB)
- **Espacio en disco**: 500 MB
- **Navegador web**: Chrome, Firefox, Edge o Safari (última versión)

---

## 2. Instalación

### 2.1 Requisitos Previos

1. **Instalar Python 3.10 o superior**
   - Descargar desde: https://www.python.org/downloads/
   - Durante la instalación, marcar "Add Python to PATH"

2. **Verificar la instalación**
   ```bash
   python --version
   pip --version
   ```

### 2.2 Pasos de Instalación

1. **Descargar el software**
   - Copie la carpeta `calculos_mecanicos_at` a su computador

2. **Abrir terminal/consola**
   - Windows: Buscar "cmd" o "PowerShell"
   - macOS/Linux: Abrir Terminal

3. **Navegar al directorio del proyecto**
   ```bash
   cd ruta/a/calculos_mecanicos_at
   ```

4. **Crear entorno virtual (opcional pero recomendado)**
   ```bash
   python -m venv venv

   # Activar en Windows:
   venv\Scripts\activate

   # Activar en macOS/Linux:
   source venv/bin/activate
   ```

5. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

### 2.3 Ejecución del Programa

```bash
streamlit run app.py
```

El programa se abrirá automáticamente en su navegador web predeterminado en la dirección: `http://localhost:8501`

---

## 3. Guía de Uso

### 3.1 Pantalla Principal

Al iniciar el software, verá la pantalla principal con:
- Información del proyecto
- Navegación a los diferentes módulos
- Advertencia sobre el carácter educativo del software

### 3.2 Módulo 1: Datos del Conductor

**Objetivo**: Seleccionar el conductor para el diseño

**Pasos**:
1. Seleccione el **tipo de conductor** (ACSR, AAAC, AAC)
2. Seleccione el **calibre/código** del conductor
3. Revise las propiedades mostradas:
   - Sección transversal
   - Diámetro
   - Peso por kilómetro
   - Carga de rotura
   - Módulo de elasticidad
   - Coeficiente de dilatación

**Conductor personalizado**:
- Si su conductor no está en la base de datos, expanda "Ingresar Conductor Personalizado"
- Complete todos los campos requeridos
- Presione "Usar Conductor Personalizado"

### 3.3 Módulo 2: Condiciones Ambientales

**Objetivo**: Configurar las condiciones climáticas del proyecto

**Pasos**:
1. Seleccione la **zona climática** de Colombia
2. Ajuste la **altitud** específica del proyecto
3. Verifique y ajuste las **temperaturas**:
   - Mínima (para Hipótesis B)
   - Media (para condición EDS)
   - Máxima ambiente
4. Ajuste la **velocidad de viento de diseño**
5. Configure la **temperatura de operación** del conductor
6. Ajuste el **porcentaje EDS** (típico: 18%)

**Nota sobre corrección por altitud**:
- Para tensiones > 57.5 kV y altitudes > 1000 msnm
- El sistema aplica automáticamente el factor de corrección

### 3.4 Módulo 3: Cálculo Mecánico

**Objetivo**: Calcular tensiones, flechas y cargas

**Pasos**:
1. **Configurar vanos**:
   - Modo "Vano único": Ingrese una sola longitud
   - Modo "Múltiples vanos": Ingrese los vanos separados por comas
2. Verifique el **vano regulador** calculado
3. Configure los **parámetros de cálculo**:
   - Temperatura inicial y final
   - Incluir o no carga de viento
   - Método de solución (Cardano, Newton, Brent)
4. Presione **"Calcular"**

**Interpretación de resultados**:
- **Tensión unitaria final**: En kg/mm²
- **Tensión total**: En kg (multiplicar por sección)
- **% Carga de rotura**: Debe ser ≤ 50% para Hipótesis A
- **Flecha máxima**: En metros
- **Longitud del conductor**: Mayor que el vano

### 3.5 Módulo 4: Análisis de Hipótesis

**Objetivo**: Evaluar las 4 hipótesis de cálculo RETIE

**Hipótesis calculadas**:

| Hipótesis | Condición | Límite |
|-----------|-----------|--------|
| A | Viento máximo + Temp. coincidente | σ ≤ 50% rotura |
| B | Temperatura mínima sin viento | σ ≤ 35% rotura |
| C | EDS - Temperatura media | σ = 15-18% rotura |
| D | Temperatura máxima operación | Verificar distancias |

**Pasos**:
1. Ajuste el **porcentaje EDS** si es necesario
2. Ajuste la **temperatura de operación**
3. Presione **"Ejecutar Análisis de Hipótesis"**
4. Revise la **tabla comparativa**
5. Verifique que todas las hipótesis **cumplan** (✓)

### 3.6 Módulo 5: Verificación RETIE

**Objetivo**: Verificar distancias mínimas de seguridad

**Pasos**:
1. Seleccione el **nivel de tensión**
2. Ingrese la **altitud** del proyecto
3. Ingrese la **flecha máxima** (de Hipótesis D)
4. Seleccione el **tipo de cruce** a verificar
5. Ingrese la **altura del soporte**
6. Ingrese la **altura del obstáculo** (si aplica)
7. Presione **"Verificar"**

**Tipos de cruce disponibles**:
- Terreno transitable/no transitable
- Edificaciones
- Carreteras y calles
- Ferrocarriles
- Líneas de baja tensión
- Líneas de comunicaciones
- Aguas navegables/no navegables

### 3.7 Módulo 6: Generar Reporte

**Objetivo**: Exportar resultados en formato PDF

**Pasos**:
1. Complete la **información del proyecto**:
   - Nombre del proyecto
   - Ubicación
   - Nivel de tensión
   - Autor
   - Fecha
2. Seleccione el **contenido a incluir**
3. Presione **"Generar Reporte PDF"**
4. Presione **"Descargar Reporte PDF"**

---

## 4. Fundamentos Teóricos

### 4.1 Ecuación de Cambio de Estado

La ecuación de cambio de estado relaciona la tensión mecánica de un conductor bajo diferentes condiciones:

**Forma cúbica**:
```
σ₂³ - σ₂² × A - B = 0
```

**Donde**:
- `A = σ₁ - E×α×(t₂-t₁) + (E×a²×g₁²)/(24×σ₁²)`
- `B = (E×a²×g₂²)/24`

**Variables**:
- σ₁, σ₂: Tensiones unitarias inicial y final (kg/mm²)
- E: Módulo de elasticidad (kg/mm²)
- α: Coeficiente de dilatación (1/°C)
- t₁, t₂: Temperaturas inicial y final (°C)
- a: Vano regulador (m)
- g₁, g₂: Cargas específicas (kg/m/mm²)

### 4.2 Cálculos de Flecha

**Aproximación parabólica** (válida para f/a < 5%):
```
f = (w × a²) / (8 × H)
```

**Catenaria exacta**:
```
f = c × [cosh(a/(2×c)) - 1]
```

Donde c = H/w (parámetro catenario)

### 4.3 Vano Regulador

```
Lr = √(Σ(Li³) / Σ(Li))
```

El vano regulador representa el comportamiento mecánico de un cantón completo.

**Regla**: vano_máximo ≤ 2.5 × vano_regulador

### 4.4 Cargas Mecánicas

**Carga de viento**:
```
p_v = (ρ × V² × Cd × d) / 2
```

**Peso resultante**:
```
w_r = √(w_c² + p_v²)
```

### 4.5 Distancias de Seguridad

**Factor de corrección por altitud** (para V > 57.5 kV y h > 1000 msnm):
```
Factor = 1 + 0.03 × [(altitud - 1000) / 300]
```

---

## 5. Casos de Ejemplo

### 5.1 Caso 1: Línea 115 kV en Santanderes

**Datos**:
- Conductor: Hawk (ACSR 477 kcmil)
- Vanos: 280, 320, 300, 290, 310 m
- Altitud: 1000 msnm
- Viento: 25 m/s (90 km/h)
- EDS: 18%

**Resultados esperados**:
- Vano regulador: ~300 m
- Flecha máxima (75°C): ~10-12 m
- Todas las hipótesis deben cumplir

### 5.2 Caso 2: Línea 230 kV en Costa Caribe

**Datos**:
- Conductor: Drake (ACSR 795 kcmil)
- Vano regulador: 350 m
- Altitud: 50 msnm
- Viento: 27.8 m/s (100 km/h)
- EDS: 18%

**Consideraciones especiales**:
- Mayor carga de viento
- Temperatura ambiente más alta

### 5.3 Caso 3: Línea 34.5 kV en zona Andina

**Datos**:
- Conductor: Penguin (ACSR 4/0 AWG)
- Vano único: 200 m
- Altitud: 2600 msnm
- Viento: 23.6 m/s (85 km/h)
- EDS: 18%

**Consideraciones especiales**:
- Aplicar corrección por altitud para distancias
- Menor densidad del aire

---

## 6. Solución de Problemas

### 6.1 Errores Comunes

**"La tensión calculada excede el límite"**
- Reducir la tensión EDS inicial
- Verificar que el vano no sea excesivo
- Considerar un conductor de mayor sección

**"No se encontró solución física válida"**
- Verificar los parámetros de entrada
- La combinación de temperatura y carga puede ser incompatible
- Probar con otro método de solución

**"El cantón no es válido"**
- El vano máximo excede 2.5 veces el regulador
- Redistribuir las estructuras
- Dividir el cantón

**"Distancia no cumple RETIE"**
- Aumentar altura del soporte
- Reducir la flecha (aumentar tensión EDS)
- Verificar que la flecha usada sea de Hipótesis D

### 6.2 Preguntas Frecuentes

**P: ¿Cuál método de solución debo usar?**
R: Cardano es el más rápido y preciso para la mayoría de casos. Use Newton o Brent si Cardano falla.

**P: ¿Por qué la tensión aumenta al bajar la temperatura?**
R: El conductor se contrae térmicamente, lo que aumenta la tensión mecánica.

**P: ¿Cuándo debo considerar carga de hielo?**
R: En Colombia, solo en páramos sobre 3,500 msnm donde puede haber formación de escarcha.

**P: ¿Qué valor de EDS debo usar?**
R: Típicamente 15-20%. Un EDS menor reduce la fatiga pero aumenta la flecha.

---

## 7. Referencias

1. **RETIE - Resolución 40117 de 2024**
   Ministerio de Minas y Energía de Colombia
   - Artículo 13: Distancias de seguridad
   - Artículo 22: Líneas de transmisión

2. **NTC 2050**
   Código Eléctrico Colombiano (basado en NFPA 70)

3. **IEEE Std 738-2023**
   Standard for Calculating the Current-Temperature Relationship of Bare Overhead Conductors

4. **IEC 60826:2017**
   Design criteria of overhead transmission lines

5. **CREG 025 de 1995**
   Código de Redes

6. **NSR-10**
   Reglamento Colombiano de Construcción Sismo Resistente (velocidades de viento)

---

## Información de Contacto

**Programa**: Tecnología en Electricidad Industrial
**Universidad**: Unidades Tecnológicas de Santander
**Ubicación**: Bucaramanga, Colombia
**Año**: 2025

---

*Este software es de carácter educativo. Los resultados deben ser verificados por un profesional calificado antes de su uso en proyectos reales.*
