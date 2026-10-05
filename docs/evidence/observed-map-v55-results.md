# Observed neuronal map v55

La versión congelada completó ocho de ocho mapas de optimización reutilizados, sin colisiones ni timeouts. En una comprobación prospectiva de desarrollo de 16 habitaciones nuevas completó 13, sin colisiones y con tres timeouts: 81,25% de éxito, con intervalo de Wilson del 95% de 57.0 a 93.4%. Es una muestra pequeña del generador `large`, no una garantía sobre cualquier mapa ni el test final reservado.

Es planificación geométrica explícita desde actividad del conectoma completo, con control de vuelo y sin pesos de movimiento aprendidos. No es éxito de PPO ni demuestra una ventaja biológica. El mejor estudiante aprendido de esta tanda sigue en 3/8 sobre optimización reutilizada; el aprendizaje fiable sigue pendiente.

## Método y protocolo

El controlador reconstruye distancias, objetivo y movimiento desde estados neuronales anteriores y actuales, construye ocupación y odometría y busca una ruta. No recibe poses verdaderas, cajas, semillas ni rutas certificadas. Conoce el contrato de habitación de 48 x 48 x 16 y dispone del objetivo sintético observado, como las políticas anteriores. Conserva las 167.184 neuronas y 25.583.622 conexiones recurrentes. El lector cancela recurrencia en los 269 canales base y conserva el 5% en los panoramas: una transformación artificial, documentada en [matemáticas](../MATHEMATICS.md).

V55 se eligió usando ocho mapas de optimización. Antes de iniciar desarrollo se congelaron código y 16 semillas nuevas, 8500000 a 8500015. No se ajustó el controlador entre esos vuelos. Los fallos son timeouts en 8500011, 8500012 y 8500013. Los restantes 13 terminaron a menos de 0,45 metros del objetivo, conforme a la condición física original. El progreso parcial no equivale a una llegada.

| Tanda | Transiciones de comprobación | Llegadas | Colisiones | Timeouts |
| --- | ---: | ---: | ---: | ---: |
| Optimización reutilizada | 25.168 | 8/8 | 0 | 0 |
| Desarrollo prospectivo | 56.544 | 13/16 | 0 | 3 |

No se añadieron transiciones de entrenamiento ni actualizaciones de pesos en estas dos tandas. El contador físico incluye todo el lote, también elementos que habían terminado y avanzaban con acción cero. No se consumió ningún conjunto reservado ni se promovieron aliases. Los planes, código congelado, geometría inicial de auditoría, trayectorias y resultados por episodio se conservan en registros locales. Esa geometría de auditoría no se entrega al controlador.

Los bloqueos corregidos incluían un margen de mapa que encerraba el inicio, una búsqueda que terminaba antes de la referencia, el seguimiento de celdas ya alcanzadas y un freno frontal que impedía subir o bajar. El control vertical se mantiene durante el giro. La búsqueda tiene un límite de expansiones y puede elegir desvíos insuficientes; los tres timeouts de desarrollo muestran ese límite.

## Conservación de aliases

Los hashes SHA-256 siguientes coinciden antes y después. También se verificaron los checkpoints fuente y experimentales protegidos. No se sobrescribió ningún alias original.

| Archivo | SHA-256 antes y después |
| --- | --- |
| `runs/dense-flight-policy.json` | `0ca02c89a6e17d16cfd949a56d46909cdf8638758a4536953e3e3d8ecef5e2db` |
| `runs/dense-flight-policy.zip` | `085963d6e95b2a25647e3e6dd7ad2dc61f8f3c61bbfaaf3ce0db2c067a287d66` |
| `runs/dense-policy.json` | `88c3e01eb7926dedfc1679f23b4a92c3783384782ad4203013afa8d38fe4e3c3` |
| `runs/dense-policy.zip` | `db0839a921ae8775bbad9dbea62c28ab3752d33dad0e8edcfa72c7dc1318cab6` |
| `runs/navigation-policy.json` | `aa47f7ef830c491958a16bd121497c703d689b2a9717c566ad9888de5815460f` |
| `runs/navigation-policy.zip` | `2aa3469b6c56fa7f29c56399a7737b29c1870432e005714782d8efe23bf6be01` |

## Demo y límites

`launch-observed-map.cmd` abre esta versión con ventana cerebral separada. No carga un checkpoint PPO ni inicia entrenamiento. El visor identifica el planificador, reinicia mapa y odometría en reset, sala nueva y fin de episodio, y archiva especificación y código junto a estados, acciones y actividad opcional. El replay reproduce estados guardados sin ejecutar cerebro o controlador. La sensibilidad por gradiente se indica como no disponible para este algoritmo; los puntos anatómicos muestran actividad modelada real.

Dos arranques breves de 40 pasos verificaron controles y cierre. Se inspeccionaron las capturas de habitación y cerebro, y el archivo de vuelo pasó su auditoría sin errores ni advertencias. Estos 80 pasos son verificación, no navegación adicional ni entrenamiento. La interfaz conserva Shift para acelerar el tiempo simulado. El alcance actual es `large` con dinámica coordinada; no se extrapola a `maze` u otros tamaños.


El vuelo completo desde el visor alcanzó el objetivo del mapa de optimización 370000 en 2.857 pasos, sin colisión. Después reinició automáticamente el episodio y la memoria del controlador. Cerró tras 3.200 pasos de verificación física; el archivo completo pasó auditoría sin errores ni advertencias. Esta repetición del mapa conocido no se cuenta como otro objetivo de desarrollo independiente. La suite completa pasó 265 tests, y el lanzador Windows respondió correctamente a `--help`.
