#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Injeta data/rais/resumo.json em numeros.html entre marcadores <!-- rais:X --> (sc, br, nota). So vinculos (empregos), nunca contagem de estabelecimentos."""
import json, re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'numeros.html')
R = json.load(open(os.path.join(ROOT, 'data', 'rais', 'resumo.json'), encoding='utf-8'))
t = open(P, encoding='utf-8').read()
anos = sorted(R['anos']); A0, A1 = anos[-2], anos[-1]
r0, r1 = R['anos'][A0], R['anos'][A1]


def n(v):
    return f"{v:,}".replace(',', '.')


def var(a, b):
    if not a:
        return '-'
    x = round(100 * (b - a) / a)
    return ('+' if x > 0 else '') + str(x) + '%'


def put(key, html):
    global t
    t, k = re.subn(r'<!-- rais:%s -->.*?<!-- /rais:%s -->' % (key, key), '<!-- rais:%s -->%s<!-- /rais:%s -->' % (key, html, key), t, count=1, flags=re.S)
    print(f"  {key}: {k}")


put('sc', '')
put('br', '')
put('nota', '')
for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, flags=re.S):
    json.loads(x)
open(P, 'w', encoding='utf-8').write(t)
print('ok (RAIS fora da pagina)')
