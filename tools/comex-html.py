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
YC = Y - 1
tot_sc = next((s['exp_sc'] for s in serie if s['ano'] == YC), 0)
def top(lst, key, tot, minimo=1_000_000, frac=0.05, n=5):
    return [x for x in sorted(lst, key=lambda x: -x['fob']) if x['fob'] >= minimo or (tot and x['fob'] >= frac * tot)][:n]
msc = top(B['municipios_sc'].get(str(YC), []), 'municipio', tot_sc)
psc = top(B['paises_sc'].get(str(YC), []), 'pais', tot_sc)
# NCM agrupado em cinco linhas
nsc = B['ncm_sc'].get(str(YC), [])
GRUPOS = [('Lanchas de 7,5 a 24 m', 'Motorboats 7.5 to 24 m', ['89033200']), ('Lanchas e iates acima de 24 m', 'Motorboats and yachts over 24 m', ['89033300']), ('Lanchas até 7,5 m', 'Motorboats up to 7.5 m', ['89033100']), ('Veleiros', 'Sailboats', ['89039100', '89032100', '89032200', '89032300']), ('Infláveis', 'Inflatables', ['89031000', '89031100', '89031200', '89031900'])]
usados = set(); grows = ''
for pt, en, codes in GRUPOS:
    v = sum(x['fob'] for x in nsc if x['ncm'] in codes); u = sum(x['unidades'] for x in nsc if x['ncm'] in codes); usados |= set(codes)
    if v:
        grows += f'      <tr><td data-en="{en}">{pt}</td><td class="v">{u}</td><td class="v">{usd(v)}</td></tr>\n'
v = sum(x['fob'] for x in nsc if x['ncm'] not in usados); u = sum(x['unidades'] for x in nsc if x['ncm'] not in usados)
if v:
    grows += f'      <tr><td data-en="Other recreational and sport boats">Outras embarcações de recreio e esporte</td><td class="v">{u}</td><td class="v">{usd(v)}</td></tr>\n'
tot_u = sum(x['unidades'] for x in nsc)
serie_html += (f'    <h3 data-en="{YC}: what Santa Catarina exported" style="margin-top:1.2rem">{YC}: o que Santa Catarina exportou</h3>\n'
               f'    <div class="tw"><table>\n      <tr><th data-en="Type">Tipo</th><th data-en="Boats">Barcos</th><th>US$ FOB</th></tr>\n{grows}'
               f'      <tr><td><b data-en="Total">Total</b></td><td class="v"><b>{tot_u}</b></td><td class="v"><b>{usd(tot_sc)}</b></td></tr>\n    </table></div>\n')
if msc:
    serie_html += f'    <p class="mini" data-en="{YC}, by municipality: ' + ' · '.join(f"{x['municipio'].replace(' - SC', '')} {usd_en(x['fob'])}" for x in msc) + f'.">Por município em {YC}: ' + ' · '.join(f"{x['municipio'].replace(' - SC', '')} {usd(x['fob'])}" for x in msc) + '.</p>\n'
if psc:
    serie_html += f'    <p class="mini" data-en="{YC}, by destination: ' + ' · '.join(f"{x['pais']} {usd_en(x['fob'])}" + (f" ({x['unidades']} boat{'s' if x['unidades'] > 1 else ''})" if x['unidades'] else '') for x in psc) + f'.">Por destino em {YC}: ' + ' · '.join(f"{x['pais']} {usd(x['fob'])}" + (f" ({x['unidades']} barco{'s' if x['unidades'] > 1 else ''})" if x['unidades'] else '') for x in psc) + '.</p>\n'
put('serie', serie_html)

