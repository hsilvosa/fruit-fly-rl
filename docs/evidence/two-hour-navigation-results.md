# Resultados de la ventana adicional de dos horas

El plazo autorizado termina el 4 de octubre de 2026 a las 20:40:52 UTC (22:40:52 de Madrid). Las tandas y sus evaluaciones han terminado antes del plazo. La navegación autónoma en los mapas grandes originales sigue sin resolverse.

| Experimento | Transiciones nuevas | Objetivos en desarrollo | Colisiones | Timeouts |
| --- | ---: | ---: | ---: | ---: |
| Cobertura panorámica v8 | 301.056 | 0/8 | 8 | 0 |
| Atención direccional v9 | 32.768 | 0/8 | 8 | 0 |
| Guía con anticipación v10 | 163.840 | 0/8 | 0 | 8 |
| Percepción de distancia v12 | 8.192 | 0/8 | 1 | 7 |

Se añadieron 505.856 transiciones desde v8. La tanda v7, iniciada antes de esta ventana, terminó sus 98.304 transiciones pero falló al finalizar el informe por una diferencia entre separadores de rutas. Se corrigió esa búsqueda y se recuperó una evaluación separada sin modificar sus pesos: 0/8, ocho colisiones. El total sustantivo completado del proyecto es 1.472.512 transiciones; los pasos de verificación se contabilizan aparte.

Los ocho mapas de desarrollo se reutilizaron para diagnosticar las correcciones. No son una prueba independiente de generalización. Ningún candidato cumplió el criterio de selección y no se ejecutó el test reservado. Tampoco se promovió ningún alias original.

En v8 el profesor alcanzó 64 objetivos; en v10 alcanzó 35. Son vuelos guiados con geometría privilegiada durante entrenamiento, no éxitos del estudiante. Las tandas autónomas de optimización v8, v9, v10 y v12 no alcanzaron objetivos. Los optimizadores registraron pérdidas finitas y las recargas reprodujeron los tensores y acciones comprobados. Eso verifica la ejecución, pero no acredita una navegación útil.

La atención direccional evita comprimir toda la imagen panorámica en una única media; la guía v10 avanza sobre la ruta sin exigir detenerse en cada vértice; v12 elimina el canal panorámico de velocidad de aproximación de su encoder visual. Estas intervenciones no produjeron llegadas en desarrollo. No se ha aislado una causa única ni demostrado una ventaja biológica.

Se integró el cálculo de sensores por lotes en CUDA y su caché de episodio. Las comprobaciones contrastan geometría con NumPy, reinicios independientes, gradientes finitos y compatibilidad de checkpoints. Se mantienen los 167.184 neurones y 25.583.622 conexiones del grafo completo. La inspección breve del último demo confirmó una escena renderizada y actividad finita durante 40 pasos; no fue una evaluación de navegación ni una prueba manual de todos los controles.

Los hashes de fuentes congeladas, checkpoints fuente y los seis archivos de alias originales se conservaron, según las auditorías detalladas privadas. El último checkpoint experimental es `runs/training/distance-only-perception-v12/policy.zip`, SHA256 `eaded4b6b600be5bd563a1b23907e727cf21d0e1b6d1def6d1e93dc6a06456ea`. El manifiesto local `runs/latest-large-demo.json` lo identifica; `launch-panorama.ps1` comprueba su hash antes de abrirlo.

Desde la carpeta del proyecto:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\launch-panorama.ps1
```

Este demo usa al estudiante autónomo, sin profesor ni entrenamiento. Sigue siendo experimental. Los resultados detallados, trayectorias y pérdidas se conservan localmente en `private` y `runs/training`. El watchdog aplica el plazo mediante PID, fecha de inicio y ejecutable, sin reiniciar ninguna tarea. Al cumplirse el plazo se pausa el trabajo por petición del usuario.

Antes de otra tanda conviene estudiar los estados donde el estudiante se detiene o gira, comprobar qué información conserva la proyección neuronal cerca de una abertura y mejorar la cobertura de esos estados. Cualquier intervención nueva necesita presupuesto y evaluación separados; el resultado actual no permite marcar la navegación completa.
