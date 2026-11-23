"""Reproducción de los análisis principales de la tesis con cifras públicas del CPEIP.

Insumos: N por dependencia (Tabla 2 de cada informe) y porcentajes A-E por dependencia
(Gráfico 10). Las frecuencias se derivan de ambas cifras oficiales y dependen de que
correspondan a los mismos grupos; son estimaciones, no conteos publicados.

Requiere: numpy, scipy, pandas.  Uso: python analisis_portafolio.py
Escribe en pantalla los resultados principales y guarda el detalle en resultados.json.
"""
import csv
import json
from pathlib import Path
import numpy as np
import pandas as pd
import scipy
from scipy.optimize import linprog
from scipy.stats import chi2, chi2_contingency, norm

N = {2023: [27766, 17148, 2361], 2024: [10637, 12617, 1622]}
N_ALT_2024 = [10840, 12617, 1419]          # suma de códigos del Gráfico 8 (2024)
P = {2023: [[10, 42, 27, 13, 7], [13, 44, 25, 12, 7], [8, 28, 24, 21, 18]],
     2024: [[4, 41, 30, 17, 8], [7, 50, 27, 12, 5], [8, 39, 26, 17, 10]]}
G = ['MUN_SLEP', 'PS_AD', 'JARDINES']
CAT = list('ABCDE')
REG = {'Arica y Parinacota': (719, 359), 'Tarapacá': (708, 451), 'Antofagasta': (1150, 552),
       'Atacama': (916, 357), 'Coquimbo': (2466, 1379), 'Valparaíso': (5187, 2531),
       'Metropolitana': (12845, 7890), "O'Higgins": (2852, 1449), 'Maule': (3964, 1802),
       'Ñuble': (2074, 1006), 'Biobío': (5309, 2351), 'Araucanía': (3558, 1939),
       'Los Ríos': (1545, 798), 'Los Lagos': (3054, 1501), 'Aysén': (420, 276), 'Magallanes': (508, 235)}
OUT = {'versiones': {'numpy': np.__version__, 'scipy': scipy.__version__,
                     'pandas': pd.__version__}}


def derivar_frecuencias(pct, n):
    """Ajusta cada fila a 100% y reparte enteros por mayor resto: cada fila suma exactamente su N."""
    pct = np.array(pct, float)
    out = []
    for row, total in zip(pct, n):
        exact = row / row.sum() * total
        base = np.floor(exact).astype(int)
        faltan = int(total - base.sum())
        base[np.argsort(-(exact - base))[:faltan]] += 1
        out.append(base)
    return np.array(out)


def asociacion(T):
    c, p, gl, E = chi2_contingency(T, correction=False)
    k = min(T.shape) - 1
    return dict(chi2=c, gl=int(gl), p=p, V=float(np.sqrt(c / (T.sum() * k))), esperada_min=float(E.min())), E


def dif_prop(T, i, j, hasta):
    a = T[:, :hasta].sum(1) / T.sum(1)
    n = T.sum(1)
    d = a[i] - a[j]
    se = np.sqrt(a[i] * (1 - a[i]) / n[i] + a[j] * (1 - a[j]) / n[j])
    return dict(dif=100 * d, li=100 * (d - 1.96 * se), ls=100 * (d + 1.96 * se), se=100 * se)


def filas_factibles(pub):
    """Restricciones: publicado - 0,5 <= verdadero <= publicado + 0,5 y cada fila suma 100."""
    pub = np.array(pub, float)
    lo, hi = np.clip(pub - 0.5, 0, None), pub + 0.5
    return lo, hi


def muestrear_fila(lo, hi, rng):
    while True:
        x = rng.uniform(lo[:4], hi[:4])
        ult = 100 - x.sum()
        if lo[4] <= ult <= hi[4]:
            return np.append(x, ult)


