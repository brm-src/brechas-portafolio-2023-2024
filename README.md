# Brechas por dependencia en el Sistema Único de Evaluación Docente, 2023-2024

Código de reproducción de la tesis "Brechas por dependencia administrativa en el Sistema Único de Evaluación Docente: categorías del Portafolio en Chile, 2023-2024" (Cristian Aravena Quilodrán, Magíster en Gobierno y Dirección Pública, Universidad Autónoma de Chile, 2026).

## Qué hace

`analisis_portafolio.py` toma los totales por grupo (Tabla 2) y los porcentajes por categoría (Gráfico 10) de los informes nacionales del CPEIP, reconstruye las frecuencias y calcula el chi-cuadrado, la V de Cramér, los residuos ajustados, las diferencias A/B y A/B/C con sus intervalos, el cambio entre años y las cotas de redondeo. `salida.txt` es la salida completa de una ejecución.

## Cómo ejecutarlo

    pip install numpy scipy pandas
    python3 analisis_portafolio.py

Verificado con Python 3.14, numpy 2.5.4, scipy 1.18.1 y pandas 3.1.1.

Para regenerar los CSV y comprobarlos:

```sh
python3 analisis_portafolio.py
python3 verificar_datos.py
```

## Datos CSV y correspondencia con la tesis

- [`datos/portafolio_2023.csv`](datos/portafolio_2023.csv)
- [`datos/portafolio_2024.csv`](datos/portafolio_2024.csv)

Cada archivo contiene 15 filas: tres agrupaciones por cinco categorías A-E. Son **datos agregados, no microdatos de docentes**. Conservan los porcentajes publicados sin corregirlos (algunas filas suman 99 o 101 por redondeo) y distinguen la `frecuencia_estimada`, reconstruida por el mismo código de la tesis: normalización de cada distribución a 100 y reparto entero por mayor resto. Las estimaciones no deben presentarse como conteos oficiales observados.

`n_grupo_publicado` es el denominador de la agrupación, repetido para cada categoría: no se debe sumar entre las cinco categorías. `porcentaje_publicado` está en escala 0-100. `frecuencia_estimada` sí puede sumarse. `grupo` usa MUN_SLEP (Municipal/Servicio Local), PS_AD (Particular Subvencionado/Administración Delegada) y JARDINES. La agrupación de jardines de Tabla 2 se rotula «JUNJI, Integra, VTF, CAD»; la del Gráfico 10, «JUNJI, INTEGRA, JJII Admin Pública, Admin Privada y SLE». Su correspondencia es un supuesto de la reconstrucción, no una equivalencia individual demostrada.

Los campos de página son índices **desde 1** y distinguen página física del PDF y folio impreso. Para 2023, Tabla 2 está en página física 12 (folio 11), y Gráfico 10 en página física 14 (folio 13); para 2024 están en páginas físicas y folios 13 y 15.

Se cotejaron visualmente Tabla 2 y Gráfico 10 de los dos archivos proporcionados por el autor. Sus valores coinciden con N y P del código y con la Tabla 1 y las distribuciones de categorías de la copia de tesis usada en `defensa-teleprompter-v2/tesis.docx`. La tesis analiza **2023-2024**, no 2024-2025. No se ajustaron cifras para forzar coincidencias.

**Advertencia de la fuente 2024:** sumar MUN y SLE del Gráfico 8 da 10.840, no los 10.637 de Tabla 2; los códigos de jardines dan 1.419, no 1.622. Los CSV conservan **Tabla 2**, como la tesis. El código ya evalúa la clasificación alternativa por separado; no se mezclaron ambas bases.

Identificación SHA-256 de los originales cotejados (los PDF y el documento de tesis no se publican en este repositorio):

```text
ee284f0a9a27a890bf6b77c3aa2db9cdae5078e26bb7483ab3a9ff9d5d2a7a70  Informe_Nacional_2023 (2).pdf
b595cf568ddbe073bd863a909d94bb3a6de222492ef17c35cc5d06d86a1c9b55  Informe_Nacional_2024 (7).pdf
84cb5d1f4865575798dcaa743cedd1571401f07b63e208965ac1c289b29857a4  tesis.docx
```

## Fuentes de los datos

Informes de resultados nacionales del Portafolio, CPEIP (docentemas.cl): proceso 2023 (pp. 11 y 13) y proceso 2024 (pp. 13 y 15). Los datos son cifras públicas agregadas y están escritos dentro del código.
