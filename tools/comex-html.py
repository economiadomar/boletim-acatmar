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


# ---------- serie anual (SC) ----------
rows = ''
for s in serie:
    if not s['exp_br']:
        continue
    rk = ' · '.join(f"{r['uf']} {usd(r['fob'])}" for r in s['ranking_exp'][:3])
    rows += f'      <tr><td>{s["ano"]}</td><td class="v">{usd(s["exp_sc"])}</td><td class="v">{usd(s["exp_br"])}</td><td class="v">{str(s["part_sc"]).replace(".", ",")}%</td><td>{rk}</td></tr>\n'
serie_html = ('\n    <div class="tw"><table>\n      <tr><th data-en="Year">Ano</th><th data-en="SC exports">Exportações de SC</th><th data-en="Brazil exports">Exportações do Brasil</th><th data-en="SC share">Participação de SC</th><th data-en="Top 3 states">Três maiores exportadores</th></tr>\n'
              + rows + f'    </table></div>\n    <div class="src" data-en="Source: Comex Stat/MDIC, heading 8903 (yachts and other vessels for pleasure or sports), US$ FOB. Extracted by ACATMAR from the ministry\'s public API on {GER}; {Y} covers January to {MES_EN[M]}.">Fonte: Comex Stat/MDIC, posição 8903 (iates e outros barcos e embarcações de recreio ou esporte), US$ FOB. Extração ACATMAR da API pública do ministério em {GER}; {Y} cobre janeiro a {MES[M]}.</div>\n')
# municipios SC e paises e NCM do ultimo ano completo
YC = Y - 1
msc = B['municipios_sc'].get(str(YC), [])
psc = B['paises_sc'].get(str(YC), [])
nsc = sorted(B['ncm_sc'].get(str(YC), []), key=lambda x: -x['fob'])
tot_units = sum(x['unidades'] for x in nsc)
ncm_rows = ''.join(f'      <tr><td>{x["ncm"][:4]}.{x["ncm"][4:6]}.{x["ncm"][6:]}</td><td>{x["desc"]}</td><td class="v">{x["unidades"]}</td><td class="v">{usd(x["fob"])}</td></tr>\n' for x in nsc if x['fob'] > 0)
serie_html += (f'    <h3 data-en="{YC}: what Santa Catarina exported, by product code (NCM)" style="margin-top:1.2rem">{YC}: o que Santa Catarina exportou, por código de produto (NCM)</h3>\n'
               f'    <div class="tw"><table>\n      <tr><th>NCM</th><th data-en="Description">Descrição</th><th data-en="Units">Unidades</th><th>US$ FOB</th></tr>\n{ncm_rows}'
               f'      <tr><td></td><td><b data-en="Total">Total</b></td><td class="v"><b>{tot_units}</b></td><td class="v"><b>{usd(sum(x["fob"] for x in nsc))}</b></td></tr>\n    </table></div>\n'
               f'    <div class="src" data-en="Units are the statistical quantity reported to Comex Stat (number of boats). Extracted by ACATMAR.">Unidades são a quantidade estatística informada ao Comex Stat (número de barcos). Extração ACATMAR.</div>\n'
               f'    <div class="tw" style="margin-top:1rem"><table>\n      <tr><th data-en="{YC}, by municipality">{YC}, por município de SC</th><th>US$ FOB</th><th data-en="{YC}, by destination">{YC}, por destino</th><th>US$ FOB</th></tr>\n')
for i in range(max(len(msc[:6]), len(psc[:6]))):
    a = msc[i] if i < len(msc[:6]) else None
    b = psc[i] if i < len(psc[:6]) else None
    serie_html += f'      <tr><td>{a["municipio"].replace(" - SC", "") if a else ""}</td><td class="v">{usd(a["fob"]) if a else ""}</td><td>{b["pais"] if b else ""}</td><td class="v">{usd(b["fob"]) + (" (" + str(b["unidades"]) + " un)" if b and b["unidades"] else "") if b else ""}</td></tr>\n'
serie_html += '    </table></div>\n'
put('serie', serie_html)

