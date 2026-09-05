#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera os painéis por estado (recortes) de numeros.html entre <!-- uf:panels --> e <!-- /uf:panels -->,
a partir de: data/dpc-*.csv (frota), data/rais/resumo.json (empregos), data/comex/*.csv (exportações),
data/cnpj/resumo.json (empresas, se existir) e data/uf-destaques.json (texto).
"""
import csv, json, os, re, collections, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'numeros.html')
t = open(P, encoding='utf-8').read()
D = json.load(open(os.path.join(ROOT, 'data', 'uf-destaques.json'), encoding='utf-8'))
RAIS = json.load(open(os.path.join(ROOT, 'data', 'rais', 'resumo.json'), encoding='utf-8'))
CX = json.load(open(os.path.join(ROOT, 'data', 'comex', 'resumo.json'), encoding='utf-8'))
CNPJ = None
cp = os.path.join(ROOT, 'data', 'cnpj', 'resumo.json')
if os.path.exists(cp):
    CNPJ = json.load(open(cp, encoding='utf-8'))
ANOS = sorted(RAIS['anos']); A0, A1 = ANOS[-2], ANOS[-1]
Y = CX['embarcacoes_8903']['semestre']['ano']; M = CX['embarcacoes_8903']['semestre']['ate_mes']; YC = Y - 1
MES = ['', 'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
MES_EN = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
UFN = {'SC': 'Santa Catarina', 'SP': 'São Paulo', 'RJ': 'Rio de Janeiro', 'PR': 'Paraná', 'RS': 'Rio Grande do Sul', 'PE': 'Pernambuco', 'BA': 'Bahia', 'DF': 'Distrito Federal', 'AM': 'Amazonas', 'PA': 'Pará', 'MG': 'Minas Gerais', 'ES': 'Espírito Santo', 'GO': 'Goiás', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul', 'RR': 'Roraima', 'AP': 'Amapá', 'RO': 'Rondônia', 'CE': 'Ceará', 'RN': 'Rio Grande do Norte', 'PB': 'Paraíba', 'AL': 'Alagoas', 'SE': 'Sergipe', 'MA': 'Maranhão', 'PI': 'Piauí', 'TO': 'Tocantins', 'AC': 'Acre'}


def n(v):
    return '-' if v is None else f"{int(v):,}".replace(',', '.')


def usd(v):
    if v is None:
        return '-'
    if v >= 1e6:
        return 'US$ ' + f"{v/1e6:.1f}".replace('.', ',') + ' mi'
    if v >= 1e3:
        return 'US$ ' + f"{v/1e3:.0f}" + ' mil'
    return 'US$ ' + str(int(v))


# ---------- frota (DPC) ----------
frota = collections.defaultdict(lambda: collections.Counter())
for r in csv.reader(open(os.path.join(ROOT, 'data', 'dpc-embarcacoes-por-om-uf-tipo-arquivo-2024-09-17.csv'), encoding='utf-8-sig'), delimiter=';'):
    if len(r) < 6:
        continue
    uf = r[3].strip(); ty = r[4].strip().upper(); v = int(r[5] or 0)
    k = 'lancha' if 'LANCHA' in ty else 'moto' if 'MOTO' in ty else 'veleiro' if 'VELEIRO' in ty else 'outros'
    frota[uf][k] += v; frota[uf]['total'] += v
rank_lancha = {u: i for i, (u, c) in enumerate(sorted(frota.items(), key=lambda x: -x[1]['lancha']), 1)}

# ---------- comex ----------
exp_uf = collections.defaultdict(dict)  # uf -> ano -> fob
for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'comex', 'embarcacoes_uf.csv'), encoding='utf-8')):
    if r['flow'] == 'export' and r['uf'] in UFN:
        exp_uf[r['uf']][int(r['year'])] = exp_uf[r['uf']].get(int(r['year']), 0) + int(float(r['metricFOB'] or 0))
br_ano = collections.Counter()
for u, d in exp_uf.items():
    for y, v in d.items():
        br_ano[y] += v
def rank(uf, y):
    order = sorted(((d.get(y, 0), u) for u, d in exp_uf.items()), reverse=True)
    for i, (v, u) in enumerate(order, 1):
        if u == uf:
            return i if v > 0 else None
    return None
mun_uf = collections.defaultdict(lambda: collections.Counter())
for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'comex', 'embarcacoes_municipio.csv'), encoding='utf-8')):
    if r['flow'] == 'export' and int(r['year']) == YC:
        mun_uf[r['uf']][r['municipio']] += int(float(r['metricFOB'] or 0))
mes_uf = collections.Counter()
for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'comex', 'embarcacoes_mensal.csv'), encoding='utf-8')):
    if r['flow'] == 'export' and int(r['year']) == Y:
        mes_uf[r['uf']] += int(float(r['metricFOB'] or 0))

# ---------- rais ----------
def rais_uf(uf, ano):
    r = RAIS['anos'][ano]
    return r['industria_nautica_por_uf'].get(uf, {'estab': 0, 'vinculos': 0}), r['construcao_esporte_lazer_por_uf'].get(uf, {'estab': 0, 'vinculos': 0})


def cnpj_uf(uf):
    if not CNPJ:
        return None, None
    return CNPJ['brasil_setor_nautico_principal_por_uf'].get(uf), CNPJ['brasil_construcao_esporte_lazer_por_uf'].get(uf)


def kpi(num, l, l_en, s, s_en):
    return f'<div class="kpi"><div class="n">{num}</div><div class="l" data-en="{l_en}">{l}</div></div>'


def painel(key, cfg):
    ufs = cfg.get('ufs', [key.upper()])
    uf = ufs[0]
    nome, nome_en = cfg['nome'], cfg['nome_en']
    # frota
    fr = collections.Counter()
    for u in ufs:
        fr.update(frota[u])
    ind0, con0 = rais_uf(uf, A0); ind1, con1 = rais_uf(uf, A1)
    if len(ufs) > 1:
        for u in ufs[1:]:
            i, c = rais_uf(u, A1); ind1 = {'estab': ind1['estab'] + i['estab'], 'vinculos': ind1['vinculos'] + i['vinculos']}; con1 = {'estab': con1['estab'] + c['estab'], 'vinculos': con1['vinculos'] + c['vinculos']}
            i, c = rais_uf(u, A0); ind0 = {'estab': ind0['estab'] + i['estab'], 'vinculos': ind0['vinculos'] + i['vinculos']}; con0 = {'estab': con0['estab'] + c['estab'], 'vinculos': con0['vinculos'] + c['vinculos']}
    ex = {y: sum(exp_uf[u].get(y, 0) for u in ufs) for y in range(YC - 5, YC + 1)}
    rk = rank(uf, YC)
    ex_cur = sum(mes_uf[u] for u in ufs)
    emp, con_cnpj = cnpj_uf(uf)
    k = [kpi(n(fr['lancha']), f'lanchas registradas, {rank_lancha.get(uf, "-")}ª frota do país', f'registered motorboats, {rank_lancha.get(uf, "-")}th fleet in the country', 'Marinha do Brasil / DPC, arquivo de 17/09/2024', 'Brazilian Navy / DPC, file of Sept 17, 2024'),
         kpi(n(ind1['vinculos']), f'empregos formais na indústria náutica ({A1})', f'formal jobs in the nautical industry ({A1})', f'RAIS {A1}, extração ACATMAR', f'RAIS {A1}, ACATMAR extraction'),
         kpi(usd(ex[YC]), f'exportados em embarcações em {YC}' + (f', {rk}º do país' if rk else ', sem exportações'), f'boat exports in {YC}' + (f', {rk}th in the country' if rk else ', no exports'), 'Comex Stat / MDIC, extração ACATMAR', 'Comex Stat / MDIC, ACATMAR extraction')]
    if emp is not None:
        k.append(kpi(n(emp), 'empresas náuticas ativas (CNAE principal)', 'active nautical companies (main CNAE)', f'Receita Federal, {CNPJ["pasta"]}, extração ACATMAR', f'Federal Revenue, {CNPJ["pasta"]}, ACATMAR extraction'))
    if cfg.get('extra_kpi'):
        e = cfg['extra_kpi']; k.append(kpi(e['n'], e['l'], e['l_en'], e['s'], e['s_en']))
    kpis = '<div class="kpis">' + ''.join(k) + '</div>'
    # frota box
    fb = (f'<div class="ufbox"><h3 data-en="Registered fleet">Frota registrada</h3><table>'
          f'<tr><td data-en="Motorboats">Lanchas</td><td class="v">{n(fr["lancha"])}</td></tr>'
          f'<tr><td data-en="Personal watercraft">Motos aquáticas</td><td class="v">{n(fr["moto"])}</td></tr>'
          f'<tr><td data-en="Sailboats">Veleiros</td><td class="v">{n(fr["veleiro"])}</td></tr>'
          f'<tr><td data-en="Other types (dinghies, canoes, fishing, transport, support)">Outros tipos (botes, canoas, pesca, transporte, apoio)</td><td class="v">{n(fr["outros"])}</td></tr>'
          f'<tr><td><b data-en="Total registered">Total registrado</b></td><td class="v"><b>{n(fr["total"])}</b></td></tr></table>'
          f'<div class="src" data-en="Brazilian Navy / DPC, registry by type, file of Sept 17, 2024">Marinha do Brasil / DPC, registro por tipo, arquivo de 17/09/2024</div></div>')
    # empresas e empregos
    rows = (f'<tr><th></th><th>{A0}</th><th>{A1}</th></tr>'
            f'<tr><td data-en="Nautical industry: establishments with employees">Indústria náutica: estabelecimentos com empregados</td><td class="v">{n(ind0["estab"])}</td><td class="v">{n(ind1["estab"])}</td></tr>'
            f'<tr><td data-en="Nautical industry: formal jobs">Indústria náutica: empregos formais</td><td class="v">{n(ind0["vinculos"])}</td><td class="v">{n(ind1["vinculos"])}</td></tr>'
            f'<tr><td data-en="Sport and leisure boatbuilding: establishments">Construção de esporte e lazer: estabelecimentos</td><td class="v">{n(con0["estab"])}</td><td class="v">{n(con1["estab"])}</td></tr>'
            f'<tr><td data-en="Sport and leisure boatbuilding: formal jobs">Construção de esporte e lazer: empregos formais</td><td class="v">{n(con0["vinculos"])}</td><td class="v">{n(con1["vinculos"])}</td></tr>')
    if emp is not None:
        rows += f'<tr><td data-en="Active nautical companies, main CNAE (Federal Revenue)">Empresas náuticas ativas, CNAE principal (Receita Federal)</td><td class="v"></td><td class="v">{n(emp)}</td></tr><tr><td data-en="Active sport and leisure boatbuilders (Federal Revenue)">Construtores de esporte e lazer ativos (Receita Federal)</td><td class="v"></td><td class="v">{n(con_cnpj)}</td></tr>'
    eb = (f'<div class="ufbox"><h3 data-en="Companies and jobs">Empresas e empregos</h3><table>{rows}</table>'
          f'<div class="src" data-en="RAIS {A0} and {A1} (five nautical industry CNAEs, see methodology)' + (f'; Federal Revenue CNPJ registry, {CNPJ["pasta"]}' if emp is not None else '') + f'. ACATMAR extraction.">RAIS {A0} e {A1} (cinco CNAEs da indústria náutica, ver metodologia)' + (f'; cadastro CNPJ da Receita Federal, {CNPJ["pasta"]}' if emp is not None else '') + '. Extração ACATMAR.</div></div>')
    # exportacoes
    zeros = [str(y) for y in sorted(ex) if not ex[y]]
    xr = ''.join(f'<tr><td>{y}</td><td class="v">{usd(ex[y])}</td><td class="v">{(str(round(100*ex[y]/br_ano[y],1)).replace(".", ",") + "%") if br_ano[y] else "-"}</td><td class="v">{str(rank(uf, y)) + "º" if rank(uf, y) else "-"}</td></tr>' for y in sorted(ex) if ex[y])
    xr += f'<tr><td>{Y} (jan a {MES[M][:3]})</td><td class="v">{usd(ex_cur) if ex_cur else "-"}</td><td class="v"></td><td class="v"></td></tr>'
    if zeros:
        xr += f'<tr><td colspan="4" class="mini" data-en="No exports recorded in {", ".join(zeros)}.">Sem exportações registradas em {", ".join(zeros)}.</td></tr>'
    muns = sorted(((v, m) for m, v in mun_uf[uf].items() if v >= 1_000_000 or (ex[YC] and v >= 0.05 * ex[YC])), reverse=True)[:4]
    mtxt = ' · '.join(f'{m} {usd(v)}' for v, m in muns)
    xb = (f'<div class="ufbox"><h3 data-en="Boat exports (heading 8903)">Exportações de embarcações (posição 8903)</h3><table><tr><th data-en="Year">Ano</th><th>US$ FOB</th><th data-en="Share of Brazil">Parte do Brasil</th><th data-en="Rank">Posição</th></tr>{xr}</table>'
          + (f'<p class="mini" data-en="{YC}, by municipality: {mtxt}">{YC}, por município: {mtxt}</p>' if muns else '')
          + f'<div class="src" data-en="Comex Stat / MDIC, US$ FOB, ACATMAR extraction">Comex Stat / MDIC, US$ FOB, extração ACATMAR</div></div>')
    # destaques
    db = '<div class="ufbox"><h3 data-en="Highlights">Destaques</h3><ul class="dest">' + ''.join(f'<li><b>{a}.</b> <span data-en="{c}">{b}</span></li>' for a, b, c in cfg['destaques']) + '</ul></div>'
    sac = ''
    if cfg.get('sac'):
        sac = ('<div class="ufbox sac"><h3 data-en="SAC Náutico: the model other states can copy">SAC Náutico: o modelo que os outros estados podem copiar</h3>'
               '<p data-en="What it is: a single counter of the City of Salvador (Secretariat of the Sea) where the Navy (Port Authority), the Federal Police and the Federal Revenue serve, in one place, the foreign sailor who arrives by sea: entry into the country, immigration, temporary admission of the boat, registration and licenses. Twenty-one services for foreigners and Brazilians. Opened in October 2023.">O que é: um balcão único da Prefeitura de Salvador (Secretaria do Mar) onde Marinha (Capitania dos Portos), Polícia Federal e Receita Federal atendem, no mesmo lugar, o velejador estrangeiro que chega pelo mar: entrada no país, imigração, admissão temporária do barco, registro e licenças. São 21 serviços, para estrangeiros e brasileiros. Inaugurado em outubro de 2023.</p>'
               '<table><tr><th data-en="Milestone">Marco</th><th data-en="Result">Resultado</th></tr>'
               '<tr><td data-en="First year (Oct 2024)">Primeiro ano (out/2024)</td><td data-en="750 services, 98 foreign boats received, sailors of 31 nationalities">750 atendimentos, 98 embarcações estrangeiras recebidas, velejadores de 31 nacionalidades</td></tr>'
               '<tr><td data-en="Dec 2025">Dez/2025</td><td data-en="1,600 services, 47 nationalities">1,6 mil atendimentos, 47 nacionalidades</td></tr>'
               '<tr><td data-en="2026 (one year of the Secretariat of the Sea)">2026 (um ano da Secretaria do Mar)</td><td data-en="More than 2,000 sailors from about 50 countries served since opening">Mais de 2 mil velejadores de cerca de 50 países atendidos desde a abertura</td></tr>'
               '<tr><td data-en="Time to clear a foreign boat">Tempo para regularizar um barco estrangeiro</td><td data-en="From about 7 hours in three agencies to 3 hours in one place">De cerca de 7 horas em três órgãos para 3 horas em um só lugar</td></tr></table>'
               '<p data-en="Why it matters: every foreign boat that clears in stays for weeks or months paying marina, maintenance, provisioning and tourism, and the boat can remain in the country for up to two years. The model needs no new agency, only the three federal bodies working side by side, which any coastal state can replicate. ACATMAR has asked the City of Salvador for the number of boats received per year to complete this series.">Por que importa: cada barco estrangeiro que entra fica semanas ou meses pagando marina, manutenção, abastecimento e turismo, e pode permanecer no país por até dois anos. O modelo não exige órgão novo, só os três órgãos federais trabalhando lado a lado, e qualquer estado costeiro pode replicar. A ACATMAR pediu à Prefeitura de Salvador o número de barcos recebidos por ano para completar esta série.</p>'
               '<div class="src" data-en="City of Salvador, Secretariat of the Sea and SAC Náutico, 2024 to 2026 reports">Prefeitura de Salvador, Secretaria do Mar e SAC Náutico, balanços de 2024 a 2026</div></div>')
    more = ''
    if key == 'sc':
        more = '<p class="mini" data-en="Below: Santa Catarina in depth, section by section (Sea Economy, regions, ranking, nautical sector, fishing, foreign trade).">Abaixo, Santa Catarina em profundidade, seção por seção (Economia do Mar, regiões, ranking, setor náutico, pesca, comércio exterior).</p>'
    return (f'<section class="blk gated ufp" data-uf="{key}" id="uf-{key}">\n<div class="ufhead"><span class="eyebrow" data-en="State cut">Recorte por estado</span><h2 data-en="{nome_en}">{nome}</h2><p class="lead" data-en="{cfg["tagline_en"]}">{cfg["tagline"]}</p></div>\n{kpis}\n<div class="ufgrid">{fb}{eb}{xb}{db}{sac}</div>{more}\n</section>\n')


# ---------- painel Brasil: estados em numeros ----------
def brasil():
    rows = ''
    ordem = sorted(UFN, key=lambda u: -exp_uf[u].get(YC, 0) - frota[u]['lancha'] / 1e3)
    keys = {c.get('ufs', [k.upper()])[0]: k for k, c in D.items()}
    for u in ordem:
        if frota[u]['lancha'] < 2000 and exp_uf[u].get(YC, 0) < 100000 and u not in keys:
            continue
        i1, c1 = rais_uf(u, A1)
        emp, _ = cnpj_uf(u)
        link = f'<a href="#uf-{keys[u]}" class="uflink" data-set-uf="{keys[u]}">{UFN[u]}</a>' if u in keys else UFN[u]
        rows += f'<tr><td>{link}</td><td class="v">{n(frota[u]["lancha"])}</td><td class="v">{n(i1["vinculos"])}</td><td class="v">{n(c1["estab"])}</td>' + (f'<td class="v">{n(emp)}</td>' if CNPJ else '') + f'<td class="v">{usd(exp_uf[u].get(YC, 0)) if exp_uf[u].get(YC, 0) else "-"}</td></tr>'
    head = (f'<tr><th data-en="State">Estado</th><th data-en="Motorboats registered">Lanchas registradas</th><th data-en="Nautical industry jobs {A1}">Empregos ind. náutica {A1}</th><th data-en="Sport and leisure boatbuilders {A1}">Construtores esporte e lazer {A1}</th>' + (f'<th data-en="Active nautical companies">Empresas náuticas ativas</th>' if CNPJ else '') + f'<th data-en="Boat exports {YC}">Exportações de barcos {YC}</th></tr>')
    return (f'<section class="blk gated ufp" data-uf="br" id="uf-br">\n<div class="ufhead"><span class="eyebrow" data-en="States">Estados</span><h2 data-en="The states in numbers">Os estados em números</h2><p class="lead" data-en="Click a state to open its cut. Motorboats: Navy registry (Sept 2024). Jobs and boatbuilders: RAIS {A1}. Companies: Federal Revenue. Exports: Comex Stat {YC}. All read by ACATMAR from the primary sources.">Clique no estado para abrir o recorte dele. Lanchas: registro da Marinha (set/2024). Empregos e construtores: RAIS {A1}. Empresas: Receita Federal. Exportações: Comex Stat {YC}. Tudo lido pela ACATMAR direto das fontes primárias.</p></div>\n'
            f'<div class="tw"><table>{head}{rows}</table></div>\n</section>\n')


html = brasil() + ''.join(painel(k, c) for k, c in D.items())
t, k = re.subn(r'<!-- uf:panels -->.*?<!-- /uf:panels -->', '<!-- uf:panels -->\n' + html + '<!-- /uf:panels -->', t, count=1, flags=re.S)
print('painéis injetados:', k, '| estados:', list(D))
for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, flags=re.S):
    json.loads(x)
open(P, 'w', encoding='utf-8').write(t)
