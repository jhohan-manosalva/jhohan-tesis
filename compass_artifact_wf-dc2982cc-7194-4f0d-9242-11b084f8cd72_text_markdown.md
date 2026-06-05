# Normativa colombiana y metodología técnica para cálculos mecánicos en líneas de transmisión de alta tensión

El diseño mecánico de líneas de transmisión en Colombia se rige por el **RETIE (Resolución 40117 de 2024)**, las normas NTC del ICONTEC, y los códigos de la CREG, aplicando metodologías basadas en estándares internacionales IEC e IEEE adaptadas a condiciones climáticas tropicales específicas. La tensión máxima permitida en conductores no debe superar el **50% de la carga de rotura** bajo condiciones de viento máximo, mientras que la tensión de operación diaria (EDS) se limita al **18%** para prevenir fatiga por vibraciones. Los parámetros de diseño varían significativamente según la zona geográfica: desde la Costa Caribe con vientos de hasta **162 km/h** en La Guajira, hasta las zonas andinas con temperaturas que oscilan entre **5°C y 40°C** según la altitud.

## Marco regulatorio colombiano vigente

El Reglamento Técnico de Instalaciones Eléctricas establece los requisitos obligatorios para líneas de transmisión aérea en Colombia. La **Resolución 90708 de 2013** del Ministerio de Minas y Energía constituyó el RETIE vigente durante más de una década, con modificaciones mediante las Resoluciones 90907/2013 y 90795/2014. En 2024, la **Resolución 40117** introdujo el nuevo RETIE estructurado en cuatro libros: definiciones, productos, instalaciones y evaluación de conformidad.

El Artículo 22 del RETIE establece las prescripciones generales para líneas de transmisión. El diseño debe contemplar memorias de cálculos eléctricos, estructurales, mecánicos y geotécnicos, junto con especificaciones técnicas, requerimientos ambientales y planos de localización. Los cálculos mecánicos exigidos incluyen comportamiento en régimen permanente y transitorio, coordinación de aislamiento, distancias de seguridad, apantallamiento y análisis de sobretensiones.

Las **distancias de seguridad** según la Tabla 13.2 del RETIE para líneas de alta tensión establecen valores mínimos que aumentan con el nivel de tensión. Para cruces de carreteras, la distancia vertical mínima es de **6.1 metros** para líneas de 115 kV, **8.5 metros** para 230 kV, y **11.5 metros** para 500 kV. Un requisito crítico especifica que para tensiones mayores a 57.5 kV, las distancias se incrementan en **3% por cada 300 metros** que sobrepasen los 1,000 msnm, factor determinante dado el terreno montañoso colombiano.

### Normas técnicas colombianas aplicables

El **Código Eléctrico Colombiano (NTC 2050)**, basado en el NFPA 70, establece requisitos generales cuya aplicación es obligatoria según el RETIE. Para conductores aéreos, la **NTC 309** especifica conductores ACSR conforme a ASTM B232, mientras que la **NTC 2639** cubre conductores con núcleo de acero recubierto de aluminio. La **NTC 2244** define conectores para uniones aluminio-aluminio o aluminio-cobre en líneas aéreas desnudas.

La **Resolución CREG 025 de 1995** establece el Código de Redes con requisitos técnicos mínimos para conexiones al Sistema de Transmisión Nacional. Define los criterios N-1 (operación estable ante indisponibilidad de un circuito) y N-K para análisis probabilístico. Los niveles de tensión según CREG 070/1998 clasifican el Nivel IV como tensiones ≥62 kV, correspondiente a líneas de transmisión propiamente dichas.

## Ecuaciones fundamentales de cálculo mecánico

### La ecuación de cambio de estado

La herramienta matemática central para el diseño mecánico es la ecuación cúbica de cambio de estado, que relaciona la tensión mecánica de un conductor en diferentes condiciones de temperatura y carga:

**α(t₂ - t₁) + (σ₂ - σ₁)/E = (a²/24) × [(g₂²/σ₂²) - (g₁²/σ₁²)]**

Donde **α** representa el coeficiente de dilatación térmica (19.3×10⁻⁶ 1/°C para ACSR), **E** el módulo de elasticidad (77-83 GPa para ACSR), **σ** la tensión unitaria en kg/mm², **g** la carga específica, y **a** el vano o vano regulador. Esta ecuación se resuelve iterativamente o mediante el método de Cardano, permitiendo calcular la tensión del conductor cuando cambian las condiciones ambientales.