# ---------- semestre / acumulado do ano corrente ----------
h = sem['h1']; ac = sem['acumulado_ate_mes']
h1_html = (f'\n    <h3 data-en="{Y} so far: January to {MES_EN[M]}, against the same months of {Y-1}" style="margin-top:1.2rem">{Y} até agora: janeiro a {MES[M]}, contra os mesmos meses de {Y-1}</h3>\n'
           f'    <div class="tw"><table>\n      <tr><th data-en="Indicator">Indicador</th><th>{Y-1}</th><th>{Y}</th><th data-en="Change">Variação</th></tr>\n'
           f'      <tr><td data-en="Brazil, boat exports (8903), Jan to {MES_EN[M]}">Brasil, exportações de embarcações (8903), jan a {MES[M][:3]}</td><td class="v">{usd(ac["br"][0])}</td><td class="v">{usd(ac["br"][1])}</td><td class="v">{fmtpct(pct(ac["br"][1], ac["br"][0]))}</td></tr>\n'
           f'      <tr><td data-en="Santa Catarina, Jan to {MES_EN[M]}">Santa Catarina, jan a {MES[M][:3]}</td><td class="v">{usd(ac["sc"][0])}</td><td class="v">{usd(ac["sc"][1])}</td><td class="v">{fmtpct(pct(ac["sc"][1], ac["sc"][0]))}</td></tr>\n'
           f'      <tr><td data-en="Brazil, first half">Brasil, 1º semestre</td><td class="v">{usd(h["br"][0])}</td><td class="v">{usd(h["br"][1])}</td><td class="v">{fmtpct(pct(h["br"][1], h["br"][0]))}</td></tr>\n'
           f'      <tr><td data-en="Santa Catarina, first half">Santa Catarina, 1º semestre</td><td class="v">{usd(h["sc"][0])}</td><td class="v">{usd(h["sc"][1])}</td><td class="v">{fmtpct(pct(h["sc"][1], h["sc"][0]))}</td></tr>\n'
           f'      <tr><td data-en="Itajaí, first half">Itajaí, 1º semestre</td><td class="v">{usd(h["itajai"][0])}</td><td class="v">{usd(h["itajai"][1])}</td><td class="v">{fmtpct(pct(h["itajai"][1], h["itajai"][0]))}</td></tr>\n'
           f'      <tr><td data-en="Palhoça, first half">Palhoça, 1º semestre</td><td class="v">{usd(h["palhoca"][0])}</td><td class="v">{usd(h["palhoca"][1])}</td><td class="v">{fmtpct(pct(h["palhoca"][1], h["palhoca"][0]))}</td></tr>\n'
           f'    </table></div>\n    <div class="src" data-en="Source: Comex Stat/MDIC, monthly data, heading 8903, US$ FOB. Extracted by ACATMAR on {GER}.">Fonte: Comex Stat/MDIC, dados mensais, posição 8903, US$ FOB. Extração ACATMAR em {GER}.</div>\n')
put('h1', h1_html)

# tile e guia de Itajai (1o semestre)
it0, it1 = h['itajai']
v = pct(it1, it0)
t, n = re.subn(r'<div class="tile" id="tile-itajai"><div class="n">[^<]*</div><div class="l"[^>]*>[^<]*</div>(?:<div class="s"[^>]*>[^<]*</div>)?</div>',
               f'<div class="tile" id="tile-itajai"><div class="n">{usd(it1)}</div><div class="l" data-en="exported by Itajaí in boats in the first half of {Y} ({fmtpct(v)}), national leader">exportados por Itajaí em embarcações no 1º semestre de {Y} ({fmtpct(v)}), líder nacional</div></div>', t, count=1)
print('  tile itajai:', n)
t, n = re.subn(r'<li data-en="<b>Itajaí is the country\'s top boat-exporting city</b>[^"]*"><b>Itajaí é a cidade que mais exporta barcos no país</b>[^<]*<a href="#comex">ver &darr;</a></li>',
               f'<li data-en="<b>Itajaí is the country\'s top boat-exporting city</b>: {usd_en(it1)} in the first half of {Y}, {fmtpct(v)}. <a href=&quot;#comex&quot;>see &darr;</a>"><b>Itajaí é a cidade que mais exporta barcos no país</b>: {usd(it1).replace(" mi", " milhões")} no 1º semestre de {Y}, {fmtpct(v)}. <a href="#comex">ver &darr;</a></li>', t, count=1)
print('  guia itajai:', n)

