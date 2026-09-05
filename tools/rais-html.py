#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Injeta data/rais/resumo.json em numeros.html entre marcadores <!-- rais:X --> (sc, br, nota)."""
import json, re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'numeros.html')
R = json.load(open(os.path.join(ROOT, 'data', 'rais', 'resumo.json'), encoding='utf-8'))
t = open(P, encoding='utf-8').read()
anos = sorted(R['anos'])
A0, A1 = anos[-2], anos[-1]
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


GR = ['Indústria náutica', 'Comércio e serviços náuticos', 'Indústria naval', 'Portos e navegação', 'Pesca e aquicultura']
GR_EN = {'Indústria náutica': 'Boatbuilding and nautical industry', 'Comércio e serviços náuticos': 'Nautical trade and services', 'Indústria naval': 'Shipbuilding', 'Portos e navegação': 'Ports and navigation', 'Pesca e aquicultura': 'Fishing and aquaculture'}
rows = ''
tot0 = tot1 = te0 = te1 = 0
for g in GR:
    a = r0['grupos_sc'].get(g, {'estab': 0, 'vinculos': 0}); b = r1['grupos_sc'].get(g, {'estab': 0, 'vinculos': 0})
    tot0 += a['vinculos']; tot1 += b['vinculos']; te0 += a['estab']; te1 += b['estab']
    rows += f'      <tr><td data-en="{GR_EN[g]}">{g}</td><td class="v">{n(a["estab"])}</td><td class="v">{n(a["vinculos"])}</td><td class="v">{n(b["estab"])}</td><td class="v">{n(b["vinculos"])}</td><td class="v">{var(a["vinculos"], b["vinculos"])}</td></tr>\n'
rows += f'      <tr><td><b data-en="Total, nautical and naval chain">Total da cadeia náutica e naval</b></td><td class="v"><b>{n(te0)}</b></td><td class="v"><b>{n(tot0)}</b></td><td class="v"><b>{n(te1)}</b></td><td class="v"><b>{n(tot1)}</b></td><td class="v"><b>{var(tot0, tot1)}</b></td></tr>\n'
# por CNAE (industria nautica) SC
cn = ''
for c, d in sorted(r1['sc_por_cnae'].items(), key=lambda x: -x[1]['vinculos']):
    if d['grupo'] != 'Indústria náutica':
        continue
    d0 = r0['sc_por_cnae'].get(c, {'estab': 0, 'vinculos': 0})
    cn += f'      <tr><td>{c[:4]}-{c[4]}/{c[5:]}</td><td>{d["desc"]}</td><td class="v">{n(d0["vinculos"])}</td><td class="v">{n(d["vinculos"])}</td><td class="v">{n(d["estab"])}</td></tr>\n'
# municipios
mun = ''
for m, d in list(r1['industria_nautica_sc_por_municipio'].items())[:10]:
    d0 = r0['industria_nautica_sc_por_municipio'].get(m, {'estab': 0, 'vinculos': 0})
    mun += f'      <tr><td>{m}</td><td class="v">{n(d0["vinculos"])}</td><td class="v">{n(d["vinculos"])}</td><td class="v">{n(d["estab"])}</td><td class="v">{var(d0["vinculos"], d["vinculos"])}</td></tr>\n'
# ranking UF 3012100
uf = ''
for u, d in list(r1['construcao_esporte_lazer_por_uf'].items())[:8]:
    d0 = r0['construcao_esporte_lazer_por_uf'].get(u, {'estab': 0, 'vinculos': 0})
    uf += f'      <tr><td>{u}</td><td class="v">{n(d0["vinculos"])}</td><td class="v">{n(d["vinculos"])}</td><td class="v">{n(d["estab"])}</td></tr>\n'
