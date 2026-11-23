"""Ejecutar después de analisis_portafolio.py: python verificar_datos.py."""
import csv
import json
from pathlib import Path

base = Path(__file__).resolve().parent
resultados = json.loads((base / 'resultados.json').read_text())
# Transcripción cotejada visualmente con Tabla 2 y Gráfico 10 de los PDF originales.
fuente = {
    2023: ([27766, 17148, 2361], [[10, 42, 27, 13, 7], [13, 44, 25, 12, 7], [8, 28, 24, 21, 18]], (12, 11, 14, 13)),
    2024: ([10637, 12617, 1622], [[4, 41, 30, 17, 8], [7, 50, 27, 12, 5], [8, 39, 26, 17, 10]], (13, 13, 15, 15)),
}
for anio, (totales, porcentajes, paginas) in fuente.items():
    with (base / f'datos/portafolio_{anio}.csv').open(newline='', encoding='utf-8') as archivo:
        filas = list(csv.DictReader(archivo))
    assert len(filas) == 15
    assert len({(f['grupo'], f['categoria']) for f in filas}) == 15
    for g, grupo in enumerate(['MUN_SLEP', 'PS_AD', 'JARDINES']):
        grupo_filas = [f for f in filas if f['grupo'] == grupo]
        assert [f['categoria'] for f in grupo_filas] == list('ABCDE')
        assert sum(int(f['frecuencia_estimada']) for f in grupo_filas) == totales[g]
        for c, f in enumerate(grupo_filas):
            assert int(f['anio']) == anio
            assert int(f['n_grupo_publicado']) == totales[g]
            assert int(f['porcentaje_publicado']) == porcentajes[g][c]
            assert int(f['frecuencia_estimada']) == resultados['frecuencias'][str(anio)][g][c]
            assert tuple(int(f[k]) for k in ['pagina_pdf_tabla2', 'folio_tabla2', 'pagina_pdf_grafico10', 'folio_grafico10']) == paginas
    print(f'{anio}: 15 filas; porcentajes y totales oficiales; frecuencias idénticas a resultados.json; N={sum(totales)}')
