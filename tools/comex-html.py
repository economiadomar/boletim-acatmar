#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Injeta os dados de data/comex/resumo.json em numeros.html, entre marcadores
<!-- comex:X --> ... <!-- /comex:X -->. Rodar depois de tools/comex.py.
Marcadores: serie, h1, pesca, sp, rj, sc, pr, rs, pe, ba, df, am. Também atualiza o tile
de Itajaí (#tile-itajai), o item 2 do guia e a FAQ da cidade líder.
"""
import json, re, os, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'numeros.html')
R = json.load(open(os.path.join(ROOT, 'data', 'comex', 'resumo.json'), encoding='utf-8'))
t = open(P, encoding='utf-8').read()
B = R['embarcacoes_8903']; F = R['pescado_cap03_1604_1605']
serie = B['serie_anual']; sem = B['semestre']
Y = sem['ano']; M = sem['ate_mes']
MES = ['', 'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
MES_EN = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
GER = datetime.date.fromisoformat(R['gerado_em']).strftime('%d/%m/%Y')
UFN = {'SC': 'Santa Catarina', 'SP': 'São Paulo', 'RJ': 'Rio de Janeiro', 'PR': 'Paraná', 'RS': 'Rio Grande do Sul', 'PE': 'Pernambuco', 'BA': 'Bahia', 'DF': 'Distrito Federal', 'AM': 'Amazonas', 'PA': 'Pará', 'MG': 'Minas Gerais', 'ES': 'Espírito Santo', 'GO': 'Goiás', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul', 'RR': 'Roraima', 'AP': 'Amapá', 'RO': 'Rondônia', 'CE': 'Ceará', 'RN': 'Rio Grande do Norte', 'PB': 'Paraíba', 'AL': 'Alagoas', 'SE': 'Sergipe', 'MA': 'Maranhão', 'PI': 'Piauí', 'TO': 'Tocantins', 'AC': 'Acre'}


def usd(v):
    if v is None:
        return '-'
    if v >= 1e6:
        return 'US$ ' + f"{v/1e6:.1f}".replace('.', ',') + ' mi'
    if v >= 1e3:
        return 'US$ ' + f"{v/1e3:.0f}" + ' mil'
    return 'US$ ' + str(v)


def usd_en(v):
    if v is None:
        return '-'
    if v >= 1e6:
        return f'US$ {v/1e6:.1f} million'
    if v >= 1e3:
        return f'US$ {v/1e3:.0f} thousand'
    return f'US$ {v}'


def pct(a, b):
    return None if not b else round(100 * (a - b) / b)


def fmtpct(x):
    return '-' if x is None else ('+' if x > 0 else '') + str(x) + '%'


def put(key, html):
    global t
    pat = r'<!-- comex:%s -->.*?<!-- /comex:%s -->' % (key, key)
    t, n = re.subn(pat, '<!-- comex:%s -->%s<!-- /comex:%s -->' % (key, html, key), t, count=1, flags=re.S)
    print(f"  {key}: {n}")


def rank_of(uf, year):
    s = next((x for x in serie if x['ano'] == year), None)
    if not s:
        return None
    for i, r in enumerate(s['ranking_exp'], 1):
        if r['uf'] == uf:
            return i
    return None


def uf_val(uf, year, flow='export'):
    # le do csv por UF (mais completo que o ranking top-6)
    import csv
    path = os.path.join(ROOT, 'data', 'comex', 'embarcacoes_uf.csv')
    s = 0
    for r in csv.DictReader(open(path, encoding='utf-8')):
        if r['uf'] == uf and int(r['year']) == year and r['flow'] == flow:
            s += int(float(r['metricFOB'] or 0))
    return s


def uf_rank(uf, year):
    import csv
    path = os.path.join(ROOT, 'data', 'comex', 'embarcacoes_uf.csv')
    tot = {}
    for r in csv.DictReader(open(path, encoding='utf-8')):
        if int(r['year']) == year and r['flow'] == 'export' and r['uf'] and r['uf'] in UFN:
            tot[r['uf']] = tot.get(r['uf'], 0) + int(float(r['metricFOB'] or 0))
    order = sorted(tot.items(), key=lambda x: -x[1])
    for i, (u, v) in enumerate(order, 1):
        if u == uf:
            return i, len(order)
    return None, len(order)


def mun_of_uf(uf, year, n=3):
    lst = B['municipios_top_brasil'].get(str(year)) or B['municipios_top_brasil'].get(year) or []
    return [x for x in lst if x['municipio'].endswith('- ' + uf)][:n]


# ---------- serie anual (SC), 2014 em diante ----------
rows = ''
for s in serie:
    if s['ano'] < 2014 or not s['exp_br']:
        continue
    rows += f'      <tr><td>{s["ano"]}</td><td class="v">{usd(s["exp_sc"])}</td><td class="v">{usd(s["exp_br"])}</td><td class="v">{str(s["part_sc"]).replace(".", ",")}%</td></tr>\n'
serie_html = ('\n    <div class="tw"><table>\n      <tr><th data-en="Year">Ano</th><th data-en="Santa Catarina">Santa Catarina</th><th data-en="Brazil">Brasil</th><th data-en="SC share">Participação de SC</th></tr>\n' + rows + '    </table></div>\n')
put('serie', serie_html)

# ---------- 1o semestre (como na materia da ACATMAR) ----------
h = sem['h1']
it0, it1 = h['itajai']; pa0, pa1 = h['palhoca']
h1_html = (f'\n    <h3 data-en="First half of {Y} against the first half of {Y-1}" style="margin-top:1.2rem">Primeiro semestre de {Y} contra o primeiro semestre de {Y-1}</h3>\n'
           f'    <div class="tw"><table>\n      <tr><th></th><th>{Y-1}</th><th>{Y}</th><th data-en="Change">Variação</th></tr>\n'
           f'      <tr><td data-en="Brazil">Brasil</td><td class="v">{usd(h["br"][0])}</td><td class="v">{usd(h["br"][1])}</td><td class="v">{fmtpct(pct(h["br"][1], h["br"][0]))}</td></tr>\n'
           f'      <tr><td data-en="Santa Catarina">Santa Catarina</td><td class="v">{usd(h["sc"][0])}</td><td class="v">{usd(h["sc"][1])}</td><td class="v">{fmtpct(pct(h["sc"][1], h["sc"][0]))}</td></tr>\n'
           f'      <tr><td>Itajaí</td><td class="v">{usd(it0)}</td><td class="v">{usd(it1)}</td><td class="v">{fmtpct(pct(it1, it0))}</td></tr>\n'
           f'      <tr><td>Palhoça</td><td class="v">{usd(pa0)}</td><td class="v">{usd(pa1)}</td><td class="v">{fmtpct(pct(pa1, pa0))}</td></tr>\n    </table></div>\n')
put('h1', h1_html)
v = pct(it1, it0)
t, n = re.subn(r'<div class="tile" id="tile-itajai"><div class="n">[^<]*</div><div class="l"[^>]*>[^<]*</div>(?:<div class="s"[^>]*>[^<]*</div>)?</div>',
               f'<div class="tile" id="tile-itajai"><div class="n">{usd(it1)}</div><div class="l" data-en="exported by Itajaí in boats in the first half of {Y} ({fmtpct(v)}), national leader">exportados por Itajaí em embarcações no 1º semestre de {Y} ({fmtpct(v)}), líder nacional</div></div>', t, count=1)
print('  tile itajai:', n)
t, n = re.subn(r'<li data-en="<b>Itajaí is the country\'s top boat-exporting city</b>[^"]*"><b>Itajaí é a cidade que mais exporta barcos no país</b>[^<]*<a href="#comex">ver &darr;</a></li>',
               f'<li data-en="<b>Itajaí is the country\'s top boat-exporting city</b>: {usd_en(it1)} in the first half of {Y}, {fmtpct(v)}. <a href=&quot;#comex&quot;>see &darr;</a>"><b>Itajaí é a cidade que mais exporta barcos no país</b>: {usd(it1).replace(" mi", " milhões")} no 1º semestre de {Y}, {fmtpct(v)}. <a href="#comex">ver &darr;</a></li>', t, count=1)
print('  guia itajai:', n)

put('pesca', '')

# ---------- cards por UF ----------
for key, uf in [('sp', 'SP'), ('rj', 'RJ'), ('sc', 'SC'), ('pr', 'PR'), ('rs', 'RS'), ('pe', 'PE'), ('ba', 'BA'), ('df', 'DF'), ('am', 'AM')]:
    v_prev = uf_val(uf, YC); r_prev, n_uf = uf_rank(uf, YC)
    v_cur = uf_val(uf, Y)
    v_imp = uf_val(uf, YC, 'import')
    muns = []
    ordinal = f'{r_prev}º' if r_prev else 'sem exportações'
    ordinal_en = (f'{r_prev}th' if r_prev not in (1, 2, 3) else {1: '1st', 2: '2nd', 3: '3rd'}[r_prev]) if r_prev else 'no exports'
    mtxt = (' · ' + ' · '.join(f'{m["municipio"].replace(" - " + uf, "")} {usd(m["fob"])}' for m in muns)) if muns else ''
    html = (f'<br><span data-en="Boat exports (Comex Stat, 8903): {usd_en(v_prev)} in {YC}, {ordinal_en} among the states{mtxt}; {usd_en(v_cur)} from January to {MES_EN[M]} {Y}. Imports in {YC}: {usd_en(v_imp)}. ACATMAR extraction.">'
            f'Exportações de embarcações (Comex Stat, 8903): <b>{usd(v_prev)}</b> em {YC}, {ordinal} entre os estados{mtxt}; {usd(v_cur)} de janeiro a {MES[M]} de {Y}. Importações em {YC}: {usd(v_imp)}. Extração ACATMAR.</span>')
    put(key, html)

# ---------- FAQ cidade lider ----------
t, n = re.subn(r'Itajaí \(SC\): US\$ [^<"]*? (?:no 1º semestre|de janeiro a \w+) de \d{4}(?:, (?:alta|queda) de \d+%)?, líder nacional\.',
               f'Itajaí (SC): {usd(it1).replace(" mi", " milhões")} no 1º semestre de {Y}, alta de {abs(v or 0)}%, líder nacional.', t)
print('  faq itajai pt:', n)
t, n = re.subn(r'Itajaí \(SC\): US\$ [^<"]*? (?:in H1|from January to \w+) \d{4}(?:, (?:up|down) \d+%)?, national leader\.',
               f'Itajaí (SC): {usd_en(it1)} in H1 {Y}, up {abs(v or 0)}%, national leader.', t)
print('  faq itajai en:', n)
for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, flags=re.S):
    json.loads(x)
open(P, 'w', encoding='utf-8').write(t)
print('ok')