# ---------- ano corrente: um periodo so (janeiro ao ultimo mes divulgado) ----------
import csv as _csv
ac = sem['acumulado_ate_mes']
def acum_mun(nome, ano):
    s = 0
    for r in _csv.DictReader(open(os.path.join(ROOT, 'data', 'comex', 'embarcacoes_mensal_municipio.csv'), encoding='utf-8')):
        if r['flow'] == 'export' and int(r['year']) == ano and int(r['monthNumber']) <= M and r['municipio'] == nome and r['uf'] == 'SC':
            s += int(float(r['metricFOB'] or 0))
    return s
it0, it1 = acum_mun('Itajaí', Y - 1), acum_mun('Itajaí', Y)
pa0, pa1 = acum_mun('Palhoça', Y - 1), acum_mun('Palhoça', Y)
h1_html = (f'\n    <h3 data-en="{Y}, January to {MES_EN[M]}, against the same months of {Y-1}" style="margin-top:1.2rem">{Y}, janeiro a {MES[M]}, contra os mesmos meses de {Y-1}</h3>\n'
           f'    <div class="tw"><table>\n      <tr><th></th><th>{Y-1}</th><th>{Y}</th><th data-en="Change">Variação</th></tr>\n'
           f'      <tr><td data-en="Brazil">Brasil</td><td class="v">{usd(ac["br"][0])}</td><td class="v">{usd(ac["br"][1])}</td><td class="v">{fmtpct(pct(ac["br"][1], ac["br"][0]))}</td></tr>\n'
           f'      <tr><td data-en="Santa Catarina">Santa Catarina</td><td class="v">{usd(ac["sc"][0])}</td><td class="v">{usd(ac["sc"][1])}</td><td class="v">{fmtpct(pct(ac["sc"][1], ac["sc"][0]))}</td></tr>\n'
           f'      <tr><td>Itajaí</td><td class="v">{usd(it0)}</td><td class="v">{usd(it1)}</td><td class="v">{fmtpct(pct(it1, it0))}</td></tr>\n'
           f'      <tr><td>Palhoça</td><td class="v">{usd(pa0)}</td><td class="v">{usd(pa1)}</td><td class="v">{fmtpct(pct(pa1, pa0))}</td></tr>\n    </table></div>\n')
put('h1', h1_html)
# tile e guia de Itajai: acumulado do ano
v = pct(it1, it0)
t, n = re.subn(r'<div class="tile" id="tile-itajai"><div class="n">[^<]*</div><div class="l"[^>]*>[^<]*</div>(?:<div class="s"[^>]*>[^<]*</div>)?</div>',
               f'<div class="tile" id="tile-itajai"><div class="n">{usd(it1)}</div><div class="l" data-en="exported by Itajaí in boats from January to {MES_EN[M]} {Y}, national leader">exportados por Itajaí em embarcações de janeiro a {MES[M]} de {Y}, líder nacional</div></div>', t, count=1)
print('  tile itajai:', n)
t, n = re.subn(r'<li data-en="<b>Itajaí is the country\'s top boat-exporting city</b>[^"]*"><b>Itajaí é a cidade que mais exporta barcos no país</b>[^<]*<a href="#comex">ver &darr;</a></li>',
               f'<li data-en="<b>Itajaí is the country\'s top boat-exporting city</b>: {usd_en(it1)} from January to {MES_EN[M]} {Y}. <a href=&quot;#comex&quot;>see &darr;</a>"><b>Itajaí é a cidade que mais exporta barcos no país</b>: {usd(it1).replace(" mi", " milhões")} de janeiro a {MES[M]} de {Y}. <a href="#comex">ver &darr;</a></li>', t, count=1)
print('  guia itajai:', n)

# ---------- pesca (SC): tabela propria ----------
ps = F['serie_anual']
pr = ''
for s in ps[-5:]:
    if not s['exp_br']:
        continue
    pr += f'      <tr><td>{s["ano"]}</td><td class="v">{usd(s["exp_sc"])}</td><td class="v">{str(s["part_sc"]).replace(".", ",")}%</td><td class="v">{usd(s["imp_sc"])}</td></tr>\n'
