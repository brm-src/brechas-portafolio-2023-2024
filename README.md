# Brechas por dependencia en el Sistema Único de Evaluación Docente, 2023-2024

Código de reproducción de la tesis "Brechas por dependencia administrativa en el Sistema Único de Evaluación Docente: categorías del Portafolio en Chile, 2023-2024" (Cristian Aravena Quilodrán, Magíster en Gobierno y Dirección Pública, Universidad Autónoma de Chile, 2026).

## Qué hace

`analisis_portafolio.py` toma los totales por grupo (Tabla 2) y los porcentajes por categoría (Gráfico 10) de los informes nacionales del CPEIP, reconstruye las frecuencias y calcula el chi-cuadrado, la V de Cramér, los residuos ajustados, las diferencias A/B y A/B/C con sus intervalos, el cambio entre años y las cotas de redondeo. `salida.txt` es la salida completa de una ejecución.

## Cómo ejecutarlo

    pip install numpy scipy pandas
    python3 analisis_portafolio.py

Verificado con Python 3.14, numpy 2.5.4, scipy 1.18.1 y pandas 3.1.1.

## Fuentes de los datos

Informes de resultados nacionales del Portafolio, CPEIP (docentemas.cl): proceso 2023 (pp. 11 y 13) y proceso 2024 (pp. 13 y 15). Los datos son cifras públicas agregadas y están escritos dentro del código.