La derivación parte de dos principios: la variación de longitud por temperatura (ΔL₁ = α×L₀×Δt) y por tensión mecánica según la Ley de Hooke (ΔL₂ = Δσ×L₀/(E×S)). Igualando estas variaciones con la diferencia geométrica de longitudes de la catenaria se obtiene la ecuación cúbica completa.

### Cálculo de flecha mediante catenaria y parábola

La **ecuación exacta de la catenaria** describe la curva del conductor suspendido:

**y(x) = c × [cosh(x/c) - 1]** donde **c = H/w** (constante catenaria)

La flecha máxima para vanos a nivel se calcula como:

**f = c × [cosh(a/2c) - 1]**

La **aproximación parabólica**, válida cuando la relación flecha/vano es menor al 5%, simplifica considerablemente el cálculo:

**f = (w × L²)/(8 × H)**

Para un conductor ACSR Hawk de **0.975 kg/m** en un vano de 300 metros con tensión horizontal de 2,000 kg, la flecha parabólica resulta aproximadamente **5.5 metros**. El error respecto a la catenaria es inferior al 0.1% para vanos menores a 400 metros, pero alcanza el 2.5% para vanos de 1,000 metros.

La **longitud del conductor** según la aproximación parabólica se estima como L ≈ a + (8f²)/(3a), resultando típicamente un **0.5-1.0%** adicional sobre la longitud del vano.

## Vano regulador y vano crítico

El **vano regulador** (ruling span) es un vano ficticio que representa el comportamiento mecánico de un cantón completo entre torres de anclaje:

**Lr = √[(Σ Li³)/(Σ Li)]**

Esta fórmula pondera los vanos proporcionalmente al cubo de su longitud, reflejando que los vanos más largos tienen mayor influencia en el comportamiento tensional del cantón. Los valores típicos son **80 metros** en zonas urbanas y **150 metros** en zonas rurales. Para que el vano regulador represente adecuadamente al cantón, el vano máximo individual no debe exceder 2.5 veces el vano regulador.

El **vano crítico** determina qué condición climática gobierna el diseño:

**a_c = √[(24 × E × S × α × ΔT)/(g₂² - g₁²) × σ_adm]**

Para vanos menores al crítico domina la condición de temperatura mínima (máxima contracción), mientras que para vanos mayores domina la condición de máximo viento o carga. Identificar el vano crítico permite optimizar el diseño seleccionando la hipótesis correcta para cada estructura.

## Hipótesis de cálculo según normativa colombiana

El RETIE y las normas técnicas de empresas transmisoras definen cuatro hipótesis de diseño obligatorias para verificar la integridad mecánica de las líneas.

La **Hipótesis A (viento máximo)** combina la velocidad de viento de diseño (**100 km/h** según parámetros estándar, hasta **162 km/h** en La Guajira) con la temperatura mínima coincidente. La tensión del conductor no debe superar el **50% de la carga de rotura**. Esta condición determina las cargas transversales sobre estructuras y la tensión máxima del conductor.

La **Hipótesis B (temperatura mínima)** considera la temperatura mínima absoluta (**12°C** en zonas cálidas, hasta **5°C** en zonas altas) sin viento. La tensión máxima inicial debe limitarse al **33-35% de la carga de rotura** para prevenir exceso de tensión durante la vida útil debido al creep del conductor.

La **Hipótesis C (condición EDS)** representa la operación diaria normal a temperatura promedio (**20°C**) sin viento. La tensión de operación típica se mantiene entre **15-18% de la carga de rotura** para conductores de transmisión, permitiendo fatiga aceptable por vibraciones eólicas sin necesidad de amortiguadores.

La **Hipótesis D (flecha máxima)** evalúa la temperatura máxima del conductor (**75°C** en operación continua, hasta **100°C** en emergencia) para verificar que la flecha no viole las distancias de seguridad al terreno. Esta es la condición crítica para dimensionar la altura de estructuras.

## Cargas mecánicas y factores de seguridad

### Cálculo de cargas combinadas

La carga del viento sobre el conductor se calcula como:

**p_v = (0.5 × ρ × V² × C_d × d)/1000** [daN/m]