# ---------- pesca (SC), serie ----------
ps = F['serie_anual']
pr = ''
for s in ps[-6:]:
    if not s['exp_br']:
        continue
    rk = ' · '.join(f"{r['uf']} {usd(r['fob'])}" for r in s['ranking_exp'][:3])
    pr += f'      <tr><td>{s["ano"]}</td><td class="v">{usd(s["exp_sc"])}</td><td class="v">{str(s["part_sc"]).replace(".", ",")}%</td><td class="v">{usd(s["imp_sc"])}</td><td>{rk}</td></tr>\n'
pmun = F['municipios_sc'].get(str(YC), [])[:4]
pesca_html = ('<tr><td colspan="3"><b data-en="Foreign trade in fish and seafood (chapter 03 plus headings 1604 and 1605)">Comércio exterior de pescado (capítulo 03 mais posições 1604 e 1605)</b></td></tr>\n'
              '      <tr><td colspan="3"><div class="tw"><table>\n      <tr><th data-en="Year">Ano</th><th data-en="SC exports">Exportações de SC</th><th data-en="SC share of Brazil">Participação no Brasil</th><th data-en="SC imports">Importações de SC</th><th data-en="Top 3 exporting states">Três maiores exportadores</th></tr>\n' + pr + '    </table></div></td></tr>\n'
              + f'      <tr><td data-en="{YC}, SC seafood exports by municipality">{YC}, exportações de pescado de SC por município</td><td class="v">{usd(pmun[0]["fob"]) if pmun else "-"}</td><td>' + ' · '.join(f'{x["municipio"].replace(" - SC", "")} {usd(x["fob"])}' for x in pmun) + '</td></tr>')
put('pesca', pesca_html)

# ---------- cards por UF ----------
for key, uf in [('sp', 'SP'), ('rj', 'RJ'), ('sc', 'SC'), ('pr', 'PR'), ('rs', 'RS'), ('pe', 'PE'), ('ba', 'BA'), ('df', 'DF'), ('am', 'AM')]:
    v_prev = uf_val(uf, YC); r_prev, n_uf = uf_rank(uf, YC)
    v_cur = uf_val(uf, Y)
    v_imp = uf_val(uf, YC, 'import')
    muns = mun_of_uf(uf, YC)
    ordinal = f'{r_prev}º' if r_prev else 'sem exportações'
    ordinal_en = (f'{r_prev}th' if r_prev not in (1, 2, 3) else {1: '1st', 2: '2nd', 3: '3rd'}[r_prev]) if r_prev else 'no exports'
    mtxt = (' · ' + ' · '.join(f'{m["municipio"].replace(" - " + uf, "")} {usd(m["fob"])}' for m in muns)) if muns else ''
    html = (f'<br><span data-en="Boat exports (Comex Stat, 8903): {usd_en(v_prev)} in {YC}, {ordinal_en} among the states{mtxt}; {usd_en(v_cur)} from January to {MES_EN[M]} {Y}. Imports in {YC}: {usd_en(v_imp)}. ACATMAR extraction.">'
            f'Exportações de embarcações (Comex Stat, 8903): <b>{usd(v_prev)}</b> em {YC}, {ordinal} entre os estados{mtxt}; {usd(v_cur)} de janeiro a {MES[M]} de {Y}. Importações em {YC}: {usd(v_imp)}. Extração ACATMAR.</span>')
    put(key, html)

# ---------- FAQ cidade lider ----------
t, n = re.subn(r'Itajaí \(SC\): US\$ [^<"]*? no 1º semestre de \d{4}, alta de \d+%, líder nacional\.',
               f'Itajaí (SC): {usd(it1).replace(" mi", " milhões")} no 1º semestre de {Y}, {"alta" if (v or 0) >= 0 else "queda"} de {abs(v or 0)}%, líder nacional.', t)
print('  faq itajai pt:', n)
t, n = re.subn(r'Itajaí \(SC\): US\$ [^<"]*? in H1 \d{4}, up \d+%, national leader\.',
               f'Itajaí (SC): {usd_en(it1)} in H1 {Y}, {"up" if (v or 0) >= 0 else "down"} {abs(v or 0)}%, national leader.', t)
print('  faq itajai en:', n)
for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, flags=re.S):
    json.loads(x)
open(P, 'w', encoding='utf-8').write(t)
print('ok')