html = (f'\n    <h3 data-en="Formal jobs in the nautical and naval chain of Santa Catarina (RAIS {A0} and {A1}, ACATMAR extraction)" style="margin-top:1.4rem">Empregos formais na cadeia náutica e naval de Santa Catarina (RAIS {A0} e {A1}, extração ACATMAR)</h3>\n'
        f'    <p class="lead" data-en="Establishments with at least one active employment contract on Dec 31 and active contracts, by group of CNAE subclasses defined by ACATMAR (see methodology). Read directly from the public RAIS microdata of the Ministry of Labor.">Estabelecimentos com pelo menos um vínculo ativo em 31 de dezembro e vínculos ativos, por grupo de subclasses CNAE definido pela ACATMAR (ver metodologia). Lidos direto dos microdados públicos da RAIS, do Ministério do Trabalho.</p>\n'
        f'    <div class="tw"><table>\n      <tr><th data-en="Group">Grupo</th><th data-en="Establishments {A0}">Estab. {A0}</th><th data-en="Jobs {A0}">Vínculos {A0}</th><th data-en="Establishments {A1}">Estab. {A1}</th><th data-en="Jobs {A1}">Vínculos {A1}</th><th data-en="Change">Variação</th></tr>\n{rows}    </table></div>\n'
        f'    <h3 data-en="Boatbuilding and nautical industry in SC, by CNAE subclass" style="margin-top:1.2rem">Indústria náutica de SC, por subclasse CNAE</h3>\n'
        f'    <div class="tw"><table>\n      <tr><th>CNAE</th><th data-en="Activity">Atividade</th><th data-en="Jobs {A0}">Vínculos {A0}</th><th data-en="Jobs {A1}">Vínculos {A1}</th><th data-en="Establishments {A1}">Estab. {A1}</th></tr>\n{cn}    </table></div>\n'
        f'    <h3 data-en="Boatbuilding and nautical industry in SC, by municipality" style="margin-top:1.2rem">Indústria náutica de SC, por município</h3>\n'
        f'    <div class="tw"><table>\n      <tr><th data-en="Municipality">Município</th><th data-en="Jobs {A0}">Vínculos {A0}</th><th data-en="Jobs {A1}">Vínculos {A1}</th><th data-en="Establishments {A1}">Estab. {A1}</th><th data-en="Change">Variação</th></tr>\n{mun}    </table></div>\n'
        f'    <div class="src" data-en="Source: RAIS {A0} and {A1}, public establishment microdata (PDET/MTE), read and tabulated by ACATMAR. Open files in data/rais.">Fonte: RAIS {A0} e {A1}, microdados públicos por estabelecimento (PDET/MTE), lidos e tabulados pela ACATMAR. Arquivos abertos em <a href="data/rais/nautica_municipio_sc_{A1}.csv">data/rais</a>.</div>\n')
put('sc', html)
sc1 = r1['construcao_esporte_lazer_por_uf'].get('SC', {'vinculos': 0, 'estab': 0})
tot_br = sum(d['vinculos'] for d in r1['construcao_esporte_lazer_por_uf'].values())
put('br', f'      <tr><td data-en="Formal jobs in sport and leisure boatbuilding (CNAE 3012-1/00), by state">Empregos formais na construção de embarcações de esporte e lazer (CNAE 3012-1/00), por estado</td><td class="v">SC {n(sc1["vinculos"])} de {n(tot_br)}</td><td data-en="{A1}: ' + ' · '.join(f"{u} {n(d['vinculos'])}" for u, d in list(r1['construcao_esporte_lazer_por_uf'].items())[:6]) + f' · RAIS {A1}, ACATMAR extraction">{A1}: ' + ' · '.join(f"{u} {n(d['vinculos'])}" for u, d in list(r1['construcao_esporte_lazer_por_uf'].items())[:6]) + f' · RAIS {A1}, extração ACATMAR</td></tr>\n')
defs = '; '.join(f"{c[:4]}-{c[4]}/{c[5:]} {d['descricao']}" for c, d in R['definicao'].items())
put('nota', f'<li data-en="Jobs: RAIS establishment microdata, {len(R["definicao"])} CNAE subclasses grouped by ACATMAR into nautical industry, nautical trade and services, shipbuilding, ports and navigation, fishing and aquaculture; only establishments with at least one active contract on Dec 31 count, so companies without employees do not appear.">Empregos: microdados da RAIS por estabelecimento, {len(R["definicao"])} subclasses CNAE agrupadas pela ACATMAR em indústria náutica, comércio e serviços náuticos, indústria naval, portos e navegação, pesca e aquicultura; só contam estabelecimentos com pelo menos um vínculo ativo em 31 de dezembro, por isso empresas sem empregados não aparecem.</li>')
for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, flags=re.S):
    json.loads(x)
open(P, 'w', encoding='utf-8').write(t)
print('ok', A0, A1, 'total cadeia SC', tot0, tot1)
