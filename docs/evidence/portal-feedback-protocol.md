# Percepción de pasos y control de vuelo mediante actividad neuronal

El trabajo se retomó por petición del usuario el 5 de octubre de 2026. La navegación autónoma en los mapas grandes originales seguía pendiente después de v12. Este protocolo distingue aprender una referencia espacial de aprender a convertirla en aceleraciones.

Los pilotos v13 y v14 consumen exclusivamente las nueve muestras de actividad neuronal del contrato sensors-v6. El cerebro conserva los 167.184 neuronas y las 25.583.622 conexiones de MaleCNS v1.0. El encoder predice una referencia en coordenadas del cuerpo y su velocidad local. No recibe posición absoluta, obstáculos, coordenadas de aberturas ni la ruta certificada durante el vuelo.

Las etiquetas se reconstruyen desde las poses y mapas de los 98.304 estados de optimización conservados de v7. Para cada estado se elige el siguiente punto de entrada o salida de una abertura sobre la ruta de entrenamiento, o el objetivo después de la última pared. Esta geometría es información privilegiada de supervisión. No entra en las observaciones del estudiante. Reutilizar esos datos no añade transiciones físicas.

La referencia predicha alimenta un control proporcional de velocidad, con frenado durante giros y compensación de arrastre. Este es un controlador híbrido: percepción aprendida y control físico explícito. Los pilotos ajustan percepción por supervisión, no ejecutan optimización PPO. La interfaz mantiene la distribución gaussiana y los caminos de predicción y evaluación de PPO consistentes, para una futura corrección con aprendizaje por refuerzo. No se presentan vuelos de este controlador como evidencia de que PPO aprendió esos movimientos.

V13 usó 1.024 actualizaciones y un límite de 32.768 transiciones de comprobación en ocho mapas de optimización. Terminó tras 3.504 transiciones, con cero llegadas y ocho colisiones. La recarga reprodujo las acciones, las pérdidas fueron finitas y los archivos protegidos conservaron sus hashes. Su error angular mediano en 512 estados de optimización fue 11,55 grados; el percentil 90 fue 50,92 grados. Los errores de velocidad fueron 0,063, 0,058 y 0,078 unidades por segundo. Son diagnósticos sobre datos reutilizados, no validación independiente.

Las predicciones iniciales de v13 mostraron una preferencia por el frente del cuerpo incluso con rumbos iniciales diferentes. V14 elimina las coordenadas horizontales fijas del encoder de puntuaciones; conserva profundidad neuronal, elevación y alineación con la dirección neuronal del objetivo. Una prueba comprueba que rotar cíclicamente la imagen neuronal y su dirección de objetivo rota la referencia predicha. Esto verifica una propiedad del encoder, no una simetría exacta del conectoma biológico o de todas las acciones.

V14 empieza con pesos nuevos, 4.096 actualizaciones supervisadas y el mismo máximo de 32.768 pasos de comprobación. Cada lote contiene un cuarto de ejemplos de los primeros 16 ticks, la mitad de estados guiados registrados y un cuarto de estados autónomos registrados. Los grupos pueden solaparse. Primero se comprueba el vuelo en mapas de optimización; sus resultados no prueban generalización. El test reservado y los aliases originales permanecen protegidos, sin promoción automática.

Los planes, pérdidas, hashes y trayectorias detalladas están en los artefactos privados y en las carpetas locales de cada experimento. Ninguno de estos cambios permite afirmar una ventaja biológica ni dar por resuelta la navegación sin llegadas autónomas verificadas.

## Nueva tanda con proyecciones corregidas

V14 también terminó con cero llegadas y ocho colisiones, tras 6.224 transiciones de comprobación. Sus 4.096 ajustes tuvieron pérdidas finitas y recarga compatible. La simetría del rumbo comprobada por los tests no bastó para navegar.

