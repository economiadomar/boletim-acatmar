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


GR = ['Construção de embarcações', 'Manutenção e reparo de embarcações', 'Comércio e serviços náuticos', 'Portos e navegação', 'Pesca e aquicultura']
GR_EN = {'Construção de embarcações': 'Boat and ship building', 'Manutenção e reparo de embarcações': 'Boat maintenance and repair', 'Comércio e serviços náuticos': 'Nautical trade and services', 'Portos e navegação': 'Ports and navigation', 'Pesca e aquicultura': 'Fishing and aquaculture'}
rows = ''
tot0 = tot1 = 0
for g in GR:
    a = r0['grupos_sc'].get(g, {'vinculos': 0})['vinculos']; b = r1['grupos_sc'].get(g, {'vinculos': 0})['vinculos']
    tot0 += a; tot1 += b
    rows += f'      <tr><td data-en="{GR_EN[g]}">{g}</td><td class="v">{n(a)}</td><td class="v">{n(b)}</td><td class="v">{var(a, b)}</td></tr>\n'
rows += f'      <tr><td><b data-en="Total, nautical and naval chain">Total da cadeia náutica e naval</b></td><td class="v"><b>{n(tot0)}</b></td><td class="v"><b>{n(tot1)}</b></td><td class="v"><b>{var(tot0, tot1)}</b></td></tr>\n'
mun = ''
for m, d in list(r1['construcao_sc_por_municipio'].items())[:6]:
    d0 = r0['construcao_sc_por_municipio'].get(m, {'vinculos': 0})
    mun += f'      <tr><td>{m}</td><td class="v">{n(d0["vinculos"])}</td><td class="v">{n(d["vinculos"])}</td><td class="v">{var(d0["vinculos"], d["vinculos"])}</td></tr>\n'
html = (f'\n    <h3 data-en="Formal jobs in the nautical and naval chain of Santa Catarina, {A0} and {A1}" style="margin-top:1.4rem">Empregos formais na cadeia náutica e naval de Santa Catarina, {A0} e {A1}</h3>\n'
        f'    <p class="lead" data-en="Employment contracts active on Dec 31, by activity group (see methodology). Boat and ship building adds up the three construction codes, from small boats to large vessels, because shipyards register under any of them.">Vínculos de emprego ativos em 31 de dezembro, por grupo de atividade (ver metodologia). Construção de embarcações soma os três códigos de construção, do barco pequeno ao navio, porque os estaleiros se registram em qualquer um deles.</p>\n'
        f'    <div class="tw"><table>\n      <tr><th data-en="Group">Grupo</th><th>{A0}</th><th>{A1}</th><th data-en="Change">Variação</th></tr>\n{rows}    </table></div>\n'
        f'    <h3 data-en="Boat and ship building jobs in SC, by municipality" style="margin-top:1.2rem">Empregos na construção de embarcações em SC, por município</h3>\n'
        f'    <div class="tw"><table>\n      <tr><th data-en="Municipality">Município</th><th>{A0}</th><th>{A1}</th><th data-en="Change">Variação</th></tr>\n{mun}    </table></div>\n')
put('sc', html)
top = list(r1['construcao_por_uf'].items())[:6]
put('br', f'      <tr><td data-en="Formal jobs in boat and ship building, by state ({A1})">Empregos formais na construção de embarcações, por estado ({A1})</td><td class="v">' + ' · '.join(f"{u} {n(d['vinculos'])}" for u, d in top[:3]) + '</td><td data-en="' + ' · '.join(f"{u} {n(d['vinculos'])}" for u, d in top[3:6]) + '">' + ' · '.join(f"{u} {n(d['vinculos'])}" for u, d in top[3:6]) + '</td></tr>\n')
put('nota', '<li data-en="Jobs: RAIS establishment microdata, grouped by ACATMAR into boat and ship building, maintenance and repair, nautical trade and services, ports and navigation, fishing and aquaculture. Only active contracts on Dec 31 are counted. This page does not count shipyards or companies by economic activity code, because the code does not identify a shipyard: leading yards are registered as commercial vessel builders, glass articles or even tire retail, and marinas and holdings appear as builders. The verified list of shipyards is being built by ACATMAR, name by name.">Empregos: microdados da RAIS por estabelecimento, agrupados pela ACATMAR em construção de embarcações, manutenção e reparo, comércio e serviços náuticos, portos e navegação, pesca e aquicultura. Só contam vínculos ativos em 31 de dezembro. Esta página não conta estaleiros nem empresas por código de atividade (CNAE), porque o código não identifica estaleiro: estaleiros de referência estão registrados como construção de uso comercial, artigos de vidro ou até comércio de pneus, e marinas e holdings aparecem como construtoras. A lista verificada de estaleiros está sendo construída pela ACATMAR, nome a nome.</li>')
for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, flags=re.S):
    json.loads(x)
open(P, 'w', encoding='utf-8').write(t)
print('ok', A0, A1, 'construcao SC', r0['grupos_sc']['Construção de embarcações']['vinculos'], r1['grupos_sc']['Construção de embarcações']['vinculos'])
