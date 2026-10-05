# Resolución de la navegación en mapas grandes

Fecha: 5 de octubre de 2026. Versión operativa: `observed-neuronal-map-v55`, integrada en el commit `972ceb4`.

Este documento reconstruye el problema, las hipótesis comprobadas, los intentos fallidos y la solución disponible. El resultado funcional es un planificador explícito que consume actividad del conectoma completo. La política aprendida sigue sin reproducir ese rendimiento. El [informe de v55](evidence/observed-map-v55-results.md) contiene las cifras, el protocolo prospectivo y los hashes de conservación; el [protocolo de intentos](evidence/portal-feedback-protocol.md) conserva la evolución experimental.

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