Un diagnóstico posterior midió una pérdida importante de precisión en el resumen por medias neuronales. Se preparó un lector de mínimos cuadrados que corrige la mezcla de la proyección sensorial artificial. La variante de diagnóstico cancela la recurrencia y sirve solo como límite de información; la candidata para vuelo conserva la contribución recurrente proyectada. Ambas se distinguen en código, huella y documentación. Las fórmulas y limitaciones están en [matemáticas](../MATHEMATICS.md).

V15 usa un controlador nuevo y un nuevo contrato de lectura neuronal. Su presupuesto es 32.768 transiciones guiadas nuevas, 4.096 actualizaciones supervisadas y hasta 32.768 transiciones separadas de comprobación autónoma en mapas de optimización. No transfiere pesos ni observaciones del test. Se registran pérdidas, mapas recorridos, datos válidos, recarga y resultados de profesor y estudiante por separado. Las comprobaciones de vuelo no incrementan el contador de entrenamiento del checkpoint.

Una verificación temporal adicional ejecutó exactamente 128 transiciones y una actualización PPO, con pérdidas finitas y recarga CPU compatible; el checkpoint temporal se eliminó. Esa verificación demuestra que la nueva política puede ejecutar la tubería de aprendizaje, pero no aporta resultados de navegación ni cuenta dentro del entrenamiento sustantivo.

## Resultados de las tandas retomadas

| Tanda | Entrenamiento físico nuevo | Comprobación física separada | Objetivos autónomos | Colisiones | Timeouts |
| --- | ---: | ---: | ---: | ---: | ---: |
| v13, percepción y PD | 0 | 3.504 | 0/8 | 8 | 0 |
| v14, rumbo equivarante | 0 | 6.224 | 0/8 | 8 | 0 |
| v15, lector corregido | 32.768 | 28.304 | 0/8 | 5 | 3 |
| v16, máximo local | 0 | 28.480 | 0/8 | 7 | 1 |
| v17, centros visibles | 32.768 | 3.952 | 0/8 | 8 | 0 |
| v18, desvíos y frenado | 0 | 26.680 | 0/8 | 8 | 0 |
| v19, espacio libre | 0 | 29.496 | 0/8 | 1 | 7 |

Se añadieron 65.536 transiciones de entrenamiento, todas guiadas y con avance del conectoma completo. Cada una de v15 y v17 registró ocho llegadas del profesor, sin colisiones ni timeouts; no son éxitos autónomos. Los ajustes de percepción usaron pérdidas finitas y los checkpoints reprodujeron las acciones tras recarga. Las tandas v16, v18 y v19 modifican la inferencia sin actualizaciones de pesos. V18 amplía con ceros dos matrices auxiliares de seis a nueve entradas; v19 conserva sus valores exactamente. Ninguna de esas transferencias conserva las acciones anteriores, porque cambia el control o la selección de candidatos.

Todos los vuelos autónomos de esta tabla son comprobaciones en los mismos ocho mapas de optimización. No son validación independiente ni test final. Después de v19 la navegación sigue sin resolverse: reducir colisiones convirtió fallos en timeouts. Los contadores del checkpoint v13 y v14 incluyen sus comprobaciones, aunque no hubo nuevo entrenamiento físico; la tabla los separa explícitamente del entrenamiento sustantivo.

El total sustantivo completado asciende a 1.538.048 transiciones. Los 126.640 pasos de comprobación de esta tabla, dos diagnósticos de 128 pasos, el smoke PPO de 128 pasos y el demo breve de 40 pasos se contabilizan aparte. Los hashes protegidos coinciden al finalizar cada tanda. No se consumió el test reservado ni se promovió un alias.

V17 conserva las poses, velocidades, rumbos, semillas y ticks de las 8.984 muestras válidas para auditar sus referencias geométricas de centros. En v19 la selección considera candidatos hasta 150 grados de la dirección neuronal del objetivo, exige 1,5 metros de espacio estimado cuando encuentra algún candidato y usa un cono de frenado horizontal de 45 grados. Es un filtro heurístico con incertidumbre de lectura, no una garantía de seguridad; su resultado confirma que aún hubo una colisión.