def cotas_dif_AB(y):
    """Cotas exactas (programación lineal) de A/B PS/AD menos A/B MUN/SLEP bajo redondeo y suma 100."""
    lo = np.concatenate([filas_factibles(P[y][g])[0] for g in (0, 1)])
    hi = np.concatenate([filas_factibles(P[y][g])[1] for g in (0, 1)])
    c = np.zeros(10); c[5:7] = 1; c[0:2] = -1                 # (A+B)_PS - (A+B)_MUN
    Aeq = np.zeros((2, 10)); Aeq[0, :5] = 1; Aeq[1, 5:] = 1
    mn = linprog(c, A_eq=Aeq, b_eq=[100, 100], bounds=list(zip(lo, hi)))
    mx = linprog(-c, A_eq=Aeq, b_eq=[100, 100], bounds=list(zip(lo, hi)))
    return float(mn.fun), float(-mx.fun), (mn.x, mx.x)


rng = np.random.default_rng(2026)
T = {y: derivar_frecuencias(P[y], N[y]) for y in (2023, 2024)}
Path('datos').mkdir(exist_ok=True)
for y in (2023, 2024):
    with open(f'datos/portafolio_{y}.csv', 'w', encoding='utf-8', newline='') as archivo:
        writer = csv.writer(archivo, lineterminator='\n')
        writer.writerow(['anio', 'grupo', 'categoria', 'n_grupo_publicado',
                         'porcentaje_publicado', 'frecuencia_estimada',
                         'pagina_pdf_tabla2', 'folio_tabla2', 'pagina_pdf_grafico10', 'folio_grafico10'])
        for g, grupo in enumerate(G):
            for c, categoria in enumerate(CAT):
                paginas = (12, 11, 14, 13) if y == 2023 else (13, 13, 15, 15)
                writer.writerow([y, grupo, categoria, N[y][g], P[y][g][c], int(T[y][g, c]), *paginas])
OUT['frecuencias'] = {str(y): T[y].tolist() for y in T}
OUT['nacional_derivada'] = {str(y): (T[y].sum(0) / T[y].sum() * 100).tolist() for y in T}
OUT['region'] = {r: dict(n23=a, p23=100 * a / 47275, n24=b, p24=100 * b / 24876) for r, (a, b) in REG.items()}

for y in (2023, 2024):
    R = {}
    for nombre, filas in (('tres', slice(0, 3)), ('escolar', slice(0, 2))):
        R[nombre], E = asociacion(T[y][filas])
        if nombre == 'tres':
            n = T[y].sum(); Rm = T[y].sum(1, keepdims=True) / n; Cm = T[y].sum(0, keepdims=True) / n
            R['residuos'] = ((T[y] - E) / np.sqrt(E * (1 - Rm) * (1 - Cm))).tolist()
            R['esperadas'] = E.tolist()
        R[nombre]['p_deff3'] = float(chi2.sf(R[nombre]['chi2'] / 3, R[nombre]['gl']))
    R['AB'] = {f'{G[i]}-{G[j]}': dif_prop(T[y], i, j, 2) for i, j in ((1, 0), (1, 2), (0, 2))}
    R['ABC'] = {f'{G[i]}-{G[j]}': dif_prop(T[y], i, j, 3) for i, j in ((1, 0), (1, 2), (0, 2))}
    R['AB_grupo'] = (T[y][:, :2].sum(1) / T[y].sum(1) * 100).tolist()
    R['ABC_grupo'] = (T[y][:, :3].sum(1) / T[y].sum(1) * 100).tolist()
    R['DE_grupo'] = (T[y][:, 3:].sum(1) / T[y].sum(1) * 100).tolist()  # bajo logro (D o E)
    R['mediana'] = [CAT[int(np.searchsorted(np.cumsum(f) / f.sum(), 0.5))] for f in T[y]]  # categoría mediana
    Te = T[y][:2]; Ee = asociacion(Te)[1]; ne = Te.sum()  # residuos de la tabla escolar (2 x 5)
    R['residuos_escolar'] = ((Te - Ee) / np.sqrt(Ee * (1 - Te.sum(1, keepdims=True) / ne) * (1 - Te.sum(0, keepdims=True) / ne))).tolist()
    OUT[str(y)] = R

# cambio específico de la diferencia A/B (sector escolar) entre años
d23, d24 = OUT['2023']['AB']['PS_AD-MUN_SLEP'], OUT['2024']['AB']['PS_AD-MUN_SLEP']
inc = d24['dif'] - d23['dif']; se = np.sqrt(d23['se'] ** 2 + d24['se'] ** 2)
OUT['cambio_AB'] = dict(incremento=inc, li=inc - 1.96 * se, ls=inc + 1.96 * se, z=inc / se, p=float(2 * norm.sf(abs(inc / se))))


