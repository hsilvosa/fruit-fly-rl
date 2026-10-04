# Neural waypoint v6: resultados

El experimento completó 81.920 transiciones nuevas: 16.384 guiadas y 65.536 autónomas. Reutilizó 98.304 ejemplos anteriores de optimización y ejecutó 6.144 actualizaciones supervisadas; esas actualizaciones no son transiciones adicionales del mundo ni actualizaciones PPO. El total acumulado de entrenamiento sustantivo del proyecto es 868.352 transiciones, separado de las comprobaciones breves.

La validación autónoma en las ocho salas originales large de desarrollo terminó con cero éxitos, ocho colisiones y cero timeouts. Las semillas 430000 a 430007 se han reutilizado para diagnóstico: este resultado no es un test independiente. No se consumió el test reservado ni se promovió un alias de lanzamiento.

Las cuatro tandas del estudiante registraron cero objetivos, con 28, 39, 30 y 25 colisiones. Los fragmentos guiados conservaron las posiciones y orientaciones originales, pero duraron solo 12,8 segundos por mundo y no completaron objetivos. Los vuelos autónomos sí conservaron episodios y estado cerebral entre ajustes. Las pérdidas fueron finitas; esto no basta para demostrar navegación.

La recarga conservó todos los tensores y produjo predicciones idénticas en la misma GPU. El error máximo CPU/GPU fue 0,00000891, dentro de la tolerancia declarada. El checkpoint fuente y los seis archivos de los aliases originales conservan sus hashes. Los hashes y resultados detallados se guardaron en evidencia privada.

El [diagnóstico de control y cobertura](neural-waypoint-v6-diagnostics.md) identifica errores de giro y altura y una cobertura densa insuficiente en parte de los estados de recuperación. No demuestra que una sola causa explique todas las colisiones. La siguiente corrección amplía el campo visual y la duración de los vuelos guiados completos; todavía debe demostrar éxito autónomo.