La nueva distribución y sus gradientes se comprobaron; las pruebas de entrenamiento y simulación anteriores pasaron 204 casos, y las pruebas posteriores cubren los cambios de centros, frenado y contratos de checkpoint. El demo v19 se abrió, renderizó 40 pasos y cerró normalmente sin entrenar. La captura se inspeccionó; los controles se comprobaron por programa, sin afirmar una verificación física de teclado o de la ventana anatómica en esa prueba.


## Diagnóstico geométrico posterior

La auditoría de 512 estados de v17 encontró 72 errores de dirección mayores de 90 grados; 45 etiquetas quedaban fuera del hemisferio permitido por esa versión. Ampliar las direcciones candidatas y frenar no bastó para resolver el vuelo. Las pérdidas finitas y una buena mediana de ajuste pueden ocultar errores de selección que destruyen un trayecto completo.

Se probaron referencias geométricas construidas exclusivamente desde distancias, dirección de objetivo y movimiento reconstruidos de estados neuronales. El algoritmo ajusta paredes a la nube de distancias, busca aberturas, mantiene una referencia mediante odometría observada y elige desvíos locales. No recibe posiciones, semillas, cajas, paredes ni la ruta certificada. El tamaño de la habitación se conoce como parte del contrato del entorno. Es navegación geométrica explícita y no una política aprendida.

V20 a v29 fueron comprobaciones de un solo mapa de optimización. Ninguna llegó al objetivo. V30 llegó en 2.399 pasos, sin colisión, usando el lector diagnóstico que cancela la contribución recurrente. Eso es un límite de información del simulador, no evidencia de que la recurrencia biológica produzca una ventaja.

V31 conserva el cinco por ciento de la contribución recurrente proyectada, con el mismo grafo completo. En ocho mapas de optimización reutilizados consiguió cuatro llegadas, cero colisiones y cuatro timeouts, tras 29.496 transiciones de comprobación. No entrenó pesos ni generó un checkpoint. La selección geométrica y la lectura artificial forman parte de este resultado; no corresponde atribuir esas cuatro llegadas al estudiante de v19.

Las variantes de diagnóstico v20 a v31 suman 53.316 transiciones físicas, separadas del entrenamiento, sin usar el test reservado. Sus fuentes, estados y trayectorias están conservados localmente con los artefactos privados. Se siguen considerando pruebas de optimización, incluidas las variantes que fallaron.

V32 inicia una tanda acotada de percepción aprendida con 32.768 nuevas transiciones guiadas, 4.096 ajustes supervisados y hasta 32.768 transiciones de comprobación autónoma. Añade contexto global del panorama a las puntuaciones locales y cambia explícitamente el contrato de lectura a una contribución recurrente del cinco por ciento. Las observaciones siguen procediendo de estados del conectoma completo; las etiquetas de centros son supervisión privilegiada de entrenamiento. El plan protege todos los checkpoints originales y separa los vuelos del profesor de los del estudiante.


## Percepción global y aproximación separada

V32 consumió sus 32.768 transiciones guiadas y 4.096 ajustes supervisados, con nueve llegadas del profesor. El checkpoint quedó guardado con pérdidas finitas. El script falló después al calcular la auditoría porque mezcló las columnas de velocidad y frenado. Se conservan ese estado de fallo y el error original. Una comprobación separada corrigió únicamente el informe, cargó el mismo checkpoint sin entrenarlo ni modificarlo y verificó la recarga.

La mediana y el percentil 90 del error angular en 512 campos de entrenamiento fueron 1,55 y 3,40 grados, respectivamente. A pesar de ello, el vuelo autónomo llegó a cero de ocho objetivos, con ocho timeouts y ninguna colisión, tras 29.496 transiciones de comprobación. Un buen ajuste de percepción no demuestra navegación. La distancia predicha tuvo un error cuadrático medio de 1,14 metros; en 73 estados con referencia a menos de dos metros, el error fue 0,54 metros.

