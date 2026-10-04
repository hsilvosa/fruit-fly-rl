# DiagnÃ³stico durante neural-waypoint-v6

Este diagnÃ³stico lee datos de optimizaciÃ³n ya recogidos. No aÃ±ade transiciones de vuelo, no modifica checkpoints y no usa el test reservado. La ejecuciÃ³n conserva su configuraciÃ³n original mientras estÃ¡ activa.

## Control y percepciÃ³n

Las tres primeras tandas autÃ³nomas, de 16.384 transiciones cada una, registraron cero Ã©xitos y 28, 39 y 30 colisiones. Estos resultados de entrenamiento no son validaciÃ³n independiente.

En las dos primeras tandas, el error cuadrÃ¡tico medio de las acciones ejecutadas frente a las correcciones de la guÃ­a fue aproximadamente 0,78 y 0,74 en giro, y 0,52 y 0,53 en control vertical. La actividad neuronal era finita y variaba entre observaciones. Esto descarta una entrada constante en esas muestras, pero no demuestra que la representaciÃ³n permita resolver todos los estados.

Un anÃ¡lisis posterior del checkpoint student-round-1 sobre muestras de esos mismos datos produjo errores de giro de 0,39 y 0,34. Son datos usados para ajustar el modelo: esos errores tampoco prueban generalizaciÃ³n ni Ã©xito de navegaciÃ³n.

## Cobertura visual

En muestras de 1.024 filas por tanda, el punto local usado como etiqueta por la guÃ­a quedÃ³ fuera del abanico visual denso en el 38,6% y el 30,5% de las observaciones autÃ³nomas. El abanico apunta hacia el objetivo final y cubre 150 grados horizontales; los sensores generales cubren otras direcciones con menor resoluciÃ³n y menor alcance. Estar fuera del abanico no implica que todos los sensores sean ciegos ni identifica por sÃ­ solo la causa de cada colisiÃ³n.

Se comprobÃ³ ademÃ¡s la direcciÃ³n del centro de la siguiente abertura geomÃ©trica sobre 128 observaciones existentes. En el 10,9% de ellas, el rayo mÃ¡s cercano del abanico estaba a mÃ¡s de diez grados. Un prototipo panorÃ¡mico de 1.800 rayos redujo esa proporciÃ³n al 0,8% con elevaciones de menos 60 a mÃ¡s 60 grados. Es una medida estÃ¡tica de cobertura, no una comparaciÃ³n de vuelos ni de aprendizaje.

## Prototipo aislado

El prototipo final amplÃ­a la elevaciÃ³n a menos 84 y mÃ¡s 84 grados, conserva 72 columnas alrededor de todo el cuerpo y usa 25 filas. Los rayos miden la primera superficie visible hasta 24 unidades; no reciben centros de aberturas, rutas ni Ã­ndices de progreso.

La integraciÃ³n estÃ¡tica con el MaleCNS completo conservÃ³ 167.184 neuronas y 25.583.622 conexiones. Produjo 3.869 grupos de actividad por observaciÃ³n, con valores finitos y resets independientes. Se comprobaron las dimensiones del controlador, gradientes finitos y la continuidad circular del procesamiento horizontal. No se ejecutaron pasos fÃ­sicos ni actualizaciones del optimizador en estas comprobaciones.

El prototipo vive en private y todavÃ­a no es la interfaz de producciÃ³n ni un checkpoint entrenado. La siguiente correcciÃ³n debe comprobar vuelos completos desde posiciones y orientaciones originales, conservar episodios entre ajustes y mantener una validaciÃ³n separada del test reservado. Ampliar los sensores no basta para declarar resuelto el problema.