pmun = top(F['municipios_sc'].get(str(YC), []), 'municipio', sum(x['fob'] for x in F['municipios_sc'].get(str(YC), [])), n=3)
pesca_html = (f'\n    <h3 data-en="Foreign trade in fish and seafood (chapter 03 plus headings 1604 and 1605)" style="margin-top:1.2rem">Comércio exterior de pescado (capítulo 03 mais posições 1604 e 1605)</h3>\n'
              f'    <div class="tw"><table>\n      <tr><th data-en="Year">Ano</th><th data-en="SC exports">Exportações de SC</th><th data-en="Share of Brazil">Parte do Brasil</th><th data-en="SC imports">Importações de SC</th></tr>\n{pr}    </table></div>\n'
              + (f'    <p class="mini" data-en="{YC}, exports by municipality: ' + ' · '.join(f"{x['municipio'].replace(' - SC', '')} {usd_en(x['fob'])}" for x in pmun) + f'.">Exportações por município em {YC}: ' + ' · '.join(f"{x['municipio'].replace(' - SC', '')} {usd(x['fob'])}" for x in pmun) + '.</p>\n' if pmun else ''))
put('pesca', pesca_html)

# ---------- cards por UF ----------
for key, uf in [('sp', 'SP'), ('rj', 'RJ'), ('sc', 'SC'), ('pr', 'PR'), ('rs', 'RS'), ('pe', 'PE'), ('ba', 'BA'), ('df', 'DF'), ('am', 'AM')]:
    v_prev = uf_val(uf, YC); r_prev, n_uf = uf_rank(uf, YC)
    v_cur = uf_val(uf, Y)
    v_imp = uf_val(uf, YC, 'import')
    muns = [m for m in mun_of_uf(uf, YC) if m['fob'] >= 1_000_000 or (v_prev and m['fob'] >= 0.05 * v_prev)]
    ordinal = f'{r_prev}º' if r_prev else 'sem exportações'
    ordinal_en = (f'{r_prev}th' if r_prev not in (1, 2, 3) else {1: '1st', 2: '2nd', 3: '3rd'}[r_prev]) if r_prev else 'no exports'
    mtxt = (' · ' + ' · '.join(f'{m["municipio"].replace(" - " + uf, "")} {usd(m["fob"])}' for m in muns)) if muns else ''
    html = (f'<br><span data-en="Boat exports (Comex Stat, 8903): {usd_en(v_prev)} in {YC}, {ordinal_en} among the states{mtxt}; {usd_en(v_cur)} from January to {MES_EN[M]} {Y}. Imports in {YC}: {usd_en(v_imp)}. ACATMAR extraction.">'
            f'Exportações de embarcações (Comex Stat, 8903): <b>{usd(v_prev)}</b> em {YC}, {ordinal} entre os estados{mtxt}; {usd(v_cur)} de janeiro a {MES[M]} de {Y}. Importações em {YC}: {usd(v_imp)}. Extração ACATMAR.</span>')
    put(key, html)

# ---------- FAQ cidade lider ----------
t, n = re.subn(r'Itajaí \(SC\): US\$ [^<"]*? (?:no 1º semestre|de janeiro a \w+) de \d{4}(?:, (?:alta|queda) de \d+%)?, líder nacional\.',
               f'Itajaí (SC): {usd(it1).replace(" mi", " milhões")} de janeiro a {MES[M]} de {Y}, líder nacional.', t)
print('  faq itajai pt:', n)
t, n = re.subn(r'Itajaí \(SC\): US\$ [^<"]*? (?:in H1|from January to \w+) \d{4}, (?:up|down) \d+%, national leader\.',
               f'Itajaí (SC): {usd_en(it1)} from January to {MES_EN[M]} {Y}, national leader.', t)
print('  faq itajai en:', n)
for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, flags=re.S):
    json.loads(x)
open(P, 'w', encoding='utf-8').write(t)
print('ok')