V33 falló antes de cualquier ajuste o transición física por una semilla de tipo NumPy incompatible con Gymnasium. V34 corrigió ese tipo y reutilizó los campos neuronales ya registrados de v32. Ajustó exclusivamente una cabeza de orientación de pared durante 1.536 actualizaciones supervisadas. Las etiquetas se derivan de las poses de entrenamiento; durante inferencia no se consultan las poses ni el mapa. No añadió entrenamiento físico ni actualizaciones PPO.

La orientación aprendida permite mantener una separación de 1,3 metros mientras se alinea con la abertura y apuntar 1,2 metros más allá cuando está alineada. En los ocho mapas de optimización reutilizados, v34 completó tres objetivos, con una colisión y cuatro timeouts, tras 28.480 transiciones de comprobación. Las pérdidas fueron finitas y la recarga reprodujo las acciones. El objetivo de navegación fiable sigue pendiente y este resultado no es una prueba independiente de generalización.

V35 conserva todos los tensores de v34 y comprueba una corrección de inferencia: usa las distancias neuronales cortas para evitar aproximarse dentro de la separación prevista cuando aún está desalineada. No añade entrenamiento ni consume el test reservado.


## Correcciones posteriores y contabilidad

Las pruebas siguen usando los ocho mapas de optimización 370000 a 370007. Se reutilizan para diagnosticar y elegir variantes; no son un test independiente. Ninguna de estas tandas consume el conjunto final reservado.

| Variante | Entrenamiento físico nuevo | Ajustes supervisados | Comprobación física | Llegadas | Colisiones | Timeouts |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| v32, contexto global | 32,768 | 4,096 | 29,496 | 0/8 | 0 | 8 |
| v34, aproximación y cruce | 0 | 1,536 | 28,480 | 3/8 | 1 | 4 |
| v35, mediana de separación | 0 | 0 | 29,496 | 0/8 | 0 | 8 |
| v37, exposición del estudiante | 32,768 | 4,096 | 29,496 | 1/8 | 2 | 5 |
| v38, ajuste aislado de distancia | 0 | 2,048 | 28,480 | 0/8 | 3 | 5 |
| v39, protección por trayectoria | 0 | 0 | 29,496 | 1/8 | 0 | 7 |
| v40, alineación temporal | 0 | 2,048 | 29,496 | 1/8 | 2 | 5 |

V35 no mejoró la aproximación: los obstáculos cercanos podían confundirse con la pared. El diagnóstico geométrico v36 tampoco mejoró v31: llegó a 1/8 objetivos con siete timeouts y sin colisiones, tras 29.496 transiciones. No entrenó una política y se conserva separado del estudiante.

V37 añadió 32.768 transiciones: 16.384 bajo acciones del estudiante y 16.384 con recuperación del profesor. Durante la recogida, el estudiante no llegó a ningún objetivo y tuvo una colisión; el profesor registró dos llegadas y ocho colisiones. La recuperación tampoco es infalible. El ajuste conjunto de dirección, distancia métrica y normal empeoró la precisión angular. V38 congeló los tensores angulares y la cabeza de orientación para aislar las pérdidas de distancia. Verificó que las puntuaciones angulares eran idénticas, pero la mejora de ajuste de distancia tampoco mejoró la navegación.

V39 conservó todos los tensores de v34 y cambió la protección de frenado a un tubo de 0,28 metros alrededor del movimiento. La prueba de geometría distingue un obstáculo lateral de uno frontal. El vuelo tuvo menos colisiones pero más timeouts; no se adopta por ello como mejora.