# sensibilidad al redondeo: cada porcentaje verdadero dentro de ±0,5 y cada fila suma 100
SENS = {}
for y in (2023, 2024):
    lo_hi = [filas_factibles(P[y][g]) for g in range(3)]
    sims = {'V_tres': [], 'V_escolar': [], 'dif_AB': [], 'p_tres': [], 'p_escolar': []}
    for _ in range(10000):
        pct = np.array([muestrear_fila(lo, hi, rng) for lo, hi in lo_hi])
        F = pct / 100 * np.array(N[y])[:, None]
        a3 = asociacion(F)[0]; a2 = asociacion(F[:2])[0]
        sims['V_tres'].append(a3['V']); sims['V_escolar'].append(a2['V']); sims['p_tres'].append(a3['p']); sims['p_escolar'].append(a2['p'])
        ab = F[:, :2].sum(1) / F.sum(1) * 100; sims['dif_AB'].append(ab[1] - ab[0])
    mn, mx, _ = cotas_dif_AB(y)
    SENS[str(y)] = {k: dict(min=float(np.min(v)), max=float(np.max(v))) for k, v in sims.items()}
    SENS[str(y)]['dif_AB_cotas_exactas'] = dict(min=mn, max=mx)
mn23, mx23, _ = cotas_dif_AB(2023); mn24, mx24, _ = cotas_dif_AB(2024)
SENS['incremento_cotas'] = dict(min=mn24 - mx23, max=mx24 - mn23)
def cotas_cambio_AB(g):
    """Cotas exactas del cambio A/B (2024 menos 2023) de un grupo bajo redondeo y suma 100."""
    lo = np.concatenate([filas_factibles(P[y][g])[0] for y in (2023, 2024)])
    hi = np.concatenate([filas_factibles(P[y][g])[1] for y in (2023, 2024)])
    c = np.zeros(10); c[5:7] = 1; c[0:2] = -1
    Aeq = np.zeros((2, 10)); Aeq[0, :5] = 1; Aeq[1, 5:] = 1
    mn = linprog(c, A_eq=Aeq, b_eq=[100, 100], bounds=list(zip(lo, hi)))
    mx = linprog(-c, A_eq=Aeq, b_eq=[100, 100], bounds=list(zip(lo, hi)))
    return dict(min=float(mn.fun), max=float(-mx.fun))
SENS['cambio_AB_grupo_cotas'] = {G[g]: cotas_cambio_AB(g) for g in (0, 1)}
OUT['sensibilidad_redondeo'] = SENS
alt = derivar_frecuencias(P[2024], N_ALT_2024)
OUT['clasificacion_alternativa_2024'] = dict(V_tres=asociacion(alt)[0]['V'], V_escolar=asociacion(alt[:2])[0]['V'],
                                             dif_AB=dif_prop(alt, 1, 0, 2)['dif'])

json.dump(OUT, open('resultados.json', 'w'), ensure_ascii=False, indent=1, default=float)

# ---------------- salida legible ----------------
print('Versiones:', OUT['versiones'])
for y in (2023, 2024):
    R = OUT[str(y)]
    print(f'\n===== {y} =====')
    print(pd.DataFrame(T[y], G, CAT).assign(Total=T[y].sum(1)))
    for nombre in ('tres', 'escolar'):
        a = R[nombre]
        print(f"{nombre}: chi2={a['chi2']:.1f} gl={a['gl']} p={a['p']:.1e} V={a['V']:.3f} "
              f"esperada mínima={a['esperada_min']:.0f}; p con efecto de diseño 3={a['p_deff3']:.1e}")
    print('Residuos ajustados\n', pd.DataFrame(np.round(R['residuos'], 1), G, CAT))
    print('Residuos ajustados, tabla escolar\n', pd.DataFrame(np.round(R['residuos_escolar'], 1), G[:2], CAT))
    print('A/B por grupo (%):', np.round(R['AB_grupo'], 1), ' A/B/C por grupo (%):', np.round(R['ABC_grupo'], 1))
    for k, v in R['AB'].items():
        print(f"A/B {k}: {v['dif']:.1f} pp (IC95 {v['li']:.1f} a {v['ls']:.1f})")
    for k, v in R['ABC'].items():
        print(f"A/B/C {k}: {v['dif']:.1f} pp (IC95 {v['li']:.1f} a {v['ls']:.1f})")
    print('D/E por grupo (%):', np.round(R['DE_grupo'], 1), ' Categoría mediana por grupo:', R['mediana'])
