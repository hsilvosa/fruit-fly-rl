# Resolución de la navegación en mapas grandes

Fecha: 5 de octubre de 2026. Versión operativa: `observed-neuronal-map-v55`, integrada en el commit `972ceb4`.

Este documento reconstruye el problema, las hipótesis comprobadas, los intentos fallidos y la solución disponible. El resultado funcional es un planificador explícito que consume actividad del conectoma completo. La política aprendida sigue sin reproducir ese rendimiento. El [informe de v55](evidence/observed-map-v55-results.md) contiene las cifras, el protocolo prospectivo y los hashes de conservación; el [protocolo de intentos](evidence/portal-feedback-protocol.md) conserva la evolución experimental.

Las secciones 1 a 6 explican el problema y su resolución. Las secciones 7 a 20 detallan antecedentes, experimentos, datos, contratos, fórmulas, resultados por habitación, recursos y reproducción. Las cifras corresponden al estado verificado del 5 de octubre de 2026; las hipótesis y las contribuciones no aisladas se identifican expresamente.

## Índice

- [1. Qué problema había](#1-qué-problema-había)
- [2. Cómo se investigó](#2-cómo-se-investigó)
- [3. Intentos de solución y resultados](#3-intentos-de-solución-y-resultados)
- [4. Solución operativa final](#4-solución-operativa-final)
- [5. Verificación del resultado](#5-verificación-del-resultado)
- [6. Cómo usarlo y qué queda pendiente](#6-cómo-usarlo-y-qué-queda-pendiente)
- [7. Antecedentes y evolución del problema](#7-antecedentes-y-evolución-del-problema)
- [8. Registro de todos los pilotos retomados](#8-registro-de-todos-los-pilotos-retomados)
- [9. Datos, conectoma y transformaciones exactas](#9-datos-conectoma-y-transformaciones-exactas)
- [10. Contrato sensorial, memoria y separación de entradas](#10-contrato-sensorial-memoria-y-separación-de-entradas)
- [11. Odometría y conocimiento del objetivo](#11-odometría-y-conocimiento-del-objetivo)
- [12. Construcción exacta del mapa](#12-construcción-exacta-del-mapa)
- [13. Búsqueda y seguimiento de ruta](#13-búsqueda-y-seguimiento-de-ruta)
- [14. Frenado tridimensional, vuelo y recompensa](#14-frenado-tridimensional-vuelo-y-recompensa)
- [15. Resultados por habitación y diagnóstico de los timeouts](#15-resultados-por-habitación-y-diagnóstico-de-los-timeouts)
- [16. Recursos, tiempos y uso de GPU](#16-recursos-tiempos-y-uso-de-gpu)
- [17. Qué comprobaron los tests y verificaciones](#17-qué-comprobaron-los-tests-y-verificaciones)
- [18. Registros, reproducción y conservación](#18-registros-reproducción-y-conservación)
- [19. Separación de datos y límites científicos](#19-separación-de-datos-y-límites-científicos)
- [20. Criterios cumplidos y trabajo pendiente](#20-criterios-cumplidos-y-trabajo-pendiente)


## 1. Qué problema había

La mosca debía recorrer una habitación tridimensional, atravesar sus pasos entre obstáculos y llegar al objetivo. En el perfil `large`, la habitación mide 48 x 48 x 16 unidades y contiene 112 cajas de colisión, incluidas cinco particiones con aberturas alternadas. Se mantiene la dinámica de vuelo coordinado, con decisiones cada 0,05 segundos. Una llegada exige estar a menos de 0,45 unidades del objetivo sin colisión; agotar el tiempo es un fallo.

Los controladores podían colisionar, aproximarse a una pared sin atravesar su abertura o quedarse casi inmóviles. Las pérdidas finitas, los checkpoints compatibles y los tests de implementación no demostraban que pudieran completar el recorrido.

El 75% anterior correspondía a 48/64 llegadas en otra tarea: una habitación de 32 x 32 x 12, con 48 obstáculos y sin las particiones obligatorias de `large`. La comparación nueva partía de inicialización fresca y no continuaba aquella política exitosa. Una comprobación del checkpoint anterior en cuatro habitaciones originales reprodujo 3/4 llegadas, mientras que su transferencia a cuatro habitaciones grandes dio 0/4. Por tanto, los registros no demuestran una pérdida del comportamiento anterior en la misma tarea. Sí demuestran que la navegación del nuevo problema fallaba. Véase el [diagnóstico inicial](GEOMETRY_DIAGNOSIS.md).

## 2. Cómo se investigó

Se separaron la lectura neuronal, la estimación de referencias, la búsqueda de rutas y el control físico. Así se podía comprobar si una buena predicción llegaba a convertirse en un movimiento útil y si una ruta disponible terminaba en una llegada real.

Se conservaron los checkpoints anteriores. Cada tanda registró sus fuentes, presupuesto, transiciones físicas, actualizaciones y resultados por episodio. Los vuelos del profesor, los del estudiante y las comprobaciones geométricas se contabilizaron por separado. Los layouts usados repetidamente para ajustar variantes son mapas de optimización, no una prueba independiente.

Las dos primeras variantes de mapa, v41 y v42, hicieron un segundo reset del generador. Aunque conservaban etiquetas de semilla, no eran los mismos layouts canónicos que los anteriores. Se corrigió el reset explícito en v43 y se guardó la geometría inicial para auditar esa identidad. No se comparan por semilla las tandas afectadas.

## 3. Intentos de solución y resultados

### Aprendizaje, cobertura y percepción

Los primeros cambios probaron currículo, recompensas, supervisión guiada, memoria temporal, aislamiento del crítico y controles de las actualizaciones PPO. También se amplió la visión a un panorama alrededor del cuerpo y se recogieron vuelos guiados completos. Varias guías llegaron al objetivo, pero sus estudiantes siguieron fallando en `large`. Las referencias privilegiadas del profesor solo sirven como supervisión de entrenamiento; sus llegadas no son resultados autónomos del modelo.

La tanda de percepción de portales v13 a v19 probó nuevas distribuciones de rumbo, lectura de proyección, atención local, contexto y frenado. Sus siete candidatos terminaron en 0/8 sobre optimización. Aumentar la cobertura o reducir colisiones no bastaba para atravesar las paredes.

V32 añadió contexto global. Su ajuste angular en datos de entrenamiento parecía bueno, pero el vuelo siguió en 0/8. V34 aprendió una normal de pared y separó la aproximación del cruce: primero alinear la mosca delante de la abertura y después apuntar más allá. Llegó a 3/8, con una colisión y cuatro timeouts. Es el mejor estudiante aprendido de esta tanda.

Los siguientes intentos aislaron distancia, recogieron estados del estudiante con recuperación del profesor, cambiaron la protección lateral y alinearon panoramas al girar. No mejoraron v34. En particular, el cambio de lectura o la alineación temporal no pueden presentarse como causas suficientes del éxito final.

Se detectó además que las referencias de centros derivadas de geometría no garantizaban visibilidad. Un centro podía estar oculto en la imagen usada para etiquetarlo. La auditoría conservada usa el rayo panorámico más próximo y es una aproximación angular, no una prueba exacta de visibilidad. Esta limitación ayuda a interpretar los fallos de percepción; no demuestra por sí sola su causa completa.

### Lectura neuronal y mapa observado

Una reconstrucción de movimiento con pequeño sesgo podía acumular deriva al integrar posición y giro. Se introdujo un lector con contrato y huella propios: cancela la contribución recurrente proyectada en los 269 canales base y conserva el 5% en los 3.600 canales panorámicos. Reconstruye esos canales desde estados neuronales anteriores y actuales y la proyección fija; no añade sensores crudos al controlador.

El grafo completo sigue avanzando, con 167.184 neuronas y 25.583.622 conexiones dirigidas. La transformación es una decisión de ingeniería, no un mecanismo biológico demostrado. Un diagnóstico corto midió error de giro de aproximadamente 0,00000472 rad/s. La fórmula y su comprobación están en [matemáticas](MATHEMATICS.md).

La planificación explícita desde un mapa observado permitió separar una mala referencia aprendida de un fallo mecánico de ruta. V43 y v44 llegaron a 5/8, sin colisiones. V44 usaba el lector estable y obtuvo el mismo número de llegadas que v43; estabilizar la lectura no resolvió todos los bloqueos.

### Bloqueos concretos y correcciones

| Problema comprobado | Corrección | Qué se aprendió |
| --- | --- | --- |
| El margen de seguridad del mapa dejaba una única celda accesible junto al inicio | Permitir salir por celdas del margen local con coste alto, manteniendo impasables las superficies observadas | Un margen conservador puede encerrar una posición físicamente libre |
| Suavizar la ruta a través de un margen permitía cortar una esquina | Reducir anticipación y velocidad en zonas estrechas y comprobar el segmento | Relajar todo el margen produjo una colisión y no era una solución suficiente |
| Una referencia predicha quedaba fuera de la cuadrícula | Validar sus límites antes de convertirla en índices | V49 falló por un error de índice; corregirlo evitó ese fallo, pero v50 solo llegó a 1/8 |
| Un grupo de cajas podía parecer una pared completa al ajuste geométrico | Exigir cobertura de superficie antes de aceptar la pared | La geometría sintética mejoró, pero v51 a v53 siguieron en 0/8 |
| La búsqueda aceptaba acabar hasta 0,96 unidades antes de su referencia | Buscar la celda final exacta y añadir el objetivo continuo | Una búsqueda marcada como completada no garantizaba que la mosca cruzara la referencia |
| El seguimiento podía conservar una celda ya alcanzada | Avanzar a la siguiente referencia cuando la actual estaba suficientemente cerca | Evita pedir velocidad cero pese a tener ruta pendiente |
| El freno comprobaba el frente aunque el siguiente movimiento fuera vertical | Medir despeje alrededor de la dirección tridimensional solicitada | Una pared frontal dejaba de bloquear una subida o bajada libre |
| El giro horizontal reducía también el movimiento vertical | Aplicar la reducción por rumbo solo a la velocidad horizontal | La mosca puede ajustar altura mientras gira |

No todas estas correcciones forman parte del algoritmo final. El ajuste de paredes, las aberturas almacenadas y las propuestas aprendidas se probaron, pero v55 conserva solamente el mapa observado y el objetivo neuronal. Esa simplificación evitó depender de referencias de abertura que podían ser incorrectas.

| Variante representativa | Llegadas en optimización | Colisiones | Timeouts |
| --- | ---: | ---: | ---: |
| v13 a v19, siete candidatos de percepción | 0/8 cada uno | Ver protocolo | Ver protocolo |
| v31, geometría local con recurrencia reducida | 4/8 | 0 | 4 |
| v34, mejor estudiante aprendido | 3/8 | 1 | 4 |
| v43 y v44, mapa observado | 5/8 cada uno | 0 | 3 |
| v48, protección más conservadora | 1/8 | 0 | 7 |
| v51 a v53, pared y abertura observadas | 0/8 cada uno | 0 | 8 |
| v54, mapa global sin propuesta aprendida | 3/8 | 0 | 5 |
| v55, seguimiento y control tridimensional corregidos | 8/8 | 0 | 0 |

Estos valores muestran la evolución de la optimización. No constituyen una comparación final independiente ni prueban qué contribución aislada explica cada llegada. El cambio de v54 a v55 combinó correcciones de seguimiento y control; no se realizó una ablación independiente de cada una.

## 4. Solución operativa final

V55 reconstruye distancias, objetivo, velocidad y giro desde actividad neuronal. Con ellos estima su posición relativa y construye una cuadrícula de ocupación de 0,6 unidades. Una búsqueda ponderada elige una ruta por espacio observado o todavía desconocido. El seguimiento selecciona una referencia cercana y los controles de aceleración, altura y giro ejecutan el desplazamiento. Las observaciones siguientes actualizan el mapa y corrigen la trayectoria.

La búsqueda tiene un límite de 12.000 expansiones. Si no alcanza la celda final, elige una frontera abierta para continuar explorando. Su coste ponderado y su límite no garantizan la ruta más corta. Los rayos y la cuadrícula tampoco garantizan seguridad absoluta.

El controlador no recibe el objeto del mundo, poses verdaderas, cajas, semillas ni rutas certificadas. Sí conoce el tamaño de habitación del contrato y recibe un objetivo sintético como observación. Guardar geometría verdadera para auditar un vuelo no significa entregarla al controlador. Por ello no sería correcto describirlo como una mosca biológica que descubre por sí sola qué objetivo debe buscar.

El planificador funciona sin pesos aprendidos de movimiento. Las fases anteriores sí tuvieron entrenamiento: la tanda retomada añadió 131.072 transiciones físicas, llevando el uso sustantivo acumulado a 1.603.584. Las comprobaciones de v55 añadieron cero transiciones de entrenamiento y cero actualizaciones. Los ajustes sobre registros existentes, las verificaciones PPO temporales y los vuelos de comprobación se conservan separados.

## 5. Verificación del resultado

Se congeló v55 después de completar ocho mapas de optimización y antes de abrir 16 habitaciones nuevas de desarrollo. No se ajustó entre esos vuelos.

| Comprobación | Transiciones físicas | Llegadas | Colisiones | Timeouts |
| --- | ---: | ---: | ---: | ---: |
| Ocho mapas de optimización reutilizados | 25.168 | 8/8 | 0 | 0 |
| Dieciséis habitaciones nuevas de desarrollo | 56.544 | 13/16 | 0 | 3 |

El resultado prospectivo es 81,25%, con intervalo de Wilson del 95% de 57,0% a 93,4%. Las tres habitaciones que agotaron el tiempo son 8500011, 8500012 y 8500013. La muestra es pequeña y pertenece al mismo generador; no demuestra robustez en cualquier mapa. No se consumió el test reservado. Si se utilizan ahora esos tres fallos para ajustar una versión nueva, sus resultados posteriores ya no serían una comprobación prospectiva de esa nueva versión.

La versión pública reprodujo las acciones y el mapa del prototipo en 60 pasos sintéticos. Es una prueba de equivalencia de implementación, sin transiciones físicas. La suite completa pasó 265 tests. Desde el visor, la mosca completó el mapa conocido 370000 en 2.857 decisiones: 142,85 segundos simulados, sin colisión. La sesión cerró tras 3.200 decisiones y verificó el reinicio automático con memoria nueva. Esa repetición no se suma a los objetivos prospectivos.

Las capturas de la habitación y del cerebro se inspeccionaron. Se corrigieron el gradiente con historial en la inspección neuronal y el guardado que podía producir una captura cerebral vacía. El mapa anatómico muestra actividad modelada real; para el planificador, la sensibilidad por gradiente se indica como no disponible. Los archivos de vuelo cerraron y pasaron su auditoría sin errores ni advertencias.

Los hashes de checkpoints y aliases protegidos coinciden antes y después. No se sobrescribieron los modelos originales ni se atribuyeron las llegadas del planificador al estudiante.

## 6. Cómo usarlo y qué queda pendiente

Desde la carpeta del proyecto:

```powershell
.\launch-observed-map.cmd
```

El lanzador abre la habitación y una ventana cerebral separada. Shift acelera el tiempo simulado diez veces; R reinicia, N cambia de habitación, C cambia la cámara y F enfoca la mosca. Las sesiones archivan estados, acciones, metadatos y código del controlador. El demo no inicia entrenamiento.

La solución disponible resuelve muchos recorridos grandes mediante planificación explícita. Quedan tres timeouts en la muestra prospectiva, el aprendizaje autónomo del estudiante y una evaluación independiente más amplia. Antes de aumentar dificultad a `maze`, hay que comprobar el nuevo tamaño, los contratos sensoriales y la navegación. El objetivo de una política aprendida fiable sigue abierto; no debe marcarse como completado por el resultado del planificador.

Los siguientes pasos son diagnosticar los desvíos que agotan el tiempo, medir una versión corregida en nuevos mapas y, después, estudiar si el estudiante puede aprender de recorridos del planificador. Esa etapa debe declarar presupuesto y separar de nuevo el rendimiento de profesor y estudiante.


## 7. Antecedentes y evolución del problema

### 7.1. Cambio de tarea, selección y recompensa

Las particiones de `large` obligan a alejarse temporalmente del objetivo, encontrar una abertura, ajustar altura y descubrir el siguiente paso. Reducir distancia euclídea puede llevar contra una pared. El diagnóstico inicial midió rutas certificadas medias de aproximadamente 116 unidades en ocho layouts grandes retenidos frente a 30 en el generador anterior usando las mismas semillas. Esas rutas son referencias geométricas factibles, no vuelos óptimos o dinámicamente comprobados. El límite de episodio rondaba 170 segundos simulados en aquella muestra.

El currículo anterior registró 51 episodios exitosos en `open`, ninguno en `passages` o `large`, y avanzó por consumo de pasos. La selección podía conservar inicialización al tener cero éxito todos los candidatos. Una etiqueta de método ganador no demostraba entonces que una política entrenada hubiera aprendido. Se corrigió esa interpretación y se conservaron los resultados originales de fracaso.

Con gamma 0,995 y decisiones de 0,05 segundos, una recompensa a 60 segundos se multiplica por aproximadamente 0,00244; a 100 segundos, por 0,0000443. El crítico puede propagar valor por bootstrap; ese cálculo no demuestra imposibilidad de aprendizaje. Justificaba investigar horizonte y exploración, pero no establecía una causa única.

### 7.2. Correcciones anteriores a los portales

| Intento | Entrenamiento físico nuevo | Resultado autónomo de desarrollo | Evidencia |
| --- | ---: | --- | --- |
| Inicialización guiada v1 | 40.960 | 0/8, ocho colisiones | [Informe](evidence/guided-navigation-v1-results.md): ocho metas del profesor no se transfirieron al estudiante |
| Guiado v2 | 65.536 | 0/8, cuatro colisiones y cuatro timeouts | [Informe](evidence/guided-navigation-v2-results.md): estados del estudiante distintos de los del profesor y KL por encima del objetivo |
| Aislamiento del crítico v3 | 65.536 | 0/8, ocho colisiones | [Informe](evidence/guided-navigation-v3-results.md): memorias separadas no evitaron cambios excesivos |
| Protección de PPO v4 | 32.768 | 0/8 antes y después, ocho colisiones | [Informe](evidence/guarded-navigation-v4-results.md): siete actualizaciones aceptadas, nueve intentos rechazados |
| Lectura espacial v5 | 98.304 | 0/8, seis colisiones y dos timeouts | [Informe](evidence/spatial-neural-v5-results.md): fallo de comparación CPU/CUDA después de guardar checkpoint |
| Referencias neuronales v6 | 81.920 | 0/8, ocho colisiones | [Informe](evidence/neural-waypoint-v6-results.md): 16.384 pasos guiados y 65.536 autónomos |
| Panorama corporal v7 | 98.304 | Recuperación separada 0/8, ocho colisiones | [Informe](evidence/panoramic-neural-v7-results.md): 16 metas del profesor; fallo posterior de informe |
| Cobertura v8 | 301.056 | 0/8, ocho colisiones | [Informe](evidence/panorama-coverage-v8-results.md): 64 metas del profesor, ninguna del estudiante |
| Atención direccional v9 | 32.768 | 0/8, ocho colisiones | [Informe](evidence/directional-and-lookahead-results.md): progreso terminado en choque no fue éxito |
| Anticipación v10 | 163.840 | Final 0/8, cero colisiones y ocho timeouts | [Informe](evidence/directional-and-lookahead-results.md): 35 metas guiadas; controles teacher-only y pooling disperso también fallaron |

Las fases, contratos y datasets difieren: la tabla no es una comparación causal ni una curva única. Las pérdidas sobre datasets distintos no forman una curva de rendimiento de navegación.

V12 excluyó planos de velocidades de aproximación en la percepción para comprobar un posible atajo visual. Añadió 8.192 transiciones y dio 0/8, con una colisión y siete timeouts. El atajo seguía siendo hipótesis. El 4 de octubre cerró con 1.472.512 transiciones sustantivas acumuladas y navegación grande pendiente.

### 7.3. Pérdidas, KL y errores de verificación

Pérdida finita significa ausencia de NaN o infinito en esa operación. Imitación baja mide ajuste en muestras concretas. Recarga compatible verifica pesos y contrato. Ninguna sustituye un episodio completo desde el inicio original.

En v3 la KL aproximada final fue 0,342514 con objetivo 0,01; una entrada anterior llegó a 3,486418. El early stop de PPO no deshace necesariamente una actualización ya aplicada. V4 añadió aceptación y rollback según KL del rollout, pero fallaba antes de PPO; contener cambios no reparó su comportamiento inicial.

En v5 los tensores CPU/CUDA coincidían, pero las convoluciones CUDA con TF32 daban diferencias de acción superiores a la tolerancia. Desactivarlo redujo la discrepancia. Se conservó el estado original de fallo y se registró aparte la verificación posterior: reparar una comparación numérica no convirtió su 0/8 en éxito.

## 8. Registro de todos los pilotos retomados

### 8.1. Contadores y estados originales

La tabla deriva de registros ya existentes; no se ejecutó entrenamiento o evaluación para documentarla. Ajustar registros anteriores no añade transiciones físicas. La comprobación cuenta todo el lote, incluidos elementos que habían terminado y continuaban con acción cero.

V32 conserva el fallo de informe después de entrenar; la verificación posterior añadió cero entrenamiento. V33 falló antes de trabajar. V49 termina por excepción sin ocho episodios completos. V45 a v47 comprobaron un único mapa. V41 y v42 usan layouts del segundo reset y no son comparables por semilla con los canónicos.

| Experimento | Estado | Entrenamiento nuevo | Ajustes supervisados | Comprobación física | Llegadas / terminados | Colisiones | Timeouts |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: |
| `portal-feedback-v13` | Completado | 0 | 1,024 | 3,504 | 0/8 | 8 | 0 |
| `portal-feedback-v14` | Completado | 0 | 4,096 | 6,224 | 0/8 | 8 | 0 |
| `whitened-portal-v15` | Completado | 32,768 | 4,096 | 28,304 | 0/8 | 5 | 3 |
| `local-peak-portal-v16` | Completado | 0 | 0 | 28,480 | 0/8 | 7 | 1 |
| `centered-portal-v17` | Completado | 32,768 | 4,096 | 3,952 | 0/8 | 8 | 0 |
| `guarded-portal-v18` | Completado | 0 | 0 | 26,680 | 0/8 | 8 | 0 |
| `free-space-portal-v19` | Completado | 0 | 0 | 29,496 | 0/8 | 1 | 7 |
| `context-portal-v32` | Fallo de script | 32,768 | 4,096 | 0 | Sin episodios de comprobación terminados | 0 | 0 |
| `context-portal-v32-verification` | Completado | 0 | 0 | 29,496 | 0/8 | 0 | 8 |
| `approach-portal-v33` | Fallo de script | 0 | 0 | 0 | Sin episodios de comprobación terminados | 0 | 0 |
| `approach-portal-v34` | Completado | 0 | 1,536 | 28,480 | 3/8 | 1 | 4 |
| `range-approach-portal-v35` | Completado | 0 | 0 | 29,496 | 0/8 | 0 | 8 |
| `dagger-approach-v37` | Completado | 32,768 | 4,096 | 29,496 | 1/8 | 2 | 5 |
| `range-only-approach-v38` | Completado | 0 | 2,048 | 28,480 | 0/8 | 3 | 5 |
| `tube-approach-v39` | Completado | 0 | 0 | 29,496 | 1/8 | 0 | 7 |
| `aligned-approach-v40` | Completado | 0 | 2,048 | 29,496 | 1/8 | 2 | 5 |
| `observed-voxel-v41` | Completado | 0 | 0 | 29,584 | 1/8 | 1 | 6 |
| `observed-voxel-v42` | Completado | 0 | 0 | 29,584 | 1/8 | 0 | 7 |
| `observed-voxel-v43` | Completado | 0 | 0 | 29,496 | 5/8 | 0 | 3 |
| `observed-voxel-v44` | Completado | 0 | 0 | 29,496 | 5/8 | 0 | 3 |
| `observed-voxel-v45` | Completado | 0 | 0 | 3,687 | 0/1 | 0 | 1 |
| `observed-voxel-v46` | Completado | 0 | 0 | 3,687 | 0/1 | 0 | 1 |
| `observed-voxel-v47` | Completado | 0 | 0 | 1,999 | 0/1 | 1 | 0 |
| `observed-voxel-v48` | Completado | 0 | 0 | 29,496 | 1/8 | 0 | 7 |
| `observed-voxel-v49` | Fallo de script | 0 | 0 | 8,480 | Sin episodios de comprobación terminados | 0 | 0 |
| `observed-voxel-v50` | Completado | 0 | 0 | 28,480 | 1/8 | 0 | 7 |
| `observed-voxel-v51` | Completado | 0 | 0 | 29,496 | 0/8 | 0 | 8 |
| `observed-voxel-v52` | Completado | 0 | 0 | 29,496 | 0/8 | 0 | 8 |
| `observed-voxel-v53` | Completado | 0 | 0 | 29,496 | 0/8 | 0 | 8 |
| `observed-voxel-v54` | Completado | 0 | 0 | 28,480 | 3/8 | 0 | 5 |
| `observed-voxel-v55` | Completado | 0 | 0 | 25,168 | 8/8 | 0 | 0 |
| `observed-v55-development` | Completado | 0 | 0 | 56,544 | 13/16 | 0 | 3 |

V36 se conserva separado: 29.496 transiciones de diagnóstico geométrico, 1/8 llegadas, cero colisiones y siete timeouts; cero entrenamiento y ajustes.

### 8.2. Diagnósticos geométricos v20 a v31

No eran políticas aprendidas. V27 a v30 cancelaban recurrencia como límite de información, no evidencia de beneficio biológico. V31 retenía 5% proyectado.

| Variante | Transiciones | Llegadas / episodios | Colisiones | Timeouts |
| --- | ---: | ---: | ---: | ---: |
| v20 | 293 | 0/1 | 1 | 0 |
| v21 | 300 | 0/1 | 1 | 0 |
| v22 | 3,687 | 0/1 | 0 | 1 |
| v23 | 3,687 | 0/1 | 0 | 1 |
| v24 | 71 | 0/1 | 1 | 0 |
| v25 | 340 | 0/1 | 1 | 0 |
| v26 | 3,687 | 0/1 | 0 | 1 |
| v27 | 3,687 | 0/1 | 0 | 1 |
| v28 | 1,982 | 0/1 | 1 | 0 |
| v29 | 3,687 | 0/1 | 0 | 1 |
| v30 | 2,399 | 1/1 | 0 | 0 |
| v31 | 29,496 | 4/8 | 0 | 4 |

El grupo suma 53.316 transiciones físicas y cero entrenamiento. Una llegada de v30 en una habitación conocida demostraba viabilidad de ese vuelo, no robustez en ocho habitaciones.


### 8.3. Diagnósticos de percepción que cambiaron las decisiones

V13 tenía percentil 90 de error angular de aproximadamente 50,92 grados en muestras reutilizadas. V14 incorporó equivariancia de rumbo: rotar imagen y objetivo debía rotar la referencia. El test pasó y sus vuelos siguieron en 0/8. Una propiedad algebraica correcta de la red no elimina todos los errores de una tarea secuencial.

En 512 registros de v17 se identificaron 72 errores de dirección mayores de 90 grados y 45 etiquetas fuera del hemisferio permitido. Una mediana favorable podía ocultar errores infrecuentes decisivos. V19 amplió candidatos hasta 150 grados respecto del objetivo y frenó en un cono de 45 grados; terminó con una colisión y siete timeouts.

V32 ajustó dirección con mediana 1,55 grados y percentil 90 de 3,40 en 512 campos de entrenamiento. El RMSE de distancia era 1,14 unidades; para 73 referencias a menos de dos unidades, 0,54. Llegó a cero objetivos. Un error métrico pequeño respecto de la habitación puede ser grande respecto del espacio de una abertura.

V34 reutilizó los datos de v32 y ajustó solo la normal de pared en 1.536 actualizaciones. Durante alineación apuntaba 1,3 unidades antes del centro; durante cruce, 1,2 más allá. Es percepción aprendida con control proporcional, no PPO nuevo. Su historial fuente era 98.304 transiciones; no equivale al gasto global del proyecto.

V37 añadió 16.384 pasos del estudiante y 16.384 de recuperación guiada. En recogida, el estudiante terminó con cero objetivos y una colisión; el profesor, dos objetivos y ocho colisiones. El ajuste conjunto de dirección, distancia y normal empeoró el error angular: mediana aproximadamente 7,35 grados y percentil 90 de 30,15. La recuperación tampoco era infalible.

V38 congeló tensores angulares y comprobó puntuaciones idénticas mientras ajustaba distancia; no mejoró el vuelo. V39 conservó los pesos de v34 y estrechó el tubo de protección; redujo colisiones pero dio solo 1/8. V40 alineó panoramas mediante bearing neuronal del objetivo y ajustó 2.048 veces sobre registros existentes; también dio 1/8.

La auditoría de visibilidad aproximada encontró un rayo próximo que pasaba más allá del centro en 7.773 de 8.928 referencias de v32 y 7.679 de 9.192 de v37. En v37, 68 referencias superaban el alcance panorámico. El resto no puede clasificarse automáticamente como oculto: el rayo próximo no es un test geométrico exacto de la referencia. Las etiquetas anteriores eran referencias de supervisión privilegiadas, no centros cuya visibilidad se hubiera certificado.

## 9. Datos, conectoma y transformaciones exactas

### 9.1. Datos originales y decisiones del proyecto

MaleCNS v1.0 aporta conectividad, anotaciones, predicciones de neurotransmisor y coordenadas de somas. Fly RL añade selección de segmentos neuronales, normalización, signo simplificado, proyección sensorial artificial, actividad continua, sensores, dinámica y reglas de navegación. Los autores del dataset no produjeron este controlador. La atribución y la licencia están en [referencias](REFERENCES.md) y [datos y modelo](DATA_AND_MODEL.md).

Las tablas oficiales de anotaciones y conectividad usadas indican confianza mínima 0,5 en sus nombres. El criterio conserva segmentos con estado `Traced` o superclass asignada, excluyendo `Glia`, `Orphan` y `Unimportant`. Dentro de ese criterio se retienen todas las neuronas y conexiones entre ellas. No se afirma que se incluyan sin filtrado todos los segmentos de las tablas.

Se conservan 167.184 neuronas, 25.583.622 pares dirigidos y 124.176.995 sinapsis representadas. No se sustituyó por un grafo reducido en los vuelos, diagnósticos completos o verificaciones PPO citados. Los tests algebraicos con matrices sintéticas son tests unitarios, no navegación ni evidencia de cobertura del dataset.

Hay 140.033 somas con coordenadas y 27.151 neuronas sin coordenadas suministradas. Estas últimas siguen calculándose aunque no aparezcan como puntos. La vista anatómica representa somas, no arborizaciones completas ni actividad experimental medida.

### 9.2. Matriz y actividad neuronal

La matriz usa filas postsinápticas y columnas presinápticas; los pares repetidos se suman. Con conteo C_ij y signo sigma_j:

\[
W_{ij}=\frac{0.9\,\sigma_j C_{ij}}{\max(1,\sum_k C_{ik})}.
\]

Sigma es -1 para fuentes con predicción GABA y +1 para las otras o desconocidas. No representa conductancias, retardos o plasticidad según tipos celulares. La actualización fija es:

\[
h_t=0.5h_{t-1}+0.5\tanh(Wh_{t-1}+Ax_t-c).
\]

A es la proyección sensorial y c el centrado panorámico. La proyección base usa dos asignaciones por neurona, semilla 42 y amplitud 0,5; la panorámica añade dos, semilla 123457 y amplitud 0,25. Son asignaciones sintéticas, no conexiones visuales biológicas reconstruidas. La matriz y estas proyecciones no se optimizan durante PPO.

### 9.3. Lectura de proyección y límites de información

Un resumen agrupado puede mezclar coordenadas útiles para navegar. El diagnóstico de 128 transiciones sobre el grafo completo dio RMSE de distancia panorámica 1,724 para un ajuste afín agrupado, 0,824 para la proyección con recurrencia retenida y aproximadamente 0,0000446 para el límite que la cancela. El ajuste afín se midió sobre las muestras donde se ajustó: es un diagnóstico favorable, no validación independiente.

Desde los estados anteriores y actuales:

\[
z_t=\operatorname{atanh}(\operatorname{clip}(2h_t-h_{t-1},-1+10^{-6},1-10^{-6}))+c.
\]

En precisión ideal y sin saturación equivale a Wh_(t-1)+Ax_t. El clipping evita invertir tanh en sus extremos, pero introduce aproximación para valores saturados. El límite de información resta Wh_(t-1). La lectura whitened lo conserva; contrast resta 95%, dejando aproximadamente 5% proyectado.

V55 separa canales:

\[
f_t=A^+(z_t-Wh_{t-1})+D A^+Wh_{t-1},
\qquad
D_{kk}=\begin{cases}0,&k<269\\0.05,&k\ge269.\end{cases}
\]

Si N contiene las normas de columnas y B=A N^-1, se forma G=B^T B+10^-6 I y se resuelve N^-1 G^-1 B^T mediante Cholesky. A^+ designa aquí la reconstrucción estabilizada implementada, no una inversión exacta sin ridge. `reconstruct_activity` no consulta sensores del mundo; compararlos con canales reconstruidos es una verificación externa de precisión.

El grafo completo sigue actualizándose, mientras la base cancela la recurrencia en distancias cortas, objetivo y movimiento; el panorama conserva 5%. Son hechos distintos. El resultado no demuestra que esa fracción ni el cableado biológico sean la causa del éxito. No se realizó una comparación pareada final contra grafos alternativos.

## 10. Contrato sensorial, memoria y separación de entradas

| Índices base cero | Cantidad | Contenido | Escala de reconstrucción |
| --- | ---: | --- | --- |
| 0–127 | 128 | Distancias cortas | Por 8 |
| 128–255 | 128 | Velocidades de aproximación cortas | Velocidad con escala 3 |
| 256–258 | 3 | Dirección del objetivo en el cuerpo | Normalizar para obtener vector |
| 259 | 1 | Distancia al objetivo | Por norma de room - 0,32 |
| 260–262 | 3 | Velocidad corporal | Por 3 |
| 263–266 | 4 | Acción anterior | Comandos normalizados |
| 267 | 1 | Altitud | Por 16 en `large` |
| 268 | 1 | Velocidad de giro | Por 2,6 |
| 269–2068 | 1.800 | Distancias panorámicas | Por 24 |
| 2069–3868 | 1.800 | Aproximación panorámica | Velocidad con escala 3 |

El panorama tiene 25 filas por 72 columnas: elevación de -84 a 84 grados, azimut de -180 a 175 y alcance 24. Los rayos cortos combinan 26 direcciones de vecindad 3D y 102 adicionales distribuidas en esfera. Son 1.928 rayos y 3.869 valores, contando objetivos y estado.

Los sensores parten del centro del cuerpo y usan cajas sin inflar. La colisión sí incluye radio 0,16. Un despeje observado de 0,2 no significa tener 0,2 después de descontar el radio. La distinción es relevante al ajustar el freno.

El adaptador exige observación finita `(1, 9, 3869)`: ocho frames históricos y el actual, stride ocho decisiones. V55 toma el actual; su memoria útil es el mapa, la pose estimada y la ruta. No usa esos ocho frames como una política recurrente aprendida; conserva el contrato de la tubería.

Los resets vacían actividad, historial y contadores. En un lote, los elementos terminados se reinician independientemente y se preserva el estado neuronal de los que continúan. El visor vacía también el controlador al fin de episodio, con R y con N.

La alineación v40 usaba cambio de bearing del objetivo y remuestreo circular de columnas. La traslación también altera ese bearing; no era odometría exacta. Pasar tests de rotación de 45 grados, borde circular y gradientes no establecía éxito de vuelo.

## 11. Odometría y conocimiento del objetivo

La posición del mapa empieza en x=y=0 y z se reconstruye de altitud. El yaw empieza en cero: es un marco relativo al rumbo inicial, no la pose absoluta de la habitación. Las superficies se rotan a ese marco antes de acumularse.

Cada decisión integra giro observado durante 0,05 segundos y transforma velocidad corporal con la rotación estimada. El objetivo local es:

\[
g_{\mathrm{local}}=\frac{f_{256:259}}{\max(\|f_{256:259}\|,10^{-6})}\max(f_{259},0)\|[48,48,16]-0.32\|.
\]

La primera observación fija `initial_goal`. Si la distancia horizontal local supera dos unidades, se compara bearing esperado del ancla con observado. El error envuelto de yaw se limita a +/-0,02 radianes y se multiplica por 0,2. La corrección de posición por el ancla limita cada componente a +/-0,2 y aplica factor 0,15. La altitud combina 80% de estimación y 20% de lectura.

No hay pose verdadera en la interfaz, pero sí una dirección y distancia sintéticas al objetivo. Es una ayuda explícita de la tarea; no es navegación sin referencia ni descubrimiento autónomo del objetivo. La geometría verdadera guardada para auditoría no entra en estos cálculos.

Un sesgo de yaw rota todas las superficies acumuladas y puede inutilizar el mapa tras miles de decisiones. El lector estable reduce ese error numérico. V43 y v44 dieron ambos 5/8, demostrando que no era la única limitación.


## 12. Construcción exacta del mapa

La cuadrícula tiene forma `(216,216,28)`, resolución 0,6 y origen `[-64.8,-64.8,0]` en el marco relativo. Son 1.306.368 celdas. El rango horizontal permite representar habitaciones rotadas respecto del rumbo inicial; no es el tamaño de la habitación física.

La evidencia usa `int8`, comienza en cero y se actualiza en la primera decisión y cada diez, aproximadamente 0,5 segundos simulados. Se planifica en la primera y cada veinte decisiones, aproximadamente un segundo, o si falta ruta.

Se muestrean puntos libres a distancias desde 0,3 hasta menos de 24, paso 0,45, antes de la distancia medida menos 0,35. Cada celda única observada libre pierde uno, con suelo -8. Se usan índices únicos para impedir cambios repetidos por muchos rayos en una integración.

Los extremos con distancia menor de 23,4 son impactos. Cada grupo de cuatro píxeles panorámicos vecinos puede rellenarse como superficie si todas sus profundidades son menores de 23,4 y su variación es menor de 1,6. Se añaden 25 puntos bilineales por grupo, con coeficientes 0, 0,25, 0,5, 0,75 y 1 en cada eje. Cada celda única de superficie gana tres, con techo 12. La celda actual se marca libre, evidencia -8.

El relleno reduce agujeros entre rayos, pero puede conectar superficies que no deberían unirse. La discretización, perspectiva, lectura y persistencia pueden producir huecos u ocupación falsa. No hay un modelo de incertidumbre calibrado ni garantía de reconstrucción exacta de cajas.

Evidencia al menos dos significa ocupado. Se bloquean capas inferior y superior, y se dilatan sólidos una celda en las direcciones axiales. El coste es 1 para observado libre, 2,8 para desconocido e infinito para sólido o margen.

Si la posición cae en el margen se activa `tight`. En una región local de cinco celdas por eje, las celdas del margen que no son sólidos pasan a coste 8; las superficies observadas siguen bloqueadas. La celda actual cuesta 1. Es un escape local, no relajación global de paredes.

## 13. Búsqueda y seguimiento de ruta

La búsqueda considera 26 desplazamientos. Cada transición cuesta el valor de celda destino por longitud del desplazamiento: 1, raíz de 2 o raíz de 3 en unidades de celda. La prioridad es:

\[
F(n)=g(n)+4.5\,h(n),\qquad h(n)=\|n-n_{\mathrm{objetivo}}\|_2.
\]

El factor 4,5 favorece progreso con menos expansiones. No garantiza ruta mínima. Para una diagonal, se rechaza el paso si alguna celda intermedia axial está bloqueada. No es una prueba continua de despeje de una esfera en todas las diagonales.

La condición final exige índice exacto del voxel objetivo y después añade su coordenada continua. Si se alcanzan 12.000 expansiones sin llegar, se eliminan entradas cerradas de la cabeza del heap y se usa la mejor frontera abierta restante. Si no hay frontera abierta, se conserva el mejor visitado por cercanía. Esto evita usar por defecto un nodo cerrado junto a pared mientras queda otra alternativa abierta, pero aún puede escoger un desvío insuficiente.

La ruta se reconstruye mediante padres y centros de celdas. Se encuentra su punto más cercano y se elimina el prefijo anterior. Si hay otro punto y el primero está a menos de 0,35, se avanza. Así no se permanece en un centro ya alcanzado.

La anticipación es tres unidades, o una en modo `tight`. Cada segmento se muestrea aproximadamente cada 0,1 y se exige estar dentro de la cuadrícula y en costes finitos. Se consulta el coste guardado de la última planificación, no una prueba geométrica oculta. A menos de 1,5 del objetivo observado se usa su vector directamente.

Antes se aceptaba finalizar a menos de 1,6 celdas del objetivo, casi 0,96 unidades con esta resolución. Una búsqueda con `found=true` podía detenerse antes de atravesar la referencia. La igualdad de voxel más el objetivo continuo eliminó esa condición anticipada.

## 14. Frenado tridimensional, vuelo y recompensa

Sea d la referencia en el cuerpo, D=max(norm(d),10^-6), u=d/D y p un extremo reconstruido. Se combinan 128 rayos cortos y 1.800 panorámicos:

\[
\ell=p^Tu,\qquad \rho=\|p-\ell u\|.
\]

El despeje L es la menor ell positiva con rho menor de 0,25; si no hay ninguna, se inicia en 24. La velocidad solicitada es:

\[
s=\min\left(v_{\max},1.5D,\sqrt{2.4\max(L-0.27,0)}\right),
\quad v_{\max}=\begin{cases}0.8,&\mathrm{tight}\\1.8,&\mathrm{normal}.\end{cases}
\]

Se mide la dirección solicitada, no el frente o la velocidad horizontal actual. Eso permite comprobar una subida libre aunque haya pared delante. Los rayos siguen siendo dispersos: no garantizan ver todos los obstáculos dentro del tubo.

Con error de yaw e, la velocidad horizontal deseada es s u_xy max(cos(e),0)^4. La vertical es s u_z, independientemente del giro horizontal. Si la componente horizontal de la referencia tiene norma menor o igual a 0,05, se usa e=0 para que ruido horizontal mínimo no bloquee un movimiento casi vertical.

Los comandos de aceleración se derivan de esa velocidad:

\[
T=\operatorname{clip}(3(\|v^*_{xy}\|-v_x)+0.6\|v^*_{xy}\|,-1.2,3),
\]

\[
a_{\mathrm{forward}}=\begin{cases}T/3,&T\ge0\\T/1.2,&T<0,\end{cases}
\]

\[
a_{\mathrm{vertical}}=\operatorname{clip}((3(v^*_z-v_z)+0.8v^*_z)/2.5,-1,1),
\qquad a_{\mathrm{yaw}}=\operatorname{clip}(2e/1.8,-1,1).
\]

El comando lateral es cero. Los factores 0,6 y 0,8 compensan arrastre simplificado frontal y vertical. No hay integral o derivada explícita del error de posición: es control proporcional de velocidad con referencia espacial y compensación de arrastre.

La dinámica coordinada calcula yaw rate deseado 1,8 a_yaw + 0,8 a_lateral y lo suaviza con factor min(1; 5 dt). La aceleración corporal positiva es `[3 a_forward, 0.35 a_lateral, 2.5 a_vertical]`; para frontal negativo se usa 1,2. El arrastre es `[0.6,2.8,0.8]`. La velocidad física se limita a tres unidades por segundo. Bank y pitch son estados visuales suavizados; no simulan batido de alas o aerodinámica real.

La colisión usa el segmento de posición anterior a nueva contra cajas infladas por radio 0,16, además de los límites del cuarto. Puede detectar atravesar una caja entre decisiones. Esa prueba física sigue activa y no se sustituye por la cuadrícula.

La recompensa base es dos veces la reducción de distancia menos 0,02 por paso, con +20 en llegada, -5 en colisión y -5 en timeout. V55 no optimiza esta recompensa; la registra por compatibilidad. El límite de episodio del perfil depende de la longitud certificada L_ref:

\[
\operatorname{ceil}\left(\frac{\max(60,2L_{\mathrm{ref}}/1.5+15)}{0.05}\right).
\]

La ruta certificada fija parte del protocolo del entorno, pero no entra en las acciones del planificador. No se ampliaron esos plazos originales para obtener el 13/16.

## 15. Resultados por habitación y diagnóstico de los timeouts

### 15.1. Optimización canónica

| Semilla | Resultado | Decisiones | Segundos simulados | Distancia final |
| --- | --- | ---: | ---: | ---: |
| 370000 | Llegada | 2857 | 142.85 | 0.422525 |
| 370001 | Llegada | 2773 | 138.65 | 0.412719 |
| 370002 | Llegada | 2026 | 101.30 | 0.419600 |
| 370003 | Llegada | 2053 | 102.65 | 0.443625 |
| 370004 | Llegada | 2998 | 149.90 | 0.400518 |
| 370005 | Llegada | 2678 | 133.90 | 0.401159 |
| 370006 | Llegada | 3146 | 157.30 | 0.449248 |
| 370007 | Llegada | 2166 | 108.30 | 0.448753 |

### 15.2. Desarrollo prospectivo congelado

| Semilla | Resultado | Decisiones | Segundos simulados | Distancia final |
| --- | --- | ---: | ---: | ---: |
| 8500000 | Llegada | 3069 | 153.45 | 0.409150 |
| 8500001 | Llegada | 1952 | 97.60 | 0.413202 |
| 8500002 | Llegada | 1918 | 95.90 | 0.398511 |
| 8500003 | Llegada | 1910 | 95.50 | 0.439138 |
| 8500004 | Llegada | 1916 | 95.80 | 0.413129 |
| 8500005 | Llegada | 2088 | 104.40 | 0.421456 |
| 8500006 | Llegada | 1663 | 83.15 | 0.421959 |
| 8500007 | Llegada | 2013 | 100.65 | 0.427010 |
| 8500008 | Llegada | 2029 | 101.45 | 0.446484 |
| 8500009 | Llegada | 3365 | 168.25 | 0.449494 |
| 8500010 | Llegada | 1739 | 86.95 | 0.441575 |
| 8500011 | Timeout | 3345 | 167.25 | 6.853000 |
| 8500012 | Timeout | 3534 | 176.70 | 26.957935 |
| 8500013 | Timeout | 3503 | 175.15 | 14.086490 |
| 8500014 | Llegada | 2872 | 143.60 | 0.408959 |
| 8500015 | Llegada | 2365 | 118.25 | 0.399152 |


El tiempo es simulado, con decisiones de 0,05 segundos. La distancia final no es longitud de recorrido. Agotar tiempo no se cuenta como éxito por haber avanzado.

Las trazas finales de 8500011 y 8500012 mostraban `found=false` y 12.000 expansiones. En 8500013 se encontraba una ruta, pero no se completó a tiempo. Aumentar únicamente el límite de búsqueda no está demostrado como solución de los tres casos. Cambios de referencia, desvíos, odometría y costes requieren análisis adicional.

Sus distancias finales fueron 6,853, 26,958 y 14,086 unidades, respectivamente. Había movimiento registrado: no eran tres llegadas omitidas ni tres colisiones ocultadas. Los detalles proceden de las trazas existentes, sin evaluación nueva.

El intervalo de Wilson usa k=13, n=16, p_hat=k/n y z=1,959964:

\[
\frac{\hat p+z^2/(2n)\ \pm\ z\sqrt{\hat p(1-\hat p)/n+z^2/(4n^2)}}{1+z^2/n}.
\]

Da 57,0–93,4%. La estimación 81,25% no establece una garantía de al menos 80%; cero colisiones en 16 tampoco implica riesgo cero. No se compararon v55 y v34 de forma pareada en estos 16 mapas.


## 16. Recursos, tiempos y uso de GPU

El entorno probado usa Python 3.11, PyTorch 2.7.1 con CUDA 12.8, Stable-Baselines3 2.7.0 y Panda3D 1.10.16, en una RTX 3060 de 12 GB. V55 no añadió dependencias.

La actualización dispersa del conectoma, la reconstrucción y los sensores `torch-cuda` usan GPU. La odometría, cuadrícula, SciPy, heap de búsqueda, buena parte de física y escritura usan CPU. La reconstrucción devuelve características a NumPy, con transferencias y sincronización. Un porcentaje bajo de GPU no significa que esté detenido ni que todo el tiempo se dedique al optimizador.

El diagnóstico estable de 128 transiciones registró aproximadamente 0,682 segundos después de inicializar, pico de 560 MiB de VRAM asignada, RMSE base normalizado 0,00000567, de yaw rate 0,00000472 rad/s y de distancia panorámica 0,0419. Ese pico es memoria asignada de PyTorch en esa comprobación, no memoria total de proceso, render o driver ni benchmark integral.

La tanda de ocho mapas comenzó a 13:02:20 UTC y terminó a 13:05:35, unos 195,27 segundos con inicialización y cierre. La prospectiva comenzó a 13:06:22 y terminó a 13:12:22, unos 360,69 segundos. Dividir sus contadores físicos por esos tiempos da alrededor de 129 y 157 transiciones de lote por segundo. Son tasas de esas ejecuciones, no una medición universal de entrenamiento ni del demo renderizado.

La cuadrícula contiene unos 1,31 millones de celdas por controlador. La búsqueda crea arrays de costes, scores, padres y visitados, además del heap. La evidencia por sí sola no representa toda la memoria de CPU. Lote, expansiones, rayos y render anatómico afectan componentes diferentes.

## 17. Qué comprobaron los tests y verificaciones

La versión integrada pasó 265 tests. Acreditan las propiedades comprobadas, no éxito en cualquier habitación. Los seis nuevos del planificador cubren avance de referencia alcanzada, escape del margen sin abrir sólidos, subida libre ante pared frontal, frenado hacia obstáculo, eliminación de mapa y odometría al reset y rechazo de historia incompatible o no finita.

Los tests de lectura verifican álgebra, recurrencia visual no nula, contratos distintos y resets independientes. Los de visualización comprueban body IDs y sensibilidad acorde con el lector. V55 guarda actividad y cambio, con sensibilidad no disponible; no calcula una derivada PPO para una acción que PPO no decidió.

La tanda incluyó tres verificaciones temporales PPO de 128 transiciones y una actualización cada una. Son comprobaciones separadas, no entrenamiento sustantivo ni rendimiento de navegación. La del lector estable registró pérdidas finitas, value loss 0,824498, KL aproximada 0 y error máximo CPU de recarga de acción 3,5763e-7. El checkpoint temporal se eliminó. Una actualización y KL cero no demuestran aprendizaje.

Dos aperturas de 40 pasos comprobaron controles y cierre. El vuelo de 3.200 verificó una llegada conocida y reset automático. Las teclas y ventanas se ejercitaron por programa en modo offscreen; no se presenta como una prueba manual de todos los dispositivos. Las imágenes de habitación y cerebro se inspeccionaron visualmente.

Se corrigió un índice neuronal aplicado sobre un gradiente que aún contenía dimensión histórica. Para lectores de proyección, el gradiente se transformó al impulso neuronal reconstruido manteniendo fijos estados anteriores, en vez de llamarlo sensibilidad del estado recurrente. Para el planificador se muestra solo actividad y cambio. El guardado cerebral evita un PNG vacío: codifica en memoria, exige datos y reemplaza mediante archivo temporal.

## 18. Registros, reproducción y conservación

### 18.1. Archivo histórico y previsualización

Cada sesión tiene directorio único en `runs/demo`; no sobrescribe sesiones previas. La imagen de previsualización y `reports/demo.json` pueden representar la última sesión, pero no son el archivo histórico completo.

El manifest guarda dataset, huella del cerebro, lectura, contrato sensorial, número de características, dinámica, configuración, versiones de software, revisión Git y si el árbol estaba modificado. Los bloques comprimidos guardan sensores anteriores y siguientes, características, acciones y acciones aplicadas, posiciones, velocidades, yaw, recompensa y terminación. Los eventos registran habitaciones, resets, fin de episodios y observaciones neuronales. Los snapshots de todas las neuronas son opcionales con `--record-brain`.

V55 archiva `controller.py` y `controller.json` con tipo, versión y SHA-256, no un checkpoint PPO que aparente pesos de movimiento. La fuente pública congelada tiene SHA-256 `faec0e96a8fb6e26a88675a25c7fb4468593aca481e70a4e50d463c621053dd2`. Prototipo y módulo público tienen estructuras distintas: su equivalencia se verificó por acciones/mapa y vuelo integrado, no suponiendo hashes iguales entre fuentes diferentes.

La telemetría usa chunks de 128 filas, checksums y reemplazo temporal. Su auditoría comprueba schema, finitud, pasos, hashes y referencias a habitaciones. Las sesiones documentadas cerraron sin errores ni advertencias de archivo. Replay reproduce estados guardados sin recalcular cerebro o controlador.

### 18.2. Comandos y contratos de ejecución

```powershell
.\launch-observed-map.cmd
.\launch-observed-map.cmd --speed 4 --seed 370001
.\launch-observed-map.cmd --record-brain
```

El wrapper `.cmd` llama a PowerShell explícitamente para evitar que la asociación de `.ps1` abra un editor. El CLI fija `large`, dinámica coordinada, sensors-v6 y lector estable. Rechaza combinar el planificador con checkpoint PPO, otro perfil o contrato sensorial incompatible. No promete tamaños arbitrarios.

Shift multiplica por diez el tiempo simulado, no los pesos, fuerzas, radio o velocidad física máxima. Acelerar reproducción requiere ejecutar más decisiones por segundo de reloj; el límite de cómputo puede reducir la aceleración visible. El demo no entrena.

Para una sesión ya guardada, sustituir el nombre por el directorio real:

```powershell
.\.conda\python.exe -m fly_rl inspect runs/demo/NOMBRE_DE_SESION
.\.conda\python.exe -m fly_rl replay runs/demo/NOMBRE_DE_SESION
```

Repetir un vuelo en una semilla conocida produce datos nuevos de comprobación, pero no nuevos mapas independientes. Inspeccionar o reproducir registros no requiere optimizar una política.

### 18.3. Fuentes para localizar cada componente

| Componente | Fuente |
| --- | --- |
| Selección neuronal, conteos, normalización y checksums | [data.py](../fly_rl/connectome/data.py) |
| Grafo recurrente, proyección y actividad | [brain.py](../fly_rl/connectome/brain.py) |
| Reconstrucciones y lector estable | [innovation.py](../fly_rl/connectome/innovation.py) |
| Orden y geometría sensorial | [sensors.py](../fly_rl/simulation/sensors.py) |
| Dinámica coordinada | [flight.py](../fly_rl/simulation/flight.py) |
| Colisión, observación, recompensa y terminación | [world.py](../fly_rl/simulation/world.py) |
| Perfiles y plazo geométrico | [map_profiles.py](../fly_rl/simulation/map_profiles.py) |
| Lotes, historia y reset neuronal | [learning.py](../fly_rl/training/learning.py) |
| Mapa, búsqueda, seguimiento y comandos de v55 | [observed_map.py](../fly_rl/navigation/observed_map.py) |
| Visor, registro y reinicio de controlador | [viewer.py](../fly_rl/visualization/viewer.py) |
| Actividad y sensibilidad | [neural_view.py](../fly_rl/visualization/neural_view.py) |
| Ventana anatómica y captura | [brain_map.py](../fly_rl/visualization/brain_map.py) |
| Manifest y bloques de telemetría | [recording.py](../fly_rl/recordings/recording.py) |
| Auditoría de archivos | [archive.py](../fly_rl/recordings/archive.py) |
| Regresiones del planificador | [test_observed_map.py](../tests/navigation/test_observed_map.py) |

### 18.4. Commits y modelos preservados

`8bccaf4` incorporó lectores/pilotos y corrigió sensibilidad. `972ceb4` integró el planificador y demo. `dedc676` documentó el proceso. Esta ampliación es documental: no modifica código congelado, pesos, resultados o contratos de ejecución.

El [informe de v55](evidence/observed-map-v55-results.md) conserva los SHA-256 antes/después de los seis archivos de aliases anteriores. Se verificaron también checkpoints fuente y experimentales. Los artefactos locales retienen planes, hashes, estados de fallo, fuentes congeladas, geometría de auditoría y trazas. No se reescribió un fallo de script como éxito de navegación.

## 19. Separación de datos y límites científicos

Entrenamiento recoge experiencia para ajustar parámetros; optimización de diseño prueba variantes sobre mapas conocidos; desarrollo prospectivo comprueba una versión congelada en mapas nuevos; el test reservado tiene su propio protocolo de acceso. No se mezclan en una tasa única.

La geometría verdadera genera habitaciones, comprueba colisión, supervisa durante entrenamiento y audita después. V55 no la recibe. Sí recibe objetivo sintético, tamaño conocido y una lectura construida con la proyección conocida. No consultar cajas ocultas no equivale a carecer de ayudas artificiales.

Reutilizar 370000 a 370007 puede adaptar reglas a esos mapas aunque no se entrenen pesos. El 8/8 no elimina ese riesgo. Los 16 nuevos se fijaron antes de la comprobación, sin cambios durante los vuelos; son prospectivos para v55. Sus fallos se inspeccionaron después. Si ahora se usan para ajustar otra versión, hará falta otro conjunto nuevo.

No se demostró ruta óptima, ventaja biológica, transferencia a `maze`, aprendizaje sin supervisión, robustez frente a ruido o diversidad fuera de este generador. Tampoco se aisló mediante ablación cada corrección final. El paso de 3/8 en v54 a 8/8 en v55 combina avance de ruta, dirección del freno, velocidad en margen y control vertical independiente; no se atribuye a un solo parámetro.

El gasto acumulado del proyecto no es el historial de un modelo individual. Las 131.072 transiciones nuevas del 5 de octubre son cuatro tandas de 32.768, v15, v17, v32 y v37. V34 reutiliza registros y no añade pasos; v55 no tiene pesos aprendidos. Las transiciones de comprobación y las actualizaciones supervisadas se conservan aparte. No se suman dos veces el entrenamiento v32 y su verificación posterior.

## 20. Criterios cumplidos y trabajo pendiente

El alcance funcional de esta entrega es abrir un demo, observar vuelo autónomo que consume actividad del grafo completo y completar recorridos grandes con registros verificables. Se cumple en las comprobaciones documentadas. La política aprendida fiable y el objetivo de al menos 80% en un test final independiente siguen abiertos.

El trabajo siguiente debe conservar v55 como referencia, diagnosticar los tres timeouts por separado, congelar cualquier corrección antes de nuevos mapas y estudiar si un estudiante puede aprender recorridos completos del planificador. Comparar planificación, percepción aprendida y PPO requiere contratos y presupuestos declarados, varias inicializaciones y evaluación pareada que no seleccione versiones.

La memoria de mapa no se presenta como memoria aprendida. Conservar todas las neuronas no demuestra que la anatomía sea necesaria para el algoritmo. La explicación respaldada es que se hizo más utilizable la lectura artificial, se añadió memoria espacial explícita y se corrigió la ejecución de rutas. Hay llegadas reales y tres fallos nuevos que delimitan el alcance. No existe todavía una prueba de que PPO haya aprendido esa solución.