Los panoramas de instantes distintos no estaban alineados al girar. En los datos guardados, el cambio de orientación del objetivo entre imágenes llegó a unos 40 grados. V40 aproxima el giro usando la diferencia de orientación neuronal del objetivo y remuestrea circularmente la imagen anterior. La traslación también cambia esa orientación, por lo que no es odometría exacta. Una prueba verifica la rotación de 45 grados, la continuidad en el borde y gradientes finitos con historial vacío. Tras 2.048 ajustes sobre campos ya guardados, v40 tampoco mejoró v34. Corregir esa hipótesis no basta para dar por resuelta la navegación.

La tanda retomada añade 131.072 transiciones físicas de entrenamiento: v15, v17, v32 y v37 aportan 32.768 cada una. El uso sustantivo acumulado pasa de 1.472.512 a 1.603.584. Los ajustes de v34, v38 y v40 reutilizan registros y no añaden transiciones físicas. Las dos verificaciones PPO de 128 pasos son pruebas temporales separadas, con una actualización cada una y pérdidas finitas; no son experimentos de rendimiento.

## Inspección neuronal y demostración

La ventana anatómica fallaba al aplicar índices de neuronas sobre un gradiente con forma de historial por características. Se selecciona ahora la muestra actual y se transforma el gradiente según el lector real. Para medias neuronales se muestra sensibilidad respecto del estado recurrente; para lecturas de proyección se muestra sensibilidad respecto del impulso neuronal reconstruido, manteniendo fijo el estado anterior. Las trazas registran esa base y su condicionamiento. No se presenta como una atribución causal ni como actividad biológica medida.

Una demostración breve de v34, con el grafo completo y ventana cerebral, cerró normalmente tras 40 pasos y 40 imágenes. Se inspeccionó la captura de la habitación. Esta comprobación acredita arranque y ejecución; no aporta una llegada adicional ni verifica físicamente todas las teclas. Las pruebas dirigidas de percepción, reconstrucción, checkpoint y visualización pasaron: 25 casos, además de la comprobación anterior de 214 casos de entrenamiento y simulación.

## Mapa observado en diagnóstico

En esta etapa se probó una alternativa de planificación explícita que construye ocupación a partir de las distancias y el movimiento reconstruidos de actividad neuronal. Su interfaz no acepta el objeto del mundo, semillas, cajas, poses verdaderas ni la ruta certificada. Usa el tamaño de habitación declarado y una cuadrícula de memoria local. No es una política aprendida y sus llegadas se informan por separado. La versión final v55 y el mejor estudiante v34 se conservan como controladores distintos.


## Lectura estable para el movimiento

La deriva acumulada del mapa motivó una variante que cancela la recurrencia proyectada en los 269 canales base, incluyendo distancias cortas, objetivo y movimiento, y conserva el cinco por ciento en los 3.600 canales del panorama. La reconstrucción usa exclusivamente estados neuronales anteriores y actuales y la proyección fija conocida. Tiene una huella nueva; los checkpoints anteriores no se reinterpretan silenciosamente. Las fórmulas y el diagnóstico numérico están en [matemáticas](../MATHEMATICS.md). No es un mecanismo biológico demostrado ni evidencia de utilidad particular del cableado de la mosca.

La prueba algebraica verifica cada bloque, la recurrencia visual no nula y los reinicios independientes. La comprobación sobre el grafo completo conservó las 167.184 neuronas y 25.583.622 conexiones. La tubería PPO pasó una verificación temporal adicional de 128 transiciones y una actualización, con pérdidas finitas y recarga compatible; el archivo temporal fue eliminado. Esa tercera prueba PPO sigue separada del entrenamiento sustantivo.