print('\nCambio de A/B por grupo, 2024 menos 2023 (pp):', np.round(np.array(OUT['2024']['AB_grupo']) - np.array(OUT['2023']['AB_grupo']), 2) + 0.0)
c = OUT['cambio_AB']
print(f"\nCambio de la diferencia A/B escolar: {c['incremento']:.2f} pp (IC95 {c['li']:.2f} a {c['ls']:.2f}), p={c['p']:.1e}")
r3 = 3 ** 0.5  # efecto de diseño de 3: los errores estándar se multiplican por su raíz
ic3 = lambda dif, ee: (round(float(dif - 1.96 * r3 * ee), 1), round(float(dif + 1.96 * r3 * ee), 1))
print('Efecto de diseño 3, intervalos A/B escolar (pp): 2023', ic3(d23['dif'], d23['se']), '| 2024', ic3(d24['dif'], d24['se']), '| aumento', ic3(inc, se))
p23 = np.array(OUT['2023']['AB_grupo']); n24 = np.array(N[2024])
print('A/B nacional de 2024 con las proporciones por grupo de 2023 (%):', round(float((p23 * n24).sum() / n24.sum()), 1))
for y in ('2023', '2024'):
    s = SENS[y]
    print(f"Redondeo {y}: V tres {s['V_tres']['min']:.3f}-{s['V_tres']['max']:.3f}; V escolar {s['V_escolar']['min']:.3f}-{s['V_escolar']['max']:.3f}; "
          f"p máx {max(s['p_tres']['max'], s['p_escolar']['max']):.1e}; dif A/B simulada {s['dif_AB']['min']:.2f}-{s['dif_AB']['max']:.2f}; cotas exactas {s['dif_AB_cotas_exactas']['min']:.2f}-{s['dif_AB_cotas_exactas']['max']:.2f}")
print(f"Incremento A/B, cotas por redondeo: {SENS['incremento_cotas']['min']:.2f} a {SENS['incremento_cotas']['max']:.2f} pp")
print('Cambio A/B por grupo 2024 menos 2023, cotas por redondeo (pp):', {k: (round(v['min'], 2), round(v['max'], 2)) for k, v in SENS['cambio_AB_grupo_cotas'].items()})
print('Clasificación alternativa 2024:', {k: round(v, 3) for k, v in OUT['clasificacion_alternativa_2024'].items()})
print('Distribución nacional derivada (%):', {y: np.round(v, 2).tolist() for y, v in OUT['nacional_derivada'].items()})

# homogeneidad de la asociación entre años (tabla escolar): modelo log-lineal sin interacción año × agrupación × categoría
X = np.array([T[2023][:2], T[2024][:2]], float); F = np.ones_like(X)
for _ in range(1000):  # ajuste proporcional iterativo a los tres márgenes de dos vías
    for eje in (0, 1, 2): F *= X.sum(eje, keepdims=True) / F.sum(eje, keepdims=True)
G2 = float(2 * (X * np.log(X / F)).sum())
print(f'\nHomogeneidad entre años (escolar): G2={G2:.1f} gl=4 p={chi2.sf(G2, 4):.1e}')
# odds ratio acumulados de PS/AD frente a MUN/SLEP por umbral (A; A-B; A-C; A-D); descriptivos
for y in (2023, 2024):
    t = T[y][:2]; print(f'Odds acumulados {y}:', [round(float((t[1, :k].sum() / t[1, k:].sum()) / (t[0, :k].sum() / t[0, k:].sum())), 2) for k in range(1, 5)])
# efecto de diseño con que cada resultado dejaría de ser significativo (alfa = 0,05), bajo perturbación uniforme
print('Efecto de diseño crítico: chi2 escolar 2023', round(OUT['2023']['escolar']['chi2'] / chi2.isf(0.05, 4), 1), '| aumento A/B', round((c['z'] / 1.96) ** 2, 1))