Donde ρ es la densidad del aire (varía de 1.225 kg/m³ a nivel del mar a aproximadamente 0.9 kg/m³ a 2,500 msnm), V la velocidad del viento en m/s, C_d el coeficiente de arrastre (**1.0** para cables cilíndricos), y d el diámetro del conductor en mm.

El **peso resultante** combina vectorialmente el peso propio y la carga del viento:

**w_r = √(w² + p_v²)**

Para un conductor ACSR Drake (403 mm², 28.1 mm de diámetro, 1.093 kg/m) sometido a viento de 100 km/h (27.8 m/s), la carga de viento resulta aproximadamente **1.33 daN/m**, y el peso resultante alcanza **1.72 daN/m**, un **57%** mayor que el peso propio.

### Factores de seguridad del RETIE

Los factores de seguridad mínimos establecidos por el RETIE, basados en IEC 60826, son:

| Elemento | Factor de Seguridad |
|----------|---------------------|
| Aisladores (suspensión y retención) | **2.5** |
| Postes de concreto | **2.5** |
| Postes de acero | **2.0** |
| Herrajes bajo tensión | **3.0** (ensayado: 2.5) |
| Grapas de retención | ≥90% carga rotura conductor |

Para estructuras de suspensión bajo condición normal (todos los conductores sanos con viento máximo), el RETIE exige verificar cargas verticales, transversales y longitudinales. Para condiciones anormales con rotura de subconductores, se aplican factores de reducción de viento y los componentes restantes deben mantener la estabilidad estructural.

## Parámetros técnicos específicos para Colombia

### Zonificación climática y condiciones ambientales

Colombia presenta cinco zonas climáticas principales según el IDEAM: Cálido Húmedo (Costa Caribe, Pacífico, Amazonía, Llanos), Cálido Seco (La Guajira, valles interandinos), Templado (laderas andinas 1,000-2,000 msnm), y Frío (altiplanos andinos sobre 2,000 msnm).

Las **temperaturas de diseño** varían considerablemente: la temperatura mínima oscila entre **5-10°C** en zonas frías y **18-22°C** en zonas cálidas; la temperatura media varía de **12-16°C** en páramos a **26-28°C** en tierras bajas; la temperatura máxima ambiente alcanza **35-40°C** en valles cálidos.

El **mapa de isotacas** según NSR-10 establece velocidades básicas de viento de **20-25 m/s** (72-90 km/h) para la mayor parte del territorio, pero valores extremos de **30-45 m/s** (108-162 km/h) en la Costa Caribe, particularmente en La Guajira. San Andrés y Providencia, ubicadas en zona de huracanes, requieren diseños para **40-50 m/s** (144-180 km/h).

### Conductores típicos por nivel de tensión

Para **34.5 kV** (subtransmisión) se utilizan conductores ACSR calibres 2 AWG a 4/0 AWG (Sparrow a Penguin), con vanos urbanos máximos de 70 metros y rurales de 100 metros. Las servidumbres mínimas son de 15 metros de ancho total.

Las líneas de **115 kV** emplean conductores ACSR de 266.8 a 477 kcmil (Partridge a Hawk), con capacidades de 100-200 MVA. El conductor Partridge (135 mm², 16.3 mm diámetro, 545 kg/km, 6,400 kgf de rotura) es frecuente para circuitos simples, mientras que Linnet o Hawk se prefieren para mayor capacidad.

Para **230 kV** se emplean conductores ACSR de 477-795 kcmil en haz de 2 conductores por fase. El conductor Ibis (201 mm², 19.9 mm diámetro) y Hawk (242 mm², 21.8 mm diámetro) son comunes. Las servidumbres alcanzan 32 metros de ancho total.

Las líneas de **500 kV** del Sistema de Transmisión Nacional utilizan haces de 3-4 conductores ACSR Drake (403 mm², 28.1 mm diámetro, 1,093 kg/km, carga de rotura superior a 14,000 kgf). Las capacidades alcanzan 1,000-2,000 MVA con servidumbres de 60-65 metros.

## Estándares internacionales y su aplicación en Colombia

### IEEE Std 738 para capacidad térmica

El estándar IEEE 738-2023 proporciona el método para calcular la relación corriente-temperatura basado en el balance de calor:

**q_c + q_r = q_s + I² × R(T_avg)**

Donde q_c representa las pérdidas por convección, q_r por radiación, q_s la ganancia solar, e I²R el calentamiento resistivo. Despejando la corriente máxima (ampacity):

**I = √[(q_c + q_r - q_s)/R(T_avg)]**

La aplicación en Colombia requiere adaptar parámetros para condiciones tropicales: latitud cercana al ecuador (mayor radiación solar), densidad del aire reducida en zonas andinas elevadas, y datos meteorológicos del IDEAM para temperaturas y vientos locales. Las empresas transmisoras como ISA e INTERCOLOMBIA aplican este estándar para determinar ratings térmicos de sus líneas.

### IEC 60826 y diseño basado en confiabilidad

El estándar IEC 60826:2017 establece la metodología probabilística mediante la ecuación:

**γ_Q × Q_T ≤ φ_R × R_C**

Donde γ_Q es el factor de carga (1.0-1.4), Q_T la carga característica con período de retorno T, φ_R el factor de resistencia (0.85-0.95), y R_C la resistencia característica. El RETIE referencia explícitamente IEC 60826 (numeral 7.3.6) para factores de seguridad de aisladores.

Los tres niveles de confiabilidad (períodos de retorno de 50, 150 y 500 años) permiten optimizar económicamente el diseño según la importancia de la línea. Las líneas del STN colombiano típicamente se diseñan con nivel 2 (150 años) para interconexiones regionales y nivel 3 (500 años) para troncales críticas como las líneas a 500 kV.

### Jerarquía normativa en Colombia

En caso de conflicto normativo, prevalece el RETIE como reglamento técnico de obligatorio cumplimiento. Las NTC aplican cuando el RETIE las referencia, y las normas internacionales (IEC, IEEE) aplican para aspectos no cubiertos por normativa nacional. Esta estructura permite adoptar el estado del arte internacional mientras se mantienen requisitos específicos para las condiciones colombianas.

## Estructuras y requisitos mecánicos según RETIE

El Artículo 22.5 del RETIE establece requisitos específicos para estructuras de suspensión y retención. Bajo **condición normal**, todas las estructuras deben resistir la combinación de conductores y cables de guarda sanos con viento máximo de diseño y temperatura coincidente.

Las **estructuras de suspensión** bajo condición anormal deben verificarse con 50% de subconductores rotos en cualquier fase (para líneas con conductores en haz) o un conductor roto en cualquier fase (para conductor simple). Las **estructuras de retención** deben resistir la condición de todos los subconductores en cualquier fase y un cable de guarda rotos simultáneamente.

Las zonas de servidumbre según Tabla 22.1 establecen anchos mínimos de **60-65 metros** para 500 kV (circuito simple/doble), **28-32 metros** para 230 kV, y **15-20 metros** para 115 kV. Para líneas HVDC, los anchos se reducen en 10%.

## Conclusiones técnicas y recomendaciones de diseño

El diseño mecánico de líneas de transmisión en Colombia exige integrar rigurosamente la normativa RETIE con metodologías internacionales adaptadas a condiciones tropicales. Los aspectos más críticos incluyen: la verificación de **cuatro hipótesis de cálculo** (viento máximo, temperatura mínima, EDS y flecha máxima), la correcta aplicación del **factor de corrección por altitud** (3% por cada 300 m sobre 1,000 msnm), y la selección de **velocidades de viento regionalizadas** que varían hasta un 100% entre el interior andino y la Costa Caribe.

La ecuación cúbica de cambio de estado permanece como herramienta fundamental, permitiendo predecir el comportamiento del conductor en todo el rango de condiciones operativas. Su solución iterativa, combinada con el concepto de vano regulador, permite optimizar cantones completos manteniendo tensiones uniformes y flechas predecibles.

Los conductores ACSR dominan el sistema de transmisión colombiano por su balance entre propiedades mecánicas y eléctricas, aunque los AAAC ganan adopción en zonas costeras por su superior resistencia a la corrosión. Las propiedades clave—módulo de elasticidad de **77-83 GPa**, coeficiente de dilatación de **19.3×10⁻⁶ 1/°C**, y límites de tensión del **50% UTS** en máxima carga—definen los parámetros de entrada para todo cálculo mecánico conforme a normativa vigente.