Las primeras variantes de mapa v41 y v42 generaron la habitación con el segundo reset del generador. Sus semillas etiquetadas no identifican los mismos layouts canónicos de las comprobaciones anteriores; se conserva el procedimiento de generación y no se comparan esos vuelos por semilla con v34. V43 corrigió el reset explícito y guardó las cajas iniciales para auditar la identidad del layout. En los ocho mapas canónicos reutilizados llegó a 5/8 objetivos, sin colisiones y con tres timeouts. V44, con el lector estable, también llegó a 5/8, sin colisiones y con tres timeouts. Ambas usaron 29.496 transiciones de comprobación; v44 añadió su diagnóstico separado de 128 transiciones. Son algoritmos de planificación geométrica, no resultados del estudiante aprendido.

En el mapa 370000, el margen duro de ocupación dejaba solo una celda accesible alrededor de la mosca. V45 confirmó ese bloqueo. V46 convirtió el margen en un coste alto, conservando impasables las superficies observadas, y permitió avanzar, pero terminó en timeout. V47 redujo la protección lateral y alcanzó mayor progreso, pero colisionó al suavizar una esquina. V48 limitó el suavizado en los márgenes, redujo la velocidad allí y añadió frenado en tres dimensiones. Llegó a 1/8 objetivos, sin colisiones y con siete timeouts. V48 no se promovió al demo.


## Auditoría de referencias y bloqueos posteriores

Las referencias de centros usadas en entrenamiento se escogían de la geometría de la habitación. No se comprobaba su visibilidad antes de etiquetar cada imagen. Por eso deben describirse como referencias geométricas, que pueden estar ocultas, y no como centros visibles verificados. Una auditoría sobre registros existentes encontró que el rayo panorámico más próximo pasaba más allá del centro en 7.773 de 8.928 referencias de v32 y 7.679 de 9.192 de v37. Es una aproximación angular, no una prueba exacta de visibilidad. Estos datos siguen siendo de entrenamiento y no evidencia independiente de generalización.

V49 falló tras 8.480 transiciones de comprobación: una referencia neuronal predicha quedaba fuera de la cuadrícula y provocaba un error de índice. Se conservan el fallo y sus registros; no añadió entrenamiento. V50 rechaza esas referencias antes de convertirlas en índices. Llegó a 1/8 objetivos, sin colisiones y con siete timeouts, tras 28.480 transiciones.

El ajuste geométrico de v51 confundía grupos de cajas con una pared completa. Se añadió una comprobación de cobertura de superficie a v52; las ocho pruebas geométricas identifican ahora la primera pared cuando es observable. Son pruebas de geometría con entradas sintéticas, sin cerebro ni vuelo, separadas de las comprobaciones de navegación. También se corrigió el final anticipado de la búsqueda: la ruta terminaba hasta 0,96 metros antes de su referencia. V53 liberó una abertura almacenada después de cruzarla. V51, v52 y v53 siguieron sin llegar a ninguno de los ocho objetivos, con cero colisiones y ocho timeouts cada una, en 29.496 transiciones por variante. Corregir esos errores no basta para resolver el vuelo.

V54 conserva solamente el mapa observado y el objetivo, sin propuesta de abertura aprendida. Usa el lector estable, permite salir de un margen ocupado por precaución, busca la celda final exacta y mantiene una frontera abierta cuando alcanza el límite de búsqueda. Llegó a 3/8 objetivos, sin colisiones y con cinco timeouts, tras 28.480 transiciones. V55 comprueba el avance de referencias ya alcanzadas y frena en la dirección tridimensional solicitada, manteniendo el control de altura durante un giro. Llegó a 8/8 en optimización y a 13/16 en una comprobación prospectiva congelada; [informe de v55](observed-map-v55-results.md). V41 a v54 y la primera comprobación de v55 son diagnóstico sobre mapas de optimización reutilizados, con cero entrenamiento físico nuevo y cero cambios de pesos. Los hashes de los checkpoints y aliases protegidos coinciden al cerrar las tandas completadas.


La [historia de resolución](../NAVIGATION_RESOLUTION.md) reúne estos intentos y explica el paso al planificador operativo v55, sin atribuir su rendimiento a la política aprendida.
