#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Injeta data/cnpj/resumo.json em numeros.html entre marcadores <!-- cnpj:X --> (sc, br, nota)."""
import json, re, os, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'numeros.html')
R = json.load(open(os.path.join(ROOT, 'data', 'cnpj', 'resumo.json'), encoding='utf-8'))
t = open(P, encoding='utf-8').read()
MESES = {'01': 'janeiro', '02': 'fevereiro', '03': 'março', '04': 'abril', '05': 'maio', '06': 'junho', '07': 'julho', '08': 'agosto', '09': 'setembro', '10': 'outubro', '11': 'novembro', '12': 'dezembro'}
MESES_EN = {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June', '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}
ano, mes = R['pasta'].split('-')
REF = f"{MESES[mes]} de {ano}"; REF_EN = f"{MESES_EN[mes]} {ano}"


def n(v):
    return f"{v:,}".replace(',', '.')


def put(key, html):
    global t
    t, k = re.subn(r'<!-- cnpj:%s -->.*?<!-- /cnpj:%s -->' % (key, key), '<!-- cnpj:%s -->%s<!-- /cnpj:%s -->' % (key, html, key), t, count=1, flags=re.S)
    print(f"  {key}: {k}")


put('sc', '')
put('br', '')
put('nota', '')
for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, flags=re.S):
    json.loads(x)
open(P, 'w', encoding='utf-8').write(t)
print('ok', REF, 'SC setor nautico', core_total)